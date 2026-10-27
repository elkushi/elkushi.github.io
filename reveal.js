// Fades sections in as they scroll into view. Without JS, everything is visible.
const io = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
}, { threshold: 0.12 });
document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

// The header firms up once the hero is behind you. A 1px marker at the top of
// the page does it, so there is no scroll handler running the whole time.
const nav = document.querySelector(".nav");
if (nav) {
  const mark = document.createElement("div");
  mark.style.position = "absolute";
  mark.style.top = "0";
  mark.style.width = "1px";
  mark.style.height = "1px";
  document.body.prepend(mark);
  new IntersectionObserver(([e]) => nav.classList.toggle("scrolled", !e.isIntersecting)).observe(mark);
}

// Read progress. Browsers with scroll-driven CSS fill the bar themselves; the
// rest (Firefox today) get it from here, one write per frame.
const bar = document.querySelector(".progress span");
if (bar && !(window.CSS && CSS.supports("animation-timeline", "scroll()"))
    && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
  let queued = false;
  const draw = () => {
    queued = false;
    const d = document.documentElement;
    const max = d.scrollHeight - d.clientHeight;
    bar.style.transform = `scaleX(${max > 0 ? d.scrollTop / max : 0})`;
  };
  addEventListener("scroll", () => {
    if (!queued) { queued = true; requestAnimationFrame(draw); }
  }, { passive: true });
  draw();
}

// Light / dark toggle. The choice is remembered; without it the system setting wins.
const root = document.documentElement;
const toggle = document.querySelector(".theme-toggle");
if (toggle) {
  toggle.addEventListener("click", () => {
    const dark = root.dataset.theme ? root.dataset.theme === "dark" : true;  // dark is the default
    root.dataset.theme = dark ? "light" : "dark";
    try { localStorage.setItem("theme", root.dataset.theme); } catch (e) { /* private mode */ }
  });
}

// Phone menu. It is a <details>, so it opens and closes without JS; this only
// shuts it once a link inside is followed (a same-page anchor would otherwise
// leave it open over the section), on Escape, and on a tap outside it.
const menu = document.querySelector("details.menu");
if (menu) {
  menu.addEventListener("click", (e) => { if (e.target.closest(".menu-panel a")) menu.open = false; });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && menu.open) { menu.open = false; menu.querySelector("summary").focus(); }
  });
  document.addEventListener("click", (e) => { if (menu.open && !menu.contains(e.target)) menu.open = false; });
}

// All-work page: category filter. Each card lists its categories in data-tags.
const filterBar = document.querySelector(".filters");
if (filterBar) {
  const buttons = filterBar.querySelectorAll("button");
  const cards = document.querySelectorAll("[data-filter-grid] .pcard");
  filterBar.addEventListener("click", (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;
    const f = btn.dataset.filter;
    buttons.forEach((b) => b.setAttribute("aria-pressed", String(b === btn)));
    cards.forEach((c) => { c.hidden = !(f === "all" || c.dataset.tags.split(" ").includes(f)); });
  });
}

// The tool row drifts only while it is visible, so it costs nothing once you
// scroll past it. Without JS it stays still, which is fine.
const stackRow = document.querySelector(".stack");
if (stackRow) {
  new IntersectionObserver(([e]) => stackRow.classList.toggle("on-screen", e.isIntersecting)).observe(stackRow);
}

// Fallback for browsers without speculation rules (Firefox, Safari): fetch a
// page into the HTTP cache when a visitor points at a link to it, so the click
// is served from cache. Same site only, each page once.
if (!(HTMLScriptElement.supports && HTMLScriptElement.supports("speculationrules"))) {
  const seen = new Set();
  const warm = (e) => {
    const a = e.target.closest && e.target.closest("a[href]");
    if (!a || a.target === "_blank" || a.origin !== location.origin || seen.has(a.pathname)) return;
    if (/\/(alisa-obby|drone)\//.test(a.pathname) || a.pathname === location.pathname) return;
    seen.add(a.pathname);
    fetch(a.href, { credentials: "same-origin" }).catch(() => {});
  };
  document.addEventListener("pointerover", warm, { passive: true });
  document.addEventListener("touchstart", warm, { passive: true });
}

// Service worker (sw.js): repeat visits and page changes load from the device.
// Once the page has settled, it hands over the links on this page so those
// pages are saved in the background.
if ("serviceWorker" in navigator && /^https?:$/.test(location.protocol)) {
  navigator.serviceWorker.register("/sw.js").catch(() => {});
  addEventListener("load", () => setTimeout(() => {
    const links = [...document.querySelectorAll("a[href]")]
      .filter((a) => a.origin === location.origin && a.target !== "_blank"
        && /\.html$|\/$/.test(a.pathname) && !/\/(alisa-obby|drone)\//.test(a.pathname))
      .map((a) => a.href.split("#")[0]);
    navigator.serviceWorker.ready.then((reg) => reg.active && reg.active.postMessage({ warm: [...new Set(links)] }));
  }, 3000));
}

// Back-to-top button: hidden until the reader is near the end of a long page.
// The link itself is a plain href="#", so it works without this script too.
const toTop = document.querySelector(".to-top");
if (toTop) {
  let queued = false;
  const check = () => {
    queued = false;
    const d = document.documentElement;
    const fromEnd = d.scrollHeight - (scrollY + innerHeight);
    toTop.classList.toggle("show", scrollY > innerHeight && fromEnd < innerHeight * 1.5);
  };
  addEventListener("scroll", () => { if (!queued) { queued = true; requestAnimationFrame(check); } }, { passive: true });
  addEventListener("resize", check);
  toTop.addEventListener("click", () => toTop.blur());
  check();
}
