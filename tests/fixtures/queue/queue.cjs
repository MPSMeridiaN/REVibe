const completed = new Map();
async function handle(id, effect) {
  if (completed.has(id)) return completed.get(id);
  const result = await effect();
  completed.set(id, result);
  return result;
}
module.exports = {handle};
