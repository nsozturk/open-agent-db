/**
 * Open-Agent-DB Web Explorer
 * Dual-mode search engine:
 * 1. Static Client-Side Mode (Runs on GitHub Pages with zero backend)
 * 2. Local Full-Database Mode (Communicates with local serve.py SQLite FTS5 backend)
 */

(function () {
  let allItems = [];
  let filteredItems = [];
  let currentPage = 1;
  const PAGE_SIZE = 24;
  let isLocalApi = false;

  const DOMAIN_ICONS = {
    "Data & AI": "🧠",
    "Tools": "🛠️",
    "Development": "💻",
    "Testing & Security": "🛡️",
    "Business": "📈",
    "DevOps": "🚀",
    "Documentation": "📚",
    "Content & Media": "🎨",
    "Research": "🔬",
    "Databases": "🗄️",
    "Lifestyle": "🌱",
    "Blockchain": "⛓️"
  };

  // State
  let currentTypeFilter = "all";
  let currentDomainFilter = "all";
  let currentCategoryFilter = "all";
  let domainTaxonomy = {}; // domain -> { count: N, categories: { cat: count } }

  // DOM Elements
  const searchInput = document.getElementById("search-input");
  const clearBtn = document.getElementById("clear-btn");
  const platformSelect = document.getElementById("platform-select");
  const domainSelect = document.getElementById("domain-select");
  const categorySelect = document.getElementById("category-select");
  const starsSelect = document.getElementById("stars-select");
  const verifiedCheckbox = document.getElementById("verified-checkbox");
  const sortSelect = document.getElementById("sort-select");
  const resultsGrid = document.getElementById("results-grid");
  const emptyState = document.getElementById("empty-state");
  const resultsCount = document.getElementById("results-count");
  const prevPageBtn = document.getElementById("prev-page-btn");
  const nextPageBtn = document.getElementById("next-page-btn");
  const pageIndicator = document.getElementById("page-indicator");
  const typeTabs = document.querySelectorAll(".type-tab");
  const domainPillsContainer = document.getElementById("domain-pills");
  const categoryPillsContainer = document.getElementById("category-pills");
  const resetDomainBtn = document.getElementById("reset-domain-btn");

  // Modal Elements
  const detailModal = document.getElementById("detail-modal");
  const modalClose = document.getElementById("modal-close");
  const modalBreadcrumb = document.getElementById("modal-breadcrumb");
  const modalTitle = document.getElementById("modal-title");
  const modalIcon = document.getElementById("modal-icon");
  const modalBadges = document.getElementById("modal-badges");
  const modalDescription = document.getElementById("modal-description");
  const modalInstallLabel = document.getElementById("modal-install-label");
  const modalInstallCode = document.getElementById("modal-install-code");
  const modalCopyBtn = document.getElementById("modal-copy-btn");
  const modalGithubLink = document.getElementById("modal-github-link");

  // CLI Guide Modal
  const cliHelpBtn = document.getElementById("cli-help-btn");
  const cliModal = document.getElementById("cli-modal");
  const cliModalClose = document.getElementById("cli-modal-close");

  async function init() {
    try {
      const apiCheck = await fetch("/api/status", { method: "HEAD" }).catch(() => null);
      if (apiCheck && apiCheck.ok) {
        isLocalApi = true;
        console.log("⚡ Connected to Open-Agent-DB Local SQLite API Server!");
      }
    } catch (_) {}

    // Load Stats
    try {
      const statsResp = await fetch("data/stats.json");
      if (statsResp.ok) {
        const stats = await statsResp.json();
        updateStatsUI(stats);
      }
    } catch (e) {
      console.warn("Could not load stats.json", e);
    }

    // Load Catalog Index
    try {
      resultsGrid.innerHTML = `
        <div class="col-span-full py-16 text-center text-slate-400">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-emerald-500 mb-3"></div>
          <p class="text-sm font-mono">Loading 27,000+ curated AI skills & MCP servers...</p>
        </div>
      `;
      const resp = await fetch("data/catalog_index.json");
      if (!resp.ok) throw new Error("Network response not ok");
      allItems = await resp.json();

      buildTaxonomyIndex();
      updateTabCounts();
      renderDomainPills();
      renderCategoryPills();
      applyFilters();
    } catch (err) {
      console.error("Failed to load catalog index:", err);
      resultsGrid.innerHTML = `
        <div class="col-span-full py-16 text-center text-rose-400">
          <p class="font-bold">Failed to load catalog index.</p>
          <p class="text-xs text-slate-500 mt-1">Please ensure 'data/catalog_index.json' is present.</p>
        </div>
      `;
    }
  }

  function updateStatsUI(stats) {
    if (stats.total_skills_indexed) {
      document.getElementById("stat-total-skills").textContent = (stats.total_skills_indexed / 1000).toFixed(0) + "K+";
    }
    if (stats.total_mcp_servers) {
      document.getElementById("stat-total-mcp").textContent = (stats.total_mcp_servers / 1000).toFixed(0) + "K+";
    }
    if (stats.total_skills_synced) {
      document.getElementById("stat-total-synced").textContent = (stats.total_skills_synced / 1000).toFixed(0) + "K+";
    }
  }

  function updateTabCounts() {
    let mcpCount = 0;
    let skillCount = 0;
    let cursorCount = 0;

    for (let i = 0; i < allItems.length; i++) {
      const t = allItems[i].t;
      if (t === "mcp_server") mcpCount++;
      else if (t === "skill") skillCount++;
      else if (t === "cursor_rule") cursorCount++;
    }

    document.getElementById("count-all").textContent = allItems.length.toLocaleString();
    document.getElementById("count-mcp").textContent = mcpCount.toLocaleString();
    document.getElementById("count-skill").textContent = skillCount.toLocaleString();
    document.getElementById("count-cursor").textContent = cursorCount.toLocaleString();
  }

  // Build Taxonomy from all items
  function buildTaxonomyIndex() {
    domainTaxonomy = {};

    for (const item of allItems) {
      const dom = item.dom || "Other";
      const cat = item.cat || "General";

      if (!domainTaxonomy[dom]) {
        domainTaxonomy[dom] = { count: 0, categories: {} };
      }
      domainTaxonomy[dom].count++;
      domainTaxonomy[dom].categories[cat] = (domainTaxonomy[dom].categories[cat] || 0) + 1;
    }

    // Populate Domain Dropdown
    domainSelect.innerHTML = `<option value="all">All Domains (${allItems.length.toLocaleString()})</option>`;
    const sortedDomains = Object.keys(domainTaxonomy).sort((a, b) => domainTaxonomy[b].count - domainTaxonomy[a].count);
    for (const dom of sortedDomains) {
      const icon = DOMAIN_ICONS[dom] || "📁";
      const opt = document.createElement("option");
      opt.value = dom;
      opt.textContent = `${icon} ${dom} (${domainTaxonomy[dom].count.toLocaleString()})`;
      domainSelect.appendChild(opt);
    }
  }

  // Render Horizontal Domain Pills
  function renderDomainPills() {
    let html = `
      <button 
        data-domain="all" 
        class="domain-pill ${currentDomainFilter === 'all' ? 'active' : ''} px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-900 border border-slate-800 text-slate-300 flex items-center gap-1.5 shrink-0"
      >
        <span>🌐</span>
        <span>All Domains</span>
        <span class="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-800/80 text-slate-400 font-mono">${allItems.length.toLocaleString()}</span>
      </button>
    `;

    const sortedDomains = Object.keys(domainTaxonomy).sort((a, b) => domainTaxonomy[b].count - domainTaxonomy[a].count);

    for (const dom of sortedDomains) {
      const icon = DOMAIN_ICONS[dom] || "📁";
      const count = domainTaxonomy[dom].count;
      const countLabel = count >= 1000 ? (count / 1000).toFixed(1) + "K" : count;
      const isActive = currentDomainFilter === dom;

      html += `
        <button 
          data-domain="${escapeAttr(dom)}" 
          class="domain-pill ${isActive ? 'active' : ''} px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-900 border border-slate-800 text-slate-300 flex items-center gap-1.5 shrink-0"
        >
          <span>${icon}</span>
          <span>${escapeHtml(dom)}</span>
          <span class="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-800/80 text-slate-400 font-mono">${countLabel}</span>
        </button>
      `;
    }

    domainPillsContainer.innerHTML = html;

    // Attach click listeners to domain pills
    domainPillsContainer.querySelectorAll(".domain-pill").forEach(pill => {
      pill.addEventListener("click", () => {
        const dom = pill.dataset.domain;
        selectDomain(dom);
      });
    });
  }

  // Select Domain action
  function selectDomain(domain) {
    currentDomainFilter = domain;
    currentCategoryFilter = "all";

    domainSelect.value = domain;
    resetDomainBtn.classList.toggle("hidden", domain === "all");

    // Update active state in domain pills
    domainPillsContainer.querySelectorAll(".domain-pill").forEach(p => {
      p.classList.toggle("active", p.dataset.domain === domain);
    });

    renderCategoryPills();
    applyFilters();
  }

  // Render Horizontal Category Pills
  function renderCategoryPills() {
    let categoriesList = [];

    if (currentDomainFilter === "all") {
      // Aggregate top categories across all domains
      const allCats = {};
      for (const dom in domainTaxonomy) {
        for (const cat in domainTaxonomy[dom].categories) {
          allCats[cat] = (allCats[cat] || 0) + domainTaxonomy[dom].categories[cat];
        }
      }
      categoriesList = Object.entries(allCats)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15);
    } else {
      // Subcategories of selected domain
      const domCats = domainTaxonomy[currentDomainFilter]?.categories || {};
      categoriesList = Object.entries(domCats).sort((a, b) => b[1] - a[1]);
    }

    let html = `
      <button 
        data-cat="all" 
        class="category-pill ${currentCategoryFilter === 'all' ? 'active' : ''} px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-950 border border-slate-800 text-slate-400 shrink-0"
      >
        ${currentDomainFilter === 'all' ? 'Top Categories' : `All in ${escapeHtml(currentDomainFilter)}`}
      </button>
    `;

    for (const [catName, count] of categoriesList) {
      const isActive = currentCategoryFilter === catName;
      const countLabel = count >= 1000 ? (count / 1000).toFixed(1) + "K" : count;

      html += `
        <button 
          data-cat="${escapeAttr(catName)}" 
          class="category-pill ${isActive ? 'active' : ''} px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-950 border border-slate-800 text-slate-400 hover:text-slate-200 shrink-0"
        >
          <span>${escapeHtml(catName)}</span>
          <span class="text-[10px] text-slate-500 font-mono ml-1">(${countLabel})</span>
        </button>
      `;
    }

    categoryPillsContainer.innerHTML = html;

    // Populate Category Dropdown
    categorySelect.innerHTML = `<option value="all">${currentDomainFilter === 'all' ? 'All Categories' : `All in ${currentDomainFilter}`}</option>`;
    for (const [catName, count] of categoriesList) {
      const opt = document.createElement("option");
      opt.value = catName;
      opt.textContent = `${catName} (${count})`;
      if (catName === currentCategoryFilter) opt.selected = true;
      categorySelect.appendChild(opt);
    }

    // Attach click listeners to category pills
    categoryPillsContainer.querySelectorAll(".category-pill").forEach(pill => {
      pill.addEventListener("click", () => {
        const cat = pill.dataset.cat;
        selectCategory(cat);
      });
    });
  }

  // Select Category action
  function selectCategory(category) {
    currentCategoryFilter = category;
    categorySelect.value = category;

    // Update active pill
    categoryPillsContainer.querySelectorAll(".category-pill").forEach(p => {
      p.classList.toggle("active", p.dataset.cat === category);
    });

    applyFilters();
  }

  // Filter & Search Engine
  function applyFilters() {
    const query = (searchInput.value || "").trim().toLowerCase();
    const platform = platformSelect.value;
    const minStars = parseInt(starsSelect.value || "0", 10);
    const verifiedOnly = verifiedCheckbox.checked;
    const sortBy = sortSelect.value;

    clearBtn.classList.toggle("hidden", query.length === 0);

    const tokens = query ? query.split(/\s+/).filter(Boolean) : [];

    filteredItems = allItems.filter(item => {
      // Type Tab Filter
      if (currentTypeFilter !== "all" && item.t !== currentTypeFilter) {
        return false;
      }

      // Domain Filter
      if (currentDomainFilter !== "all" && item.dom !== currentDomainFilter) {
        return false;
      }

      // Category Filter
      if (currentCategoryFilter !== "all" && item.cat !== currentCategoryFilter) {
        return false;
      }

      // Platform Filter
      if (platform !== "all" && item.p !== platform) {
        return false;
      }

      // Min Stars Filter
      if (minStars > 0 && (item.s || 0) < minStars) {
        return false;
      }

      // Verified Filter
      if (verifiedOnly && !item.v) {
        return false;
      }

      // Query Tokens Filter (Searches name, desc, author, domain, and category)
      if (tokens.length > 0) {
        const target = (
          item.n + " " + 
          (item.d || "") + " " + 
          (item.a || "") + " " + 
          (item.dom || "") + " " + 
          (item.cat || "")
        ).toLowerCase();
        for (let t of tokens) {
          if (!target.includes(t)) return false;
        }
      }

      return true;
    });

    // Sorting
    filteredItems.sort((a, b) => {
      if (sortBy === "stars") {
        return (b.s || 0) - (a.s || 0);
      } else if (sortBy === "used") {
        return (b.u || 0) - (a.u || 0);
      } else if (sortBy === "name") {
        return a.n.localeCompare(b.n);
      }
      return 0;
    });

    currentPage = 1;
    renderResults();
  }

  function renderResults() {
    resultsCount.textContent = `Showing ${filteredItems.length.toLocaleString()} results`;

    if (filteredItems.length === 0) {
      resultsGrid.innerHTML = "";
      emptyState.classList.remove("hidden");
      document.getElementById("pagination-wrapper").classList.add("hidden");
      return;
    }

    emptyState.classList.add("hidden");
    document.getElementById("pagination-wrapper").classList.remove("hidden");

    const totalPages = Math.ceil(filteredItems.length / PAGE_SIZE) || 1;
    const startIdx = (currentPage - 1) * PAGE_SIZE;
    const pageItems = filteredItems.slice(startIdx, startIdx + PAGE_SIZE);

    pageIndicator.textContent = `Page ${currentPage} of ${totalPages}`;
    prevPageBtn.disabled = currentPage <= 1;
    nextPageBtn.disabled = currentPage >= totalPages;

    let html = "";
    for (let item of pageItems) {
      const isMcp = item.t === "mcp_server";
      const isCursor = item.t === "cursor_rule";
      const icon = isMcp ? "🔌" : isCursor ? "🎯" : "⚡";
      const badgeClass = isMcp ? "badge-mcp" : isCursor ? "badge-cursor" : "badge-skill";
      const typeLabel = isMcp ? "MCP Server" : isCursor ? "Cursor Rule" : "Agent Skill";
      const domIcon = DOMAIN_ICONS[item.dom] || "📁";
      const installCmd = item.i || (isMcp ? `npx -y ${item.n}` : `open-agent install ${item.id}`);

      html += `
        <div class="asset-card bg-slate-900/90 border border-slate-800 rounded-xl p-4 flex flex-col justify-between" data-id="${item.id}">
          <div>
            <!-- Top Badges Row -->
            <div class="flex items-start justify-between gap-2 mb-2">
              <div class="flex flex-wrap items-center gap-1.5">
                <span class="text-lg">${icon}</span>
                <span class="text-[11px] px-2 py-0.5 rounded-full font-medium ${badgeClass}">${typeLabel}</span>
                ${item.v ? '<span class="text-xs text-amber-400" title="Verified Publisher">🛡️</span>' : ''}
              </div>
              <div class="flex items-center gap-1 text-xs text-amber-400 font-mono font-medium shrink-0">
                ${item.s > 0 ? `<span>⭐ ${item.s.toLocaleString()}</span>` : '<span class="text-slate-600">-</span>'}
              </div>
            </div>

            <!-- Title -->
            <h3 class="font-bold text-base text-white hover:text-emerald-400 transition cursor-pointer line-clamp-1 mb-1" onclick="window.openDetails('${item.id}')">
              ${escapeHtml(item.n)}
            </h3>

            <!-- Author & Platform -->
            <div class="text-xs text-slate-400 mb-2 flex items-center gap-1.5">
              <span>by <strong class="text-slate-300 font-normal">${escapeHtml(item.a)}</strong></span>
              <span class="text-slate-600">•</span>
              <span class="capitalize text-slate-500 font-mono">${item.p.replace('_', ' ')}</span>
            </div>

            <!-- Domain & Category Badges (Interactive Filter Discovery) -->
            <div class="flex flex-wrap items-center gap-1.5 mb-2.5">
              <button 
                onclick="window.quickFilterDomain('${escapeAttr(item.dom)}')" 
                class="badge-domain text-[10px] px-2 py-0.5 rounded-md font-medium hover:brightness-125 transition flex items-center gap-1"
                title="Filter by domain: ${escapeAttr(item.dom)}"
              >
                <span>${domIcon}</span>
                <span>${escapeHtml(item.dom)}</span>
              </button>
              <button 
                onclick="window.quickFilterCategory('${escapeAttr(item.dom)}', '${escapeAttr(item.cat)}')" 
                class="badge-category text-[10px] px-2 py-0.5 rounded-md font-medium hover:brightness-125 transition"
                title="Filter by category: ${escapeAttr(item.cat)}"
              >
                ${escapeHtml(item.cat)}
              </button>
            </div>

            <!-- Description -->
            <p class="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-4">
              ${escapeHtml(item.d || "No description provided.")}
            </p>
          </div>

          <!-- Bottom Install Box -->
          <div class="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-2">
            <button 
              onclick="window.copyCommand('${escapeAttr(installCmd)}', this)"
              class="flex-1 text-xs py-1.5 px-2.5 rounded-lg bg-slate-950 hover:bg-slate-800 text-slate-300 font-mono truncate border border-slate-800 flex items-center justify-between gap-1 transition"
              title="Click to copy install command: ${escapeAttr(installCmd)}"
            >
              <span class="truncate text-emerald-400">${escapeHtml(installCmd)}</span>
              <span class="text-slate-500 text-[10px]">📋</span>
            </button>

            <button 
              onclick="window.openDetails('${item.id}')"
              class="text-xs px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition font-medium shrink-0"
            >
              Info
            </button>
          </div>
        </div>
      `;
    }

    resultsGrid.innerHTML = html;
  }

  // Quick Filter helpers for card clicks
  window.quickFilterDomain = function (domain) {
    selectDomain(domain);
    window.scrollTo({ top: 150, behavior: "smooth" });
  };

  window.quickFilterCategory = function (domain, category) {
    currentDomainFilter = domain;
    domainSelect.value = domain;
    resetDomainBtn.classList.remove("hidden");
    domainPillsContainer.querySelectorAll(".domain-pill").forEach(p => {
      p.classList.toggle("active", p.dataset.domain === domain);
    });
    renderCategoryPills();
    selectCategory(category);
    window.scrollTo({ top: 150, behavior: "smooth" });
  };

  // Modal Detail View
  window.openDetails = function (id) {
    const item = allItems.find(x => x.id === id);
    if (!item) return;

    const isMcp = item.t === "mcp_server";
    const isCursor = item.t === "cursor_rule";
    const icon = isMcp ? "🔌" : isCursor ? "🎯" : "⚡";
    const badgeClass = isMcp ? "badge-mcp" : isCursor ? "badge-cursor" : "badge-skill";
    const typeLabel = isMcp ? "MCP Server" : isCursor ? "Cursor Rule" : "Agent Skill";
    const domIcon = DOMAIN_ICONS[item.dom] || "📁";
    const installCmd = item.i || (isMcp ? `npx -y ${item.n}` : `open-agent install ${item.id}`);

    modalIcon.textContent = icon;
    modalTitle.textContent = item.n;
    modalDescription.textContent = item.d || "No description provided.";
    modalInstallCode.textContent = isMcp ? generateMcpJson(item) : installCmd;
    modalInstallLabel.textContent = isMcp ? "Claude Desktop / Cursor MCP JSON Config" : "1-Click CLI Install Command";

    // Taxonomy breadcrumb
    modalBreadcrumb.innerHTML = `
      <span>${domIcon} ${escapeHtml(item.dom || 'General')}</span>
      <span class="text-slate-600 font-bold">&rsaquo;</span>
      <span class="text-slate-300 font-semibold">${escapeHtml(item.cat || 'Skill')}</span>
    `;

    modalBadges.innerHTML = `
      <span class="text-xs px-2 py-0.5 rounded-full font-medium ${badgeClass}">${typeLabel}</span>
      <span class="text-xs px-2 py-0.5 rounded-full badge-domain font-medium">${domIcon} ${escapeHtml(item.dom)}</span>
      <span class="text-xs px-2 py-0.5 rounded-full badge-category font-medium">${escapeHtml(item.cat)}</span>
      <span class="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">by ${escapeHtml(item.a)}</span>
      <span class="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 font-mono">${item.p}</span>
      ${item.s > 0 ? `<span class="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 font-mono">⭐ ${item.s.toLocaleString()}</span>` : ''}
    `;

    if (item.g) {
      modalGithubLink.href = item.g;
      modalGithubLink.classList.remove("hidden");
    } else {
      modalGithubLink.classList.add("hidden");
    }

    modalCopyBtn.onclick = () => {
      navigator.clipboard.writeText(modalInstallCode.textContent);
      modalCopyBtn.textContent = "Copied!";
      setTimeout(() => { modalCopyBtn.textContent = "Copy"; }, 2000);
    };

    detailModal.classList.remove("hidden");
  };

  function generateMcpJson(item) {
    const name = item.n || "mcp-server";
    const cmd = item.i || "";
    let command = "npx";
    let args = ["-y", name];

    if (cmd.startsWith("npx")) {
      const parts = cmd.split(/\s+/);
      command = parts[0];
      args = parts.slice(1);
    }

    const cfg = {
      mcpServers: {
        [name]: {
          command: command,
          args: args
        }
      }
    };
    return JSON.stringify(cfg, null, 2);
  }

  window.copyCommand = function (cmd, btn) {
    navigator.clipboard.writeText(cmd);
    const orig = btn.innerHTML;
    btn.innerHTML = `<span class="text-emerald-400 font-bold">✓ Copied to clipboard!</span>`;
    setTimeout(() => { btn.innerHTML = orig; }, 1500);
  };

  function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function escapeAttr(str) {
    if (!str) return "";
    return str.replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  // Event Listeners
  let debounceTimeout = null;
  searchInput.addEventListener("input", () => {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(applyFilters, 150);
  });

  clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    applyFilters();
    searchInput.focus();
  });

  platformSelect.addEventListener("change", applyFilters);
  starsSelect.addEventListener("change", applyFilters);
  verifiedCheckbox.addEventListener("change", applyFilters);
  sortSelect.addEventListener("change", applyFilters);

  // Dropdown Listeners
  domainSelect.addEventListener("change", (e) => {
    selectDomain(e.target.value);
  });

  categorySelect.addEventListener("change", (e) => {
    selectCategory(e.target.value);
  });

  resetDomainBtn.addEventListener("click", () => {
    selectDomain("all");
  });

  // Type Tabs
  typeTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      typeTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      currentTypeFilter = tab.dataset.type;
      applyFilters();
    });
  });

  // Pagination
  prevPageBtn.addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      renderResults();
      window.scrollTo({ top: 300, behavior: "smooth" });
    }
  });

  nextPageBtn.addEventListener("click", () => {
    const totalPages = Math.ceil(filteredItems.length / PAGE_SIZE);
    if (currentPage < totalPages) {
      currentPage++;
      renderResults();
      window.scrollTo({ top: 300, behavior: "smooth" });
    }
  });

  // Modal Closures
  modalClose.addEventListener("click", () => detailModal.classList.add("hidden"));
  detailModal.addEventListener("click", (e) => {
    if (e.target === detailModal) detailModal.classList.add("hidden");
  });

  cliHelpBtn.addEventListener("click", () => cliModal.classList.remove("hidden"));
  cliModalClose.addEventListener("click", () => cliModal.classList.add("hidden"));
  cliModal.addEventListener("click", (e) => {
    if (e.target === cliModal) cliModal.classList.add("hidden");
  });

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      detailModal.classList.add("hidden");
      cliModal.classList.add("hidden");
    }
    if ((e.metaKey || e.ctrlKey) && e.key === "k") {
      e.preventDefault();
      searchInput.focus();
      searchInput.select();
    }
  });

  // Start app
  init();
})();
