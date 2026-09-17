#!/usr/bin/env node

/**
 * Open-Agent-DB CLI (Node.js / npx entrypoint)
 * Universal package manager for AI Agent Skills & Model Context Protocol (MCP) Servers.
 */

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const ROOT_DIR = path.resolve(__dirname, '..');
const DATA_INDEX_PATH = path.join(ROOT_DIR, 'web', 'data', 'catalog_index.json');
const STATS_PATH = path.join(ROOT_DIR, 'web', 'data', 'stats.json');

// ANSI Colors
const c = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  cyan: '\x1b[36m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  white: '\x1b[37m',
  red: '\x1b[31m',
};

function renderBanner() {
  console.log(`
${c.cyan}╭──────────────────────────────────────────────────────────────────────────────╮${c.reset}
${c.cyan}│${c.reset} ${c.bold}${c.cyan}Open-Agent-DB${c.reset} ${c.dim}v0.1.0 (Node/npx)${c.reset} — ${c.bold}${c.white}The Universal AI Agent Registry${c.reset}             ${c.cyan}│${c.reset}
${c.cyan}│${c.reset} ${c.dim}800K+ Agent Skills & Model Context Protocol (MCP) Servers${c.reset}                    ${c.cyan}│${c.reset}
${c.cyan}╰──────────────────────────────────────────────────────────────────────────────╯${c.reset}
`);
}

function loadCatalogIndex() {
  if (!fs.existsSync(DATA_INDEX_PATH)) {
    console.error(`${c.red}Error: Catalog index file not found at ${DATA_INDEX_PATH}${c.reset}`);
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(DATA_INDEX_PATH, 'utf8'));
}

function loadStats() {
  if (fs.existsSync(STATS_PATH)) {
    return JSON.parse(fs.readFileSync(STATS_PATH, 'utf8'));
  }
  return null;
}

function cmdStats() {
  const stats = loadStats();
  console.log(`${c.bold}📊 Open-Agent-DB Catalog Overview${c.reset}\n`);

  const totalSkills = stats?.total_skills_indexed || 637876;
  const syncedSkills = stats?.total_skills_synced || 326829;
  const totalMcp = stats?.total_mcp_servers || 113566;
  const totalAssets = stats?.total_ecosystem_assets || 788158;

  console.log(`  ${c.cyan}• Agent Skills (Indexed):${c.reset}  ${c.green}${totalSkills.toLocaleString()}${c.reset} (SkillsMP, Claude, Codex)`);
  console.log(`  ${c.cyan}• Downloaded Packages:${c.reset}     ${c.green}${syncedSkills.toLocaleString()}${c.reset} (Full source in SQLite BLOBs)`);
  console.log(`  ${c.cyan}• MCP Servers (Total):${c.reset}     ${c.green}${totalMcp.toLocaleString()}${c.reset} (Glama, Smithery, Official MCP)`);
  console.log(`  ${c.cyan}• Curated Quick-Index:${c.reset}     ${c.green}${(stats?.web_index_count || 27000).toLocaleString()}${c.reset} (Instant browser & npx search)`);
  console.log(`\n  ${c.bold}${c.white}Total Ecosystem Assets:${c.reset}   ${c.bold}${c.yellow}${totalAssets.toLocaleString()}${c.reset}\n`);
}

