import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = dirname(fileURLToPath(import.meta.url));
const configuredTarget = process.env.CLICKJACKING_TARGET_URL;
const configuredLanIp = (process.env.CLICKJACKING_LAN_IP ?? '').trim();
let targetUrl;
if (configuredTarget) {
  targetUrl = new URL(configuredTarget);
  if (!['http:', 'https:'].includes(targetUrl.protocol) || targetUrl.username || targetUrl.password) throw new Error('CLICKJACKING_TARGET_URL phải là URL HTTP(S) không chứa thông tin đăng nhập.');
  const localHost = ['localhost', '127.0.0.1', '[::1]'].includes(targetUrl.hostname);
  const configuredLanTarget = configuredLanIp !== '' && targetUrl.hostname === configuredLanIp && targetUrl.protocol === 'http:';
  if (!localHost && !configuredLanTarget && targetUrl.protocol !== 'https:') throw new Error('Target remote chỉ được dùng HTTPS; HTTP chỉ được phép với CLICKJACKING_LAN_IP đã cấu hình.');
} else {
  const targetPort = Number(process.env.CLICKJACKING_TARGET_PORT ?? 5173);
  if (!Number.isInteger(targetPort) || targetPort < 1 || targetPort > 65535) throw new Error('CLICKJACKING_TARGET_PORT phải là một port hợp lệ.');
  targetUrl = new URL(`http://localhost:${targetPort}/`);
}
const escapedTargetUrl = targetUrl.toString().replaceAll('&', '&amp;').replaceAll('"', '&quot;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
const page = (await readFile(join(root, 'clickjacking-attacker.html'), 'utf8'))
  .replaceAll('__VOCABUP_URL__', escapedTargetUrl);
const configuredAttackerHost = (process.env.CLICKJACKING_ATTACKER_HOST ?? '').trim().toLowerCase();

function makeServer() {
  return createServer((req, res) => {
    const host = req.headers.host?.split(':')[0];
    const isLocalHost = ['localhost', '127.0.0.1'].includes(host ?? '');
    if ((!isLocalHost && host !== configuredAttackerHost) || !['/', '/index.html'].includes(new URL(req.url ?? '/', 'http://localhost').pathname)) {
      res.writeHead(404, { 'Cache-Control': 'no-store' }).end('Not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' }).end(page);
  });
}

async function listenOnAvailablePort(port) {
  const server = makeServer();
  const bindHost = configuredLanIp || '127.0.0.1';
  const displayHost = configuredLanIp || 'localhost';
  try {
    await new Promise((resolve, reject) => {
      server.once('error', reject);
      server.listen(port, bindHost, resolve);
    });
    console.log(`Clickjacking attacker demo: http://${displayHost}:${port} (iframe target ${targetUrl.origin})`);
  } catch (error) {
    if (error?.code === 'EADDRINUSE' && port < 4190) return listenOnAvailablePort(port + 1);
    throw error;
  }
}

await listenOnAvailablePort(Number(process.env.CLICKJACKING_ATTACKER_PORT ?? 4174));
