import { writeFile } from 'node:fs/promises';

const raw = process.env.API_BASE_URL;
if (!raw) throw new Error('Set API_BASE_URL to the Render backend URL');
const url = new URL(raw);
if (!['https:', 'http:'].includes(url.protocol) || url.username || url.password) {
  throw new Error('API_BASE_URL must be an HTTP(S) URL without credentials');
}
await writeFile(new URL('./config.js', import.meta.url),
  'window.APP_CONFIG = ' + JSON.stringify({ API_BASE_URL: url.href.replace(/\/$/, '') }) + ';\n');
