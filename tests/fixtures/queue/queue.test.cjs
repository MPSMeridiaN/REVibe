const {test} = require('node:test');
const assert = require('node:assert/strict');
const {handle} = require('./queue.cjs');
test('completed retry reuses result', async () => {
  let calls = 0;
  const effect = async () => ++calls;
  assert.equal(await handle('a', effect), 1);
  assert.equal(await handle('a', effect), 1);
  assert.equal(calls, 1);
});
