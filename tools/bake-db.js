// ============================================================
// Bake script: pre-migrate n8n's SQLite DB at Docker build time.
// Boots n8n once, waits for "Editor is now accessible", shuts it
// down cleanly. The resulting /home/node/.n8n/database.sqlite is
// baked into the image → runtime boots in seconds (critical on
// Render free tier: 0.1 CPU + health check kills slow first boot).
// Usage (build time only): node tools/bake-db.js
// ============================================================
const { spawn, spawnSync } = require('child_process');
const fs = require('fs');

const N8N_DIR = '/home/node/.n8n';
const DB_FILE = N8N_DIR + '/database.sqlite';
const LOG = '/tmp/n8n_boot.log';
const READY = 'Editor is now accessible';
const TIMEOUT_MS = 240000;

function sleepSync(ms) {
  const end = Date.now() + ms;
  while (Date.now() < end) { /* busy wait — fine during build */ }
}

function findEntry() {
  // Prefer the package entry directly (npm global bin symlink can be
  // missing in container installs); fall back to the command.
  const candidates = [
    '/usr/local/lib/node_modules/n8n/bin/n8n',
    process.env.HOME + '/lib/node_modules/n8n/bin/n8n',
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return { cmd: 'node', args: [c, 'start'] };
  }
  return { cmd: 'n8n', args: ['start'] };
}

try {
  fs.mkdirSync(N8N_DIR, { recursive: true });
  // clean any stale db so we know state is fresh
  for (const f of [DB_FILE, DB_FILE + '-wal', DB_FILE + '-shm']) {
    try { fs.unlinkSync(f); } catch (e) {}
  }

  const { cmd, args } = findEntry();
  console.log('[bake] starting:', cmd, args.join(' '));

  const logFd = fs.openSync(LOG, 'w');
  const child = spawn(cmd, args, {
    detached: true,
    stdio: ['ignore', logFd, logFd],
    env: { ...process.env, N8N_USER_FOLDER: N8N_DIR },
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

  let content = '';
  try { content = fs.readFileSync(LOG, 'utf8'); } catch (e) {}

  if (!ready) {
    console.log('=== BAKE FAILED: n8n did not become ready in', TIMEOUT_MS / 1000, 's ===');
    console.log(content.slice(-4000));
    try { process.kill(child.pid, 'SIGKILL'); } catch (e) {}
    process.exit(1);
  }

  console.log('[bake] n8n ready in', Math.round((Date.now() - start) / 1000), 's — shutting down');
  try { process.kill(child.pid, 'SIGTERM'); } catch (e) {}
  sleepSync(6000); // let it flush the DB
  try { process.kill(child.pid, 'SIGKILL'); } catch (e) {}

  if (!fs.existsSync(DB_FILE)) {
    console.log('=== BAKE FAILED: no sqlite file after clean shutdown ===');
    try { console.log('dir:', fs.readdirSync(N8N_DIR).join(', ')); } catch (e) {}
    try { console.log(content.slice(-2000)); } catch (e) {}
    process.exit(1);
  }

  console.log('[bake] SQLite pre-migrated at build time:', fs.statSync(DB_FILE).size, 'bytes');
  process.exit(0);
} catch (e) {
  console.log('=== BAKE CRASH ===', e && e.stack ? e.stack : e);
  process.exit(1);
}
