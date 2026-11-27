// Conditional Popover API polyfill (modern-web-guidance: navbar)
if (!Object.hasOwn(HTMLElement.prototype, "popover")) {
  import("https://unpkg.com/@oddbird/popover-polyfill@latest/dist/popover.min.js");
}

// 1. Single-tree responsive navbar measurement (modern-web-guidance: navbar)
const header = document.getElementById("site-header");
const headerInner = document.getElementById("header-inner");
const siteMenu = document.getElementById("site-menu");
let lastHeaderWidth = 0;

function syncNavLayout() {
  const wasWide = header.classList.contains("is-wide");
  const currentWidth = header.clientWidth;

  if (!wasWide && currentWidth <= lastHeaderWidth) {
    return;
  }
  lastHeaderWidth = currentWidth;

  const wasOpen = !wasWide && siteMenu.matches(":popover-open, .\\:popover-open");
  header.classList.add("is-measuring", "is-wide");
  siteMenu.removeAttribute("popover");

  const fits = headerInner.scrollWidth <= headerInner.clientWidth;

  if (!fits) {
    header.classList.remove("is-wide");
    siteMenu.setAttribute("popover", "auto");
    if (wasOpen && typeof siteMenu.showPopover === "function") {
      siteMenu.showPopover();
    }
  }

  requestAnimationFrame(() => header.classList.remove("is-measuring"));
}

const navObserver = new ResizeObserver(syncNavLayout);
navObserver.observe(header);
navObserver.observe(siteMenu);
syncNavLayout();

// Close popover menu when clicking an in-page link on narrow screens
siteMenu.addEventListener("click", (event) => {
  if (event.target.closest("a") && !header.classList.contains("is-wide")) {
    if (typeof siteMenu.hidePopover === "function") {
      siteMenu.hidePopover();
    }
  }
});

// 2. Clipboard + accessible status toast
const toastRegion = document.getElementById("toast-region");
function showToast(message) {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  toastRegion.appendChild(toast);
  setTimeout(() => toast.remove(), 2200);
}

async function copyText(text, message = "Copied to clipboard") {
  try {
    await navigator.clipboard.writeText(text);
    showToast(message);
  } catch {
    showToast("Clipboard unavailable");
  }
}

document.querySelectorAll("[data-copy]").forEach((btn) => {
  btn.addEventListener("click", () => {
    copyText(btn.dataset.copy, btn.dataset.copyMsg || "Copied");
  });
});

// 3. Quick Start Tabs
const tabDocker = document.getElementById("tab-docker");
const tabLocal = document.getElementById("tab-local");
const panelDocker = document.getElementById("panel-docker");
const panelLocal = document.getElementById("panel-local");
let activeInstallTab = "docker";

function setInstallTab(tab) {
  activeInstallTab = tab;
  const isDocker = tab === "docker";
  tabDocker.setAttribute("aria-selected", String(isDocker));
  tabLocal.setAttribute("aria-selected", String(!isDocker));
  panelDocker.classList.toggle("hidden", !isDocker);
  panelLocal.classList.toggle("hidden", isDocker);
}

tabDocker.addEventListener("click", () => setInstallTab("docker"));
tabLocal.addEventListener("click", () => setInstallTab("local"));

document.getElementById("copy-install-btn").addEventListener("click", () => {
  const cmd = activeInstallTab === "docker"
    ? "docker build -t forexfactory-scrapper .\ndocker run -d -p 5000:5000 --name forexfactory-scrapper forexfactory-scrapper\ncurl -f http://localhost:5000/api/health"
    : "python -m venv .venv\nsource .venv/bin/activate\npip install -r requirements.txt\npython main.py";
  copyText(cmd, `${activeInstallTab.toUpperCase()} setup copied`);
});

// 4. Interactive API Sandbox Simulator
const simEndpoint = document.getElementById("sim-endpoint");
const simParamsBundle = document.getElementById("sim-params-bundle");
const simParamsDaily = document.getElementById("sim-params-daily");
const simParamsSitemaps = document.getElementById("sim-params-sitemaps");
const simParamsPagination = document.getElementById("sim-params-pagination");
const simStatusBadge = document.getElementById("sim-status-badge");
const simCurlOutput = document.getElementById("sim-curl-output");
const simJsonOutput = document.getElementById("sim-json-output");

let latestCurl = "";
let latestJson = "";

