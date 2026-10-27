// Home page: the drone from work/drone/ flies down the page with the reader.
// It parks on the hero image, hovers beside each section heading as you scroll,
// and lands on the Telegram button in Contact. It moves like a quadcopter: a
// spring pulls it toward where the page wants it, it tilts into the
// acceleration, overshoots a little and settles. Click it to take it apart.
//
// three.js (600 KB) loads only after the page has finished loading, and only on
// a desktop-size screen with a mouse, with motion allowed and data saver off.
// Everyone else gets the page exactly as it was.
(function () {
  const me = document.currentScript;
  const url = (p) => new URL(p, me ? me.src : location.href).href;
  const root = document.documentElement;

  if (!document.getElementById("contact")) return;
  if (!matchMedia("(min-width: 1024px) and (hover: hover) and (pointer: fine)").matches) return;
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (navigator.connection && navigator.connection.saveData) return;
  try {
    const c = document.createElement("canvas");
    if (!(c.getContext("webgl2") || c.getContext("webgl"))) return;
  } catch (e) { return; }

  const load = (src) => new Promise((ok, fail) => {
    const s = document.createElement("script");
    s.src = src; s.onload = ok; s.onerror = fail;
    document.head.appendChild(s);
  });
  const start = () => load(url("vendor/three.min.js"))
    .then(() => load(url("drone-model.js")))
    .then(fly)
    .catch(() => { /* no drone, the page is unchanged */ });
  const idle = window.requestIdleCallback || ((f) => setTimeout(f, 800));
  const later = () => idle(start, { timeout: 4000 });
  if (document.readyState === "complete") later();
  else addEventListener("load", later, { once: true });

  function fly() {
    const THREE = window.THREE;
    const SIZE = 220;                 // canvas, CSS px
    const rtl = root.dir === "rtl";
    const TEXT = {
      en: { label: "Take the drone apart in 3D", tip: "Take me apart" },
      ar: { label: "فكّك الطائرة المسيّرة ثلاثية الأبعاد", tip: "فكّكني" },
      ru: { label: "Разобрать дрон в 3D", tip: "Разбери меня" },
    }[(root.lang || "en").slice(0, 2)] || null;
    const text = TEXT || { label: "Take the drone apart in 3D", tip: "Take me apart" };

    /* scene: one small canvas that follows the drone, so the GPU only ever
       draws 220x220 px, never the whole page */
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.setSize(SIZE, SIZE, false);
    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.1;
    const canvas = renderer.domElement;
    canvas.className = "drone-canvas";
    canvas.setAttribute("aria-hidden", "true");

    const scene = new THREE.Scene();
    scene.add(new THREE.HemisphereLight(0xffffff, 0x9aa3ab, 0.85));
    const key = new THREE.DirectionalLight(0xffffff, 1.6); key.position.set(4, 8, 5); scene.add(key);
    const rim = new THREE.DirectionalLight(0xdfe8ff, 0.9); rim.position.set(-6, 3, -5); scene.add(rim);

    const drone = DroneModel.build(THREE, { textureUrl: url("../work/drone/mai-logo.png"), segments: 24 });
    const body = new THREE.Group();     // yaw, pitch and roll live here
    body.rotation.order = "YXZ";
    body.add(drone.group);
    scene.add(body);

    const bounds = new THREE.Box3().setFromObject(drone.group);
    const sphere = bounds.getBoundingSphere(new THREE.Sphere());
    const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
    const dist = (sphere.radius / Math.sin((camera.fov * Math.PI / 180) / 2)) * 1.12;
    camera.position.copy(sphere.center).addScaledVector(new THREE.Vector3(0.62, 0.62, 0.8).normalize(), dist);
    camera.lookAt(sphere.center);
    camera.updateMatrixWorld();

    // Everything below works in "foot" coordinates: the point under the
    // landing legs. Where that pixel sits inside the canvas is fixed.
    const foot = new THREE.Vector3(0, bounds.min.y, 0).project(camera);
    const footPx = (-foot.y * 0.5 + 0.5) * SIZE;
    const lift = footPx - SIZE / 2;      // body centre is this far above the feet

    const link = document.createElement("a");
    link.className = "drone-link";
    link.href = "work/drone.html";
    link.setAttribute("aria-label", text.label);
    link.dataset.tip = text.tip;
    document.body.append(canvas, link);

    /* the flight path: one stop per section, measured from the live layout */
    const ids = ["work", "services", "skills", "security", "about", "contact"];
    let stops = [], keys = [];
    const BAND = 0.4;                    // stops sit 40% down the viewport
    function measure() {
      const sy = scrollY, H = innerHeight;
      const maxS = Math.max(0, root.scrollHeight - H);
      stops = [];
      const img = document.querySelector(".hero .stage3d img") || document.querySelector(".hero");
      const r = img.getBoundingClientRect();
      stops.push({ x: rtl ? r.left + 80 : r.right - 80, y: r.top + sy + 24, land: "hero" });
      ids.forEach((id, i) => {
        const sec = document.getElementById(id);
        if (!sec) return;
        if (id === "contact") {
          const b = sec.querySelector(".btn-primary") || sec.querySelector("h2");
          const rb = b.getBoundingClientRect();
          stops.push({ x: rtl ? rb.left + 70 : rb.right - 70, y: rb.top + sy, land: "contact" });
          return;
        }
        const h = sec.querySelector("h2") || sec;
        const rh = h.getBoundingClientRect(), rs = sec.getBoundingClientRect();
        const inset = 140 + (i % 2) * 190;      // weave: near the edge, then further in
        stops.push({ x: rtl ? rs.left + inset : rs.right - inset, y: rh.top + sy + rh.height / 2 + lift });
      });
      // The scroll position at which the drone should be at each stop.
      keys = stops.map((p, i) => (i === 0 ? 0 : Math.min(maxS, Math.max(0, p.y - BAND * H))));
      for (let i = keys.length - 2; i > 0; i--) keys[i] = Math.min(keys[i], keys[i + 1] - 40);
      for (let i = 1; i < keys.length; i++) keys[i] = Math.max(keys[i], keys[i - 1] + 1);
    }

    const smooth = (t) => t * t * (3 - 2 * t);
    const goal = { x: 0, y: 0, land: null };
    function target(s) {
      const n = stops.length - 1;
      if (s <= keys[0]) return set(stops[0].x, stops[0].y, stops[0].land);
      if (s >= keys[n]) return set(stops[n].x, stops[n].y, stops[n].land);
      let i = 0;
      while (s >= keys[i + 1]) i++;
      const t = (s - keys[i]) / (keys[i + 1] - keys[i]);
      const a = stops[i], b = stops[i + 1];
      return set(a.x + (b.x - a.x) * smooth(t), a.y + (b.y - a.y) * t - Math.sin(Math.PI * t) * 70, null);
    }
    function set(x, y, land) { goal.x = x; goal.y = y; goal.land = land; return goal; }

    /* flight state, in page coordinates */
    measure();
    target(scrollY);
    const p = { x: goal.x + (rtl ? -260 : 260), y: goal.y - 320 };   // swoops in from above
    const v = { x: 0, y: 0 }, acc = { x: 0, y: 0 };
    let thrust = 1, rpm = 30, wobble = 0, clock = performance.now(), t = 0;

    const K = 34, C = 2 * Math.sqrt(K) * 0.6;       // under-damped: it overshoots a little
    const clamp = (x, m) => Math.max(-m, Math.min(m, x));

    function frame(now) {
      const dt = Math.min((now - clock) / 1000, 0.05); clock = now; t += dt;
      if (innerWidth < 1024) { canvas.hidden = link.hidden = true; return requestAnimationFrame(frame); }
      canvas.hidden = link.hidden = false;

      target(scrollY);
      const dx = goal.x - p.x, dy = goal.y - p.y;
      const near = Math.hypot(dx, dy) < 4 && Math.hypot(v.x, v.y) < 25;
      const landed = goal.land === "contact" && near;
      const parked = goal.land === "hero" && near;
      // On the ground the motors stop; it has to spin up before it can move again.
      thrust += ((landed ? 0 : 1) - thrust) * Math.min(1, dt * (landed ? 1.5 : 3));
      const ax = (dx * K) * thrust - v.x * C, ay = (dy * K) * thrust - v.y * C;
      v.x += ax * dt; v.y += ay * dt;
      p.x += v.x * dt; p.y += v.y * dt;
      acc.x += (ax - acc.x) * Math.min(1, dt * 8);
      acc.y += (ay - acc.y) * Math.min(1, dt * 8);

      // A quadcopter accelerates by tilting its thrust: lean into the move.
      wobble = Math.max(0, wobble - dt);
      const roll = clamp(-(acc.x * 0.00004 + v.x * 0.00035), 0.45) + Math.sin(wobble * 26) * 0.25 * (wobble / 0.7);
      const pitch = clamp(acc.y * 0.00003 + v.y * 0.00025, 0.4);
      body.rotation.z += (roll - body.rotation.z) * Math.min(1, dt * 10);
      body.rotation.x += (pitch - body.rotation.x) * Math.min(1, dt * 10);
      body.rotation.y += (clamp(v.x * 0.0007, 0.6) - body.rotation.y) * Math.min(1, dt * 3);
      body.position.y = (landed || parked) ? 0 : Math.sin(t * 2.2) * 0.05;

      const want = landed ? 0 : parked ? 9 : 30 + Math.min(14, Math.max(0, -v.y * 0.02));
      rpm += (want - rpm) * Math.min(1, dt * (want < rpm ? 1.2 : 4));
      drone.props.forEach((pr) => { pr.rot.rotation.y += pr.dirSign * rpm * dt; });
      drone.blink(dt);

      const sx = p.x - scrollX, sy = p.y - scrollY;
      const onScreen = sy > -SIZE && sy < innerHeight + SIZE;
      canvas.style.transform = `translate(${(sx - SIZE / 2).toFixed(1)}px, ${(sy - footPx).toFixed(1)}px)`;
      link.style.transform = `translate(${(sx - 60).toFixed(1)}px, ${(sy - lift - 32).toFixed(1)}px)`;
      if (onScreen) renderer.render(scene, camera);
      requestAnimationFrame(frame);
    }

    link.addEventListener("pointerenter", () => { wobble = 0.7; });
    link.addEventListener("focus", () => { wobble = 0.7; });

    // Layout moves when fonts, images or the window change: re-measure.
    let queued = false;
    const remeasure = () => { if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; measure(); }); } };
    addEventListener("resize", remeasure);
    if (window.ResizeObserver) new ResizeObserver(remeasure).observe(document.body);
    if (document.fonts) document.fonts.ready.then(remeasure);

    requestAnimationFrame((now) => { clock = now; canvas.classList.add("in"); frame(now); });
  }
})();
