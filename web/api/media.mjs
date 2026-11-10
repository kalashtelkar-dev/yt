// Logged-in only. Sends the browser to a short-lived signed link on the private Blob store (so Range/seeking works and clips never become public).
import { issueSignedToken, presignUrl } from '@vercel/blob'; import { guard } from './_lib.mjs';
let tok; // reused while the instance is warm; presigning itself is local HMAC
export default async function (req, res) {
  if (!guard(req, res)) return;
  const { k, d, f } = req.query; if (!['dhanu', 'dhshort'].includes(k) || !['clips', 'stills'].includes(d) || !/^[\w-]+\.(mp4|png|jpg)$/.test(f || '')) return res.status(404).end();
  if (!tok || tok.validUntil < Date.now() + 120e3) tok = await issueSignedToken({ pathname: '*', operations: ['get'], validUntil: Date.now() + 15 * 60e3 });
  const { presignedUrl } = await presignUrl(tok, { operation: 'get', pathname: `${k}/${d}/${f}`, access: 'private', validUntil: Date.now() + 10 * 60e3 });
  res.setHeader('cache-control', 'private, no-store'); res.redirect(302, presignedUrl);
}