function cmdSearch(args) {
  let typeFilter = null;
  let domainFilter = null;
  let categoryFilter = null;
  let minStars = 0;
  let limit = 20;
  const queryWords = [];

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--type' && args[i + 1]) {
      typeFilter = args[++i];
    } else if (arg === '--domain' && args[i + 1]) {
      domainFilter = args[++i].toLowerCase();
    } else if (arg === '--category' && args[i + 1]) {
      categoryFilter = args[++i].toLowerCase();
    } else if (arg === '--min-stars' && args[i + 1]) {
      minStars = parseInt(args[++i], 10) || 0;
    } else if (arg === '--limit' && args[i + 1]) {
      limit = parseInt(args[++i], 10) || 20;
    } else if (!arg.startsWith('--')) {
      queryWords.push(arg);
    }
  }

  const query = queryWords.join(' ').trim().toLowerCase();

  const items = loadCatalogIndex();
  const tokens = query ? query.split(/\s+/).filter(Boolean) : [];

  const matched = items.filter(item => {
    if (typeFilter && item.t !== typeFilter) return false;
    if (domainFilter && domainFilter !== 'all' && (item.dom || '').toLowerCase() !== domainFilter) return false;
    if (categoryFilter && categoryFilter !== 'all' && (item.cat || '').toLowerCase() !== categoryFilter) return false;
    if (minStars > 0 && (item.s || 0) < minStars) return false;

    if (tokens.length > 0) {
      const target = `${item.n} ${item.d || ''} ${item.a || ''} ${item.dom || ''} ${item.cat || ''}`.toLowerCase();
      for (let t of tokens) {
        if (!target.includes(t)) return false;
      }
    }
    return true;
  });

  matched.sort((a, b) => (b.s || 0) - (a.s || 0));

  console.log(`${c.magenta}${c.bold}🔎 Search Results: '${query || '*'}' (${matched.length} matches)${c.reset}\n`);

  const display = matched.slice(0, limit);
  if (display.length === 0) {
    console.log(`${c.yellow}No matching assets found.${c.reset}\n`);
    return;
  }

  // Format columns
  display.forEach(r => {
    const isMcp = r.t === 'mcp_server';
    const typeStr = isMcp ? `${c.green}[MCP]${c.reset}` : `${c.cyan}[Skill]${c.reset}`;
    const starsStr = r.s > 0 ? `${c.yellow}⭐ ${r.s.toLocaleString()}${c.reset}` : `${c.dim}-${c.reset}`;
    const desc = (r.d || 'No description').replace(/\n/g, ' ').substring(0, 55);
    const domCat = `${r.dom || 'General'} › ${r.cat || 'Skill'}`;

    console.log(`  ${typeStr} ${c.bold}${c.white}${r.n}${c.reset} ${c.magenta}[${domCat}]${c.reset} ${c.dim}by ${r.a}${c.reset} (${r.p})`);
    console.log(`     ${starsStr} | ${c.dim}${desc}...${c.reset}`);
    const installCmd = r.i || (isMcp ? `npx -y ${r.n}` : `open-agent install ${r.id}`);
    console.log(`     ${c.dim}Install:${c.reset} ${c.cyan}${installCmd}${c.reset}\n`);
  });

  console.log(`${c.dim}Tip: Run 'npx open-agent-db info <id>' for details or 'install <id>' for config.${c.reset}\n`);
}

function cmdInfo(id) {
  if (!id) {
    console.error(`${c.red}Error: Please specify an asset name or ID.${c.reset}`);
    process.exit(1);
  }

  const items = loadCatalogIndex();
  const item = items.find(x => x.id === id || x.n.toLowerCase() === id.toLowerCase());

  if (!item) {
    console.error(`${c.red}Error: Asset '${id}' not found in catalog index.${c.reset}`);
    process.exit(1);
  }

  const isMcp = item.t === 'mcp_server';
  console.log(`\n${c.cyan}╭───────────────────────────── 📦 ${item.n} ─────────────────────────────╮${c.reset}`);
  console.log(`  ${c.bold}Name:${c.reset}           ${item.n}`);
  console.log(`  ${c.bold}Type:${c.reset}           ${isMcp ? 'MCP Server' : 'Agent Skill'} (${item.p})`);
  console.log(`  ${c.bold}Domain:${c.reset}         ${item.dom || 'General'}`);
  console.log(`  ${c.bold}Category:${c.reset}       ${item.cat || 'Skill'}`);
  console.log(`  ${c.bold}Author:${c.reset}         ${item.a}`);
  console.log(`  ${c.bold}Stars:${c.reset}          ⭐ ${(item.s || 0).toLocaleString()}`);
  if (item.g) console.log(`  ${c.bold}GitHub:${c.reset}         ${item.g}`);
  console.log(`  ${c.bold}Install Command:${c.reset} ${c.green}${item.i || `npx -y ${item.n}`}${c.reset}`);
  console.log(`\n  ${c.bold}Description:${c.reset}`);
  console.log(`  ${item.d || 'No description provided.'}`);
  console.log(`${c.cyan}╰──────────────────────────────────────────────────────────────────────────────╯${c.reset}\n`);
}