function highlightJson(obj) {
  const str = JSON.stringify(obj, null, 2);
  latestJson = str;
  return str.replace(
    /("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g,
    (match) => {
      let cls = "json-number";
      if (/^"/.test(match)) {
        cls = /:$/.test(match) ? "json-key" : "json-string";
      } else if (/true|false/.test(match)) {
        cls = "json-boolean";
      }
      return `<span class="${cls}">${match}</span>`;
    }
  );
}

function runSimulation() {
  const ep = simEndpoint.value;
  const limit = Number.parseInt(document.getElementById("sim-limit").value || "25", 10);
  const offset = Number.parseInt(document.getElementById("sim-offset").value || "0", 10);

  let url = "http://localhost:5000";
  let payload = {};
  let isError = false;

  if (ep !== "health" && (Number.isNaN(limit) || Number.isNaN(offset) || limit < 0 || offset < 0)) {
    isError = true;
    payload = { error: "Pagination parameters 'limit' and 'offset' must be non-negative integers." };
  }

  if (ep === "health") {
    url += "/api/health";
    // Mirrors src/routes/helper_routes.py: probe metrics are opt-in.
    payload = { status: "ok" };
  } else if (ep === "bundle") {
    const startDate = document.getElementById("sim-start-date").value || "2026-05-20";
    const endDate = document.getElementById("sim-end-date").value || "2026-05-21";
    const checked = Array.from(document.querySelectorAll(".sim-source-cb:checked")).map((cb) => cb.value);
    const activeSources = checked.length > 0 ? checked : ["forex"];

    url += `/api/bundle?sources=${activeSources.join(",")}&start_date=${startDate}&end_date=${endDate}&limit=${limit}&offset=${offset}`;

    if (!isError) {
      const breakdown = {};
      const events = [];
      activeSources.forEach((src, idx) => {
        breakdown[src] = src === "forex" ? 18 : 10;
        events.push({
          _source: src,
          _date: startDate,
          id: String(138542 + idx),
          currency: src === "crypto" ? "BTC" : src === "energy" ? "OIL" : src === "metal" ? "XAU" : "USD",
          impact: "High",
          event: src === "crypto" ? "Spot ETF Net Inflow" : src === "energy" ? "EIA Crude Stocks" : src === "metal" ? "LBMA Vault Report" : "CPI m/m"
        });
      });
      payload = {
        total: Object.values(breakdown).reduce((a, b) => a + b, 0),
        offset,
        limit,
        start_date: startDate,
        end_date: endDate,
        sources: activeSources,
        source_breakdown: breakdown,
        results: events.slice(0, Math.max(0, Math.min(limit, events.length)))
      };
    }
  } else if (["forex", "crypto", "energy", "metals"].includes(ep)) {
    const routeMap = {
      forex: "/api/forex/daily",
      crypto: "/api/cryptocraft/daily",
      energy: "/api/energyexch/daily",
      metals: "/api/metalsmine/daily"
    };
    const day = document.getElementById("sim-day").value || "20";
    const month = document.getElementById("sim-month").value || "5";
    const year = document.getElementById("sim-year").value || "2026";
    const paddedDate = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

    url += `${routeMap[ep]}?day=${day}&month=${month}&year=${year}&limit=${limit}&offset=${offset}`;

    if (!isError) {
      payload = {
        total: 14,
        offset,
        limit,
        results: [
          {
            id: "138542",
            date: paddedDate,
            time: "8:30am",
            currency: ep === "crypto" ? "ETH" : ep === "energy" ? "WTI" : ep === "metals" ? "XAU" : "USD",
            impact: "High",
            event: ep === "forex" ? "CPI m/m" : "Inventory & Flow Release",
            actual: "0.3%",
            forecast: "0.2%",
            previous: "0.4%"
          }
        ]
      };
    }
  } else if (ep === "sitemaps") {
    const maxPages = document.getElementById("sim-max-pages").value || "10";
    url += `/api/forex/sitemaps?max_pages=${maxPages}&limit=${limit}&offset=${offset}`;
    if (!isError) {
      payload = {
        total: 42,
        offset,
        limit,
        max_pages: Number.parseInt(maxPages, 10),
        results: [
          { loc: "https://www.forexfactory.com/calendar?day=may20.2026", lastmod: "2026-05-20T14:00:00Z" },
          { loc: "https://www.forexfactory.com/calendar?day=may21.2026", lastmod: "2026-05-21T09:15:00Z" }
        ]
      };
    }
  }

  simStatusBadge.textContent = isError ? "400 BAD REQUEST" : "200 OK";
  simStatusBadge.classList.toggle("status-badge--error", isError);

  latestCurl = `curl "${url}"`;
  simCurlOutput.textContent = latestCurl;
  simJsonOutput.innerHTML = highlightJson(payload);
}

function updateSimulatorUI() {
  const ep = simEndpoint.value;
  simParamsBundle.classList.toggle("hidden", ep !== "bundle");
  simParamsDaily.classList.toggle("hidden", !["forex", "crypto", "energy", "metals"].includes(ep));
  simParamsSitemaps.classList.toggle("hidden", ep !== "sitemaps");
  simParamsPagination.classList.toggle("hidden", ep === "health");
  runSimulation();
}

simEndpoint.addEventListener("change", updateSimulatorUI);
document.querySelectorAll("#playground input").forEach((input) => {
  input.addEventListener("input", runSimulation);
  input.addEventListener("change", runSimulation);
});

document.getElementById("copy-curl-btn").addEventListener("click", () => copyText(latestCurl, "cURL copied"));
document.getElementById("copy-json-btn").addEventListener("click", () => copyText(latestJson, "JSON copied"));

updateSimulatorUI();

// 5. Endpoint Table Filter
const endpointSearch = document.getElementById("endpoint-search");
const endpointRows = document.querySelectorAll(".endpoint-row");
endpointSearch.addEventListener("input", () => {
  const q = endpointSearch.value.trim().toLowerCase();
  endpointRows.forEach((row) => {
    row.classList.toggle("hidden", q !== "" && !row.textContent.toLowerCase().includes(q));
  });
});
