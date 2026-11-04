// IMAP over Cloudflare TCP sockets (outreach v2 reply reading). Ported from the Mechanism Audit desk (src/smtp.js + src/imap.js).
// Jacaranda Labs mail wire: TLS sockets, SMTPS 465 and plain-text MIME.
// Ported from DeskOS worker/src/mail.js (the AttestOS pattern), unchanged except: readBytes() for IMAP literals,
// HELO name, and no lanes (this Worker has exactly one Gmail box).
// Workers' connect() blocks port 25 only; SMTPS 465 and IMAPS 993 work.

const enc = new TextEncoder();
const dec = new TextDecoder();
const b64 = (u8) => { let s = ""; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode(...u8.subarray(i, i + 0x8000)); return btoa(s); };

// ---------------------------------------------------------------- wire
export class WireError extends Error {
  constructor(msg, kind = "closed") { super(msg); this.kind = kind; }
}

export function connFromStreams(readable, writable, timeoutMs = 15000, onClose) {
  const reader = readable.getReader();
  const writer = writable.getWriter();
  let buf = new Uint8Array(0);
  let done = false;
  const pull = async () => {
    if (done) throw new WireError("connection closed by server");
    let timer;
    const timeout = new Promise((_, rej) => { timer = setTimeout(() => rej(new WireError(`no response in ${timeoutMs / 1000}s`, "timeout")), timeoutMs); });
    try {
      const r = await Promise.race([reader.read(), timeout]);
      if (r.done) { done = true; throw new WireError("connection closed by server"); }
      const next = new Uint8Array(buf.length + r.value.length);
      next.set(buf); next.set(r.value, buf.length);
      buf = next;
    } finally { clearTimeout(timer); }
  };
  const conn = {
    async readLine() {
      for (;;) {
        for (let i = 0; i + 1 < buf.length; i++) {
          if (buf[i] === 13 && buf[i + 1] === 10) { const line = buf.slice(0, i); buf = buf.slice(i + 2); return line; }
        }
        if (buf.length > 1_000_000) throw new WireError("line too long");
        await pull();
      }
    },
    async readText() { return dec.decode(await conn.readLine()); },
    async readBytes(n) {
      while (buf.length < n) await pull();
      const out = buf.slice(0, n); buf = buf.slice(n); return out;
    },
    async write(data) { await writer.write(typeof data === "string" ? enc.encode(data) : data); },
    async close() {
      try { await writer.close(); } catch { /* already closed */ }
      try { reader.releaseLock(); } catch { /* ignore */ }
      if (onClose) await onClose().catch(() => {});
    },
  };
  return conn;
}

export async function openTls(hostname, port, timeoutMs = 15000) {
  const { connect } = await import("cloudflare:sockets");
  const sock = connect({ hostname, port }, { secureTransport: "on", allowHalfOpen: false });
  try {
    await Promise.race([sock.opened, new Promise((_, rej) => setTimeout(() => rej(new WireError(`connect to ${hostname}:${port} timed out`, "connect")), timeoutMs))]);
  } catch (er) {
    await sock.close().catch(() => {});
    throw er instanceof WireError ? er : new WireError(`connect to ${hostname}:${port} failed: ${er && er.message || er}`, "connect");
  }
  return connFromStreams(sock.readable, sock.writable, timeoutMs, () => sock.close());
}

