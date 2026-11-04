// Reading a reply (outreach v2): the readable text of a fetched BODY[TEXT], the sender's own words only
// (never our quoted footer with its "stop"), and what they meant. Same rules as DeskOS worker/src/outreach.js.
const qp = (s) => s.replace(/=\r?\n/g, "").replace(/=([0-9A-F]{2})/gi, (_, h) => String.fromCharCode(parseInt(h, 16)));
const b64 = (s) => { const t = s.replace(/[^A-Za-z0-9+/]/g, ""); try { return new TextDecoder().decode(Uint8Array.from(atob(t.slice(0, t.length - (t.length % 4))), (c) => c.charCodeAt(0))); } catch { return ""; } };
const unhtml = (s) => s.replace(/<blockquote[\s\S]*$/i, "").replace(/<br\s*\/?>/gi, "\n").replace(/<\/(p|div)>/gi, "\n").replace(/<[^>]+>/g, "").replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&#39;|&apos;/g, "'").replace(/&quot;/g, '"');

export function decodeBody(raw) {
  const s = String(raw || "");
  let chosen = null;
  for (const part of s.split(/\r?\n--[^\r\n]{6,}\r?\n/)) {
    const m = part.match(/^([\s\S]*?)\r?\n\r?\n([\s\S]*)$/);
    if (!m || !/content-type:/i.test(m[1])) continue;
    if (/text\/plain/i.test(m[1])) { chosen = { h: m[1], b: m[2] }; break; }
    if (!chosen && /text\/html/i.test(m[1])) chosen = { h: m[1], b: m[2] };
  }
  if (!chosen) {
    const t = s.trim();
    const lines = t.split(/\r?\n/);
    if (t.length >= 24 && lines.every((l, i) => /^[A-Za-z0-9+/]*={0,2}$/.test(l) && (i === lines.length - 1 || l.length >= 40))) {
      const d = b64(t);
      if (d && !/[\u0000-\u0008\uFFFD]/.test(d)) return d;
    }
    return /=\r?\n|=[0-9A-F]{2}/.test(s) ? qp(s) : s;
  }
  let b = chosen.b.split(/\r?\n--[^\r\n]{6,}--/)[0];
  if (/content-transfer-encoding:\s*base64/i.test(chosen.h)) b = b64(b);
  else if (/quoted-printable/i.test(chosen.h)) b = qp(b);
  return /text\/html/i.test(chosen.h) ? unhtml(b) : b;
}
export function ownWords(text) {
  const out = [];
  for (const line of String(text || "").split(/\r?\n/)) {
    if (/^\s*>/.test(line) || /^\s*On .{4,200}(wrote|\d{4}.*<[^>]+@)/i.test(line) || /^\s*-{2,}\s*Original Message/i.test(line)
      || /^\s*(From|Sent|De|Von):\s/i.test(line) || /^\s*-- ?$/.test(line) || /^\s*Sent from my /i.test(line)) break;
    out.push(line);
  }
  return out.join("\n").trim().slice(0, 800);
}
export const isStop = (w) => /^\W*(stop|unsubscribe|remove|no|nope)\b/i.test(w)
  || /\b(unsubscribe|remove me|take me off|not interested|no,? thanks|no thank you|stop (emailing|writing|contacting|sending)|do not (email|contact|write)|don'?t (email|contact|write))\b/i.test(w);
export const isAutoReply = (w) => /\b(out of (the )?office|automatic reply|auto-?reply|autoreply|away from (the |my )?(office|desk)|on (annual |parental |maternity )?leave|currently away|limited access to (my )?e-?mail)\b/i.test(w);

/** Stable box for an address (FNV-1a), so T2/T3 and the reply check always use the box that sent T1. */
export function boxIndex(email, n) {
  let h = 2166136261;
  for (const ch of String(email || "").toLowerCase()) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619) >>> 0; }
  return n > 0 ? h % n : 0;
}
