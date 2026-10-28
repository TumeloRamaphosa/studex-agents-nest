// Build the StudEx Meat site into dist/ for deployment.
//
// The site's real source is ../studex-meat (a Vite + React app) whose
// outDir is `public/`. This wrapper copies that build output into dist/ so
// the deploy tool has the shape it expects: dist/index.html.
import { cp, mkdir, rm, readdir, stat } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';

const SRC = path.resolve(process.cwd(), '../studex-meat/public');
const OUT = path.resolve(process.cwd(), 'dist');

if (!existsSync(path.join(SRC, 'index.html'))) {
  console.error(`No built site at ${SRC} - run "npm run build" in ../studex-meat first.`);
  process.exit(1);
}

await rm(OUT, { recursive: true, force: true });
await mkdir(OUT, { recursive: true });
await cp(SRC, OUT, { recursive: true });

const files = await readdir(OUT, { recursive: true });
let bytes = 0;
for (const f of files) {
  const s = await stat(path.join(OUT, f)).catch(() => null);
  if (s?.isFile()) bytes += s.size;
}
console.log(`Built ${files.length} files (${(bytes / 1048576).toFixed(1)} MB) into dist/`);
