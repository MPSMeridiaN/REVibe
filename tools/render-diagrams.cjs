// Development-only visual check; pass a path to an installed sharp module.
const fs = require('node:fs');
const path = require('node:path');
const sharp = require(process.argv[2] || 'sharp');
const root = path.resolve(__dirname, '..');
const output = path.join(root, 'dist', 'previews');
fs.mkdirSync(output, {recursive: true});
Promise.all(['journey', 'handoff'].map(name => sharp(path.join(root, 'docs', 'assets', name + '.svg'))
  .png().toFile(path.join(output, name + '.png')))).catch(error => { console.error(error); process.exitCode = 1; });