export class ImapError extends Error {
  constructor(failure, msg) { super(msg); this.failure = failure; }
}
export const quote = (s) => `"${String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;

export async function readResponse(c) {
  let line = "";
  const literals = [];
  for (;;) {
    const part = dec.decode(await c.readLine());
    line += part;
    const m = part.match(/\{(\d+)\}$/);
    if (!m) return { line, literals };
    const n = Number(m[1]);
    if (n > 2_000_000) throw new ImapError("protocol", "literal too large");
    literals.push(await c.readBytes(n));
    line = `${line.slice(0, line.length - m[0].length)}\u0000${literals.length - 1}\u0000`;
  }
}

export class ImapSession {
  constructor(c) { this.c = c; this.n = 0; }
  static async open(o) {
    let c;
    try { c = await openTls(o.host || "imap.gmail.com", o.port || 993, o.timeoutMs || 15000); }
    catch (e) { throw new ImapError("connection", e && e.message || String(e)); }
    const s = new ImapSession(c);
    try {
      const g = await readResponse(c);
      if (!/^\* (OK|PREAUTH)/i.test(g.line)) throw new ImapError("protocol", `greeting: ${g.line.slice(0, 120)}`);
      await s.login(o.user, o.pass);
      return s;
    } catch (e) {
      await c.close();
      throw e instanceof ImapError ? e : new ImapError("connection", e && e.message || String(e));
    }
  }
  static over(c) { return new ImapSession(c); }
  async cmd(command) {
    const tag = `t${++this.n}`;
    await this.c.write(`${tag} ${command}\r\n`);
    const untagged = [];
    for (;;) {
      const r = await readResponse(this.c);
      if (r.line.startsWith(`${tag} `)) {
        const m = r.line.slice(tag.length + 1).match(/^(OK|NO|BAD)\s?(.*)$/i);
        return { untagged, status: (m ? m[1] : "BAD").toUpperCase(), text: m ? m[2] : r.line };
      }
      if (r.line.startsWith("+")) continue;
      untagged.push(r);
    }
  }
  async login(user, pass) {
    const r = await this.cmd(`LOGIN ${quote(user)} ${quote(pass)}`);
    if (r.status !== "OK") throw new ImapError(/AUTHENTICATIONFAILED|invalid|incorrect|password|credentials/i.test(r.text) || r.status === "NO" ? "auth" : "protocol", `LOGIN ${r.status}: ${r.text.slice(0, 160)}`);
  }
  async examine(mailbox) {
    const r = await this.cmd(`EXAMINE ${quote(mailbox)}`);
    if (r.status !== "OK") throw new ImapError("protocol", `EXAMINE ${mailbox}: ${r.text.slice(0, 160)}`);
    return r;
  }
  async uidSearch(criteria) {
    const r = await this.cmd(`UID SEARCH ${criteria}`);
    if (r.status !== "OK") throw new ImapError("protocol", `SEARCH: ${r.text.slice(0, 160)}`);
    return r.untagged.filter((u) => /^\* SEARCH/i.test(u.line)).flatMap((u) => u.line.replace(/^\* SEARCH/i, "").trim().split(/\s+/)).map(Number).filter((n) => n > 0);
  }
  /** First `bytes` of each message's text (bounce reports name the failed address near the top). */
  async fetchText(uids, bytes = 3000) {
    if (!uids.length) return [];
    const r = await this.cmd(`UID FETCH ${uids.join(",")} (UID BODY.PEEK[TEXT]<0.${bytes}>)`);
    if (r.status !== "OK") throw new ImapError("protocol", `FETCH: ${r.text.slice(0, 160)}`);
    return r.untagged.filter((u) => /^\* \d+ FETCH/i.test(u.line)).map((u) => {
      const uid = Number((u.line.match(/\bUID (\d+)/i) || [])[1] || 0);
      const lit = u.line.match(/\u0000(\d+)\u0000/);
      const q = u.line.match(/BODY\[TEXT\](?:<\d+>)?\s+"((?:[^"\\]|\\.)*)"/i);
      return { uid, text: lit ? dec.decode(u.literals[Number(lit[1])]) : (q ? q[1] : "") };
    });
  }
  async logout() {
    try { await this.cmd("LOGOUT"); } catch { /* server closes */ }
    await this.c.close();
  }
}

/** IMAP SEARCH date: 05-Nov-2026 */
export function imapDate(d) {
  const m = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  return `${String(d.getUTCDate()).padStart(2, "0")}-${m[d.getUTCMonth()]}-${d.getUTCFullYear()}`;
}
