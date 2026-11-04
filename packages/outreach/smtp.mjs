// Server-only SMTP transport. Credentials never enter static assets or logs.
// Cloudflare's built-in TCP sockets; implicit TLS, certificate validation intact.
export class MailError extends Error {constructor(code,uncertain=false){super(code);this.code=code;this.uncertain=uncertain}}
export function mailMessage({from,to,subject,text,id,inReplyTo='',unsubscribe='',fromName='Open Practice'}){
 const address=/^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;
 if(!address.test(from)||!address.test(to)||/[\r\n]/.test(subject)||!/^[-a-zA-Z0-9]+$/.test(id))throw new MailError('invalid_message');
 // outreach v2: T2/T3/link answers thread under T1; the one-click opt-out rides in a header, never in T1's body
 if(/[\r\n<>]/.test(inReplyTo.replace(/^<|>$/g,''))||/[\r\n<>\s]/.test(unsubscribe)||/[\r\n<>"]/.test(fromName))throw new MailError('invalid_message');
 const extra=(inReplyTo?`In-Reply-To: ${inReplyTo}\r\nReferences: ${inReplyTo}\r\n`:'')+(unsubscribe?`List-Unsubscribe: <${unsubscribe}>\r\nList-Unsubscribe-Post: List-Unsubscribe=One-Click\r\n`:'');
 const utf8=new TextEncoder().encode(text),encoded=btoa(Array.from(utf8,b=>String.fromCharCode(b)).join('')).match(/.{1,76}/g)?.join('\r\n')||'';
 return `From: ${fromName} <${from}>\r\nTo: ${to}\r\nSubject: ${subject}\r\nDate: ${new Date().toUTCString()}\r\nMessage-ID: <${id}@gmail.com>\r\n${extra}MIME-Version: 1.0\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n${encoded}\r\n`;
}
export async function smtpMail(env,message=null,connector=null){
 // v2: message.box = {user,pass} picks one of the two personal boxes; default is the first
 const user=message?.box?.user||env.OUTREACH_SMTP_USER,pass=message?.box?.pass||env.OUTREACH_SMTP_PASSWORD;
 if(!user||!pass)throw new MailError('sender_not_configured');
 const connect=connector||(await import('cloudflare:sockets')).connect;
 let socket,reader,writer,buffer='',dataStarted=false,accepted=false;
 const deadline=Date.now()+24000;
 async function bounded(p){let timer;try{return await Promise.race([p,new Promise((_,reject)=>timer=setTimeout(()=>reject(new MailError('transport_timeout',dataStarted)),Math.max(1,Math.min(8000,deadline-Date.now()))))])}finally{clearTimeout(timer)}}
 async function response(){let code=null;while(true){let end=buffer.indexOf('\r\n');while(end<0){const chunk=await bounded(reader.read());if(chunk.done)throw new MailError('transport_closed',dataStarted);buffer+=new TextDecoder().decode(chunk.value);if(buffer.length>16384)throw new MailError('invalid_smtp_reply',dataStarted);end=buffer.indexOf('\r\n')}const line=buffer.slice(0,end);buffer=buffer.slice(end+2);if(!/^\d{3}[- ]/.test(line))throw new MailError('invalid_smtp_reply',dataStarted);if(code&&code!==Number(line.slice(0,3)))throw new MailError('invalid_smtp_reply',dataStarted);code=Number(line.slice(0,3));if(line[3]===' ')return code}}
 async function command(line,expected,kind='smtp_rejected'){await bounded(writer.write(new TextEncoder().encode(line+'\r\n')));if(await response()!==expected)throw new MailError(kind,dataStarted)}
 try{
  socket=connect({hostname:'smtp.gmail.com',port:465},{secureTransport:'on'});await bounded(socket.opened);reader=socket.readable.getReader();writer=socket.writable.getWriter();if(await response()!==220)throw new MailError('smtp_greeting_rejected');
  await command('EHLO open-practice.zlnew.workers.dev',250);
  await command('AUTH PLAIN '+btoa('\0'+user+'\0'+pass),235,'sender_authentication_failed');
  if(!message)return {authenticated:true,sent:false};
  const {box:_box,...msg}=message;const content=mailMessage({...msg,from:user});
  await command('MAIL FROM:<'+user+'>',250);
  await command('RCPT TO:<'+message.to+'>',250,'recipient_rejected');
  await command('DATA',354);dataStarted=true;
  await command(content+'.',250,'delivery_unknown');accepted=true;
  return {authenticated:true,sent:true,acceptedBySMTP:true,messageId:`<${message.id}@gmail.com>`,from:user};
 }catch(error){if(error instanceof MailError)throw error;throw new MailError('transport_unavailable',dataStarted&&!accepted)}finally{try{await socket?.close()}catch{}}
}
