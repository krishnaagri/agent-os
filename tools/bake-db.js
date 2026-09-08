// ============================================================
// Bake script: pre-migrate n8n's SQLite DB at Docker build time.
// Boots n8n once, waits for ready, shuts down cleanly, then
// DISCOVERS where n8n actually put database.sqlite (n8n 2.x
// semantics for N8N_USER_FOLDER are not what the docs suggest),
// and prints the path for verification. The baked /home/node
// tree is the runtime data root (image ENV sets the same value).
// Usage (build time only): node tools/bake-db.js
// ============================================================
const { spawn } = require('child_process');
const fs = require('fs');

const DATA_ROOT = '/home/node';           // N8N_USER_FOLDER value (parent)
const LOG = '/tmp/n8n_boot.log';
const READY = 'Editor is now accessible';
const TIMEOUT_MS = 240000;

function sleepSync(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) {}
}

function findEntry() {
  const candidates = [
    '/usr/local/lib/node_modules/n8n/bin/n8n',
    (process.env.HOME || '/root') + '/lib/node_modules/n8n/bin/n8n',
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return { cmd: 'node', args: [c, 'start'] };
  }
  return { cmd: 'n8n', args: ['start'] };
}

// find database.sqlite anywhere under root (maxdepth 5)
function findSqlite(root, depth = 0) {
  if (depth > 5) return null;
  let entries = [];
  try { entries = fs.readdirSync(root, { withFileTypes: true }); } catch (e) { return null; }
  for (const e of entries) {
    if (e.name.startsWith('.') && e.name !== '.' && e.name !== '..') {
      const p = root + '/' + e.name;
      if (e.isDirectory()) {
        const r = findSqlite(p, depth + 1);
        if (r) return r;
      }
    }
  }
  for (const e of entries) {
    if (e.name === 'database.sqlite') return root + '/' + e.name;
  }
  return null;
}

try {
  fs.mkdirSync(DATA_ROOT, { recursive: true });
  // clean any stale n8n data so the bake is deterministic
  for (const sub of ['.n8n', '.cache']) {
    const p = DATA_ROOT + '/' + sub;
    if (fs.existsSync(p)) fs.rmSync(p, { recursive: true, force: true });
  }

  const { cmd, args } = findEntry();
  console.log('[bake] starting:', cmd, args.join(' '));

  const logFd = fs.openSync(LOG, 'w');
  const child = spawn(cmd, args, {
    detached: true,
    stdio: ['ignore', logFd, logFd],
    env: { ...process.env, N8N_USER_FOLDER: DATA_ROOT },
  });
  child.unref();

  const start = Date.now();
  let ready = false;
  while (Date.now() - start < TIMEOUT_MS) {
    let content = '';
    try { content = fs.readFileSync(LOG, 'utf8'); } catch (e) {}
    if (content.includes(READY)) { ready = true; break; }
    sleepSync(2000);
  }

  if (!ready) {
    let content = '';
    try { content = fs.readFileSync(LOG, 'utf8'); } catch (e) {}
    console.log('=== BAKE FAILED: n8n did not become ready in', TIMEOUT_MS / 1000, 's ===');
    console.log(content.slice(-4000));
    try { process.kill(child.pid, 'SIGKILL'); } catch (e) {}
    process.exit(1);
  }

  console.log('[bake] n8n ready in', Math.round((Date.now() - start) / 1000), 's — shutting down');
  try { process.kill(child.pid, 'SIGTERM'); } catch (e) {}
  sleepSync(6000);
  try { process.kill(child.pid, 'SIGKILL'); } catch (e) {}

  const dbFile = findSqlite(DATA_ROOT);
  if (!dbFile) {
    let content = '';
    try { content = fs.readFileSync(LOG, 'utf8'); } catch (e) {}
    console.log('=== BAKE FAILED: no database.sqlite found under', DATA_ROOT, '===');
    console.log(content.slice(-2000));
    process.exit(1);
  }

  const st = fs.statSync(dbFile);
  console.log('[bake] SQLite pre-migrated at build time:', dbFile, st.size, 'bytes');
  process.exit(0);
} catch (e) {
  console.log('=== BAKE CRASH ===', e && e.stack ? e.stack : e);
  process.exit(1);
}
