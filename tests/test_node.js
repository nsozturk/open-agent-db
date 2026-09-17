const assert = require('assert');
const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.resolve(__dirname, '..');
const catalogPath = path.join(ROOT_DIR, 'web', 'data', 'catalog_index.json');
const statsPath = path.join(ROOT_DIR, 'web', 'data', 'stats.json');

// Test 1: catalog_index.json has occ field on items
const items = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
assert(items.length > 20000, "Catalog should have > 20,000 items");

const itemsWithOcc = items.filter(i => !!i.occ);
assert(itemsWithOcc.length === items.length, "All items must have an occ property");

// Test 2: stats.json has occupations with skills and mcps counts
const stats = JSON.parse(fs.readFileSync(statsPath, 'utf8'));
assert(Array.isArray(stats.occupations), "stats.occupations must be an array");
assert.strictEqual(stats.occupations.length, 10, "Must have 10 core occupations");

for (const occ of stats.occupations) {
  assert(occ.id, "Occupation must have id");
  assert(occ.title, "Occupation must have title");
  assert(occ.soc, "Occupation must have soc");
  assert(occ.total_count > 0, "Occupation must have total_count > 0");
  assert(occ.skills_count >= 0, "Occupation must have skills_count >= 0");
  assert(occ.mcps_count >= 0, "Occupation must have mcps_count >= 0");
  assert.strictEqual(occ.total_count, occ.skills_count + occ.mcps_count, "Total must equal skills + mcps");
}

console.log("All Node/JSON tests passed successfully!");
