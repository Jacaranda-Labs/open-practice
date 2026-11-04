// Reading a reply (outreach v2): the readable text of a fetched BODY[TEXT], the sender's own words only
// (never our quoted footer with its "stop"), and what they meant. Same rules as DeskOS worker/src/outreach.js.
// Owner 2026-11-04: one classifier for every business (inbound.mjs); these names stay for existing imports.
import { decodeBody, ownWords, isStop as _isStop, classifyInbound } from "./inbound.mjs";
export { decodeBody, ownWords, classifyInbound };
export const isStop = (w) => _isStop(w);
export const isAutoReply = (w) => classifyInbound({ text: w }).kind === "auto";
export function boxIndex(email, n) {
  let h = 2166136261;
  for (const ch of String(email || "").toLowerCase()) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619) >>> 0; }
  return n > 0 ? h % n : 0;
}
