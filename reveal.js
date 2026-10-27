// Fades sections in as they scroll into view. Without JS, everything is visible.
const io = new IntersectionObserver((entries) => {
  for (const e of entries) if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
}, { threshold: 0.12 });
document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

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

// A gentle 3D tilt, on the portrait only: it carries no text to read.
// Up to 5 degrees, mouse only, off for reduced motion.
if (matchMedia("(pointer: fine)").matches && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
  document.querySelectorAll("[data-tilt]").forEach((el) => {
    el.addEventListener("pointermove", (e) => {
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
      el.style.transform = `perspective(900px) rotateX(${(-y * 10).toFixed(2)}deg) rotateY(${(x * 10).toFixed(2)}deg)`;
    });
    el.addEventListener("pointerleave", () => { el.style.transform = ""; });
  });
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