function cmdInstall(id) {
  if (!id) {
    console.error(`${c.red}Error: Please specify an asset to install.${c.reset}`);
    process.exit(1);
  }

  const items = loadCatalogIndex();
  const item = items.find(x => x.id === id || x.n.toLowerCase() === id.toLowerCase());

  if (!item) {
    console.error(`${c.red}Error: Asset '${id}' not found in catalog index.${c.reset}`);
    process.exit(1);
  }

  const isMcp = item.t === 'mcp_server';

  if (isMcp) {
    const cmd = item.i || `npx -y ${item.n}`;
    let command = "npx";
    let args = ["-y", item.n];

    if (cmd.startsWith("npx")) {
      const parts = cmd.split(/\s+/);
      command = parts[0];
      args = parts.slice(1);
    }

    const cfg = {
      mcpServers: {
        [item.n]: {
          command: command,
          args: args
        }
      }
    };

    console.log(`\n${c.green}╭───────────── 🔌 MCP Server Configuration for [${item.n}] ──────────────╮${c.reset}`);
    console.log(JSON.stringify(cfg, null, 2));
    console.log(`${c.green}╰───── Add this snippet to claude_desktop_config.json or cursor mcp.json ──────╯${c.reset}\n`);
    console.log(`Or execute directly: ${c.bold}${c.green}${cmd}${c.reset}\n`);
  } else {
    console.log(`\n${c.cyan}⚡ Agent Skill Install Command:${c.reset}`);
    console.log(`  ${c.bold}${c.green}${item.i || `open-agent install ${item.id}`}${c.reset}\n`);
    if (item.g) {
      console.log(`  ${c.dim}Source Repository: ${item.g}${c.reset}\n`);
    }
  }
}

function cmdServe(port = 8080) {
  const webDir = path.join(ROOT_DIR, 'web');
  console.log(`\n${c.cyan}🚀 Launching Open-Agent-DB Web Explorer on http://localhost:${port}...${c.reset}\n`);
  
  // Check if python3 is available to launch serve.py with full SQLite FTS5 backend
  const pyCheck = spawnSync('python3', ['--version']);
  if (pyCheck.status === 0) {
    const servePy = path.join(webDir, 'serve.py');
    const child = spawnSync('python3', [servePy, '--port', String(port)], { stdio: 'inherit' });
    process.exit(child.status);
  } else {
    // Fallback: simple http server
    const http = require('http');
    const server = http.createServer((req, res) => {
      let filePath = path.join(webDir, req.url === '/' ? 'index.html' : req.url.split('?')[0]);
      if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
        const ext = path.extname(filePath);
        const mimeTypes = {
          '.html': 'text/html',
          '.js': 'application/javascript',
          '.css': 'text/css',
          '.json': 'application/json',
          '.svg': 'image/svg+xml'
        };
        res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'text/plain' });
        fs.createReadStream(filePath).pipe(res);
      } else {
        res.writeHead(404);
        res.end('Not found');
      }
    });
    server.listen(port, () => {
      console.log(`Serving static explorer at http://localhost:${port}`);
    });
  }
}

function main() {
  renderBanner();
  const args = process.argv.slice(2);
  const command = args[0] || 'help';

  switch (command) {
    case 'stats':
      cmdStats();
      break;
    case 'search':
      cmdSearch(args.slice(1));
      break;
    case 'info':
      cmdInfo(args[1]);
      break;
    case 'install':
      cmdInstall(args[1]);
      break;
    case 'serve':
      const portIdx = args.indexOf('--port');
      const port = portIdx !== -1 ? parseInt(args[portIdx + 1], 10) : 8080;
      cmdServe(port);
      break;
    case 'help':
    default:
      console.log(`${c.bold}Usage:${c.reset} npx open-agent-db <command> [options]\n`);
      console.log(`Commands:`);
      console.log(`  ${c.cyan}search <query>${c.reset}     Search across 800K+ skills & MCP servers`);
      console.log(`  ${c.cyan}info <id>${c.reset}          Show asset metadata & description`);
      console.log(`  ${c.cyan}install <id>${c.reset}       Get MCP JSON configuration or install skill`);
      console.log(`  ${c.cyan}stats${c.reset}              Show catalog overview metrics`);
      console.log(`  ${c.cyan}serve [--port N]${c.reset}   Launch interactive web search UI\n`);
      break;
  }
}

main();
