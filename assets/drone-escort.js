// Home page: the drone from work/drone/ flies down the page with the reader.
// It parks on the hero image, hovers beside each section heading as you scroll,
// and lands on the Telegram button in Contact. It moves like a quadcopter: a
// spring pulls it toward where the page wants it, it tilts into the
// acceleration, overshoots a little and settles. Click it to take it apart.
//
// three.js (600 KB) loads only after the page has finished loading, and only
// with motion allowed, data saver off and WebGL working. Everyone else gets the
// page exactly as it was. On phones the drone is smaller (SIZE, below).
(function () {
  const me = document.currentScript;
  const url = (p) => new URL(p, me ? me.src : location.href).href;
  const root = document.documentElement;

  if (!document.getElementById("contact")) return;
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
    .then(() => load(url("drone-model.js") + (me ? new URL(me.src).search : "")))
    .then(fly)
    .catch(() => { /* no drone, the page is unchanged */ });
  const idle = window.requestIdleCallback || ((f) => setTimeout(f, 800));
  const later = () => idle(start, { timeout: 4000 });
  if (document.readyState === "complete") later();
  else addEventListener("load", later, { once: true });

  function fly() {
    const THREE = window.THREE;
    // Canvas size in CSS px: smaller on smaller screens, fixed once loaded.
    const SIZE = innerWidth < 700 ? 170 : innerWidth < 1024 ? 260 : 440;
    const touch = matchMedia("(pointer: coarse)").matches;
    const rtl = root.dir === "rtl";
    // `say` is what the drone shouts when the reader scrolls too fast.
    // {s} is the section it just flew past, named as the nav names it.
    const TEXT = {
      en: { label: "Take the drone apart in 3D", tip: "Take me apart",
        say: ["Whoa, slow down! My props can't keep up.",
              "You just flew past {s}. Moustafa built that part for you to read.",
              "Turbulence! Ease off the scroll and see what Moustafa can do.",
              "Speeding detected. I'm writing you a ticket for skipping {s}."] },
      ar: { label: "فكّك الطائرة المسيّرة ثلاثية الأبعاد", tip: "فكّكني",
        say: ["مهلاً! مراوحي لا تلحق بك.",
              "مررت بقسم {s} بسرعة. كتبه مصطفى لتقرأه.",
              "مطبات هوائية! خفّف السرعة وشاهد ما يستطيع مصطفى فعله.",
              "تجاوزت السرعة المسموحة! هذه مخالفة لأنك تخطّيت {s}."] },
      ru: { label: "Разобрать дрон в 3D", tip: "Разбери меня",
        say: ["Тише! Мои винты за вами не успевают.",
              "Вы пролетели раздел «{s}». Мустафа писал его, чтобы его читали.",
              "Турбулентность! Сбавьте скорость и посмотрите, что умеет Мустафа.",
              "Превышение скорости! Выписываю штраф за пропущенный раздел «{s}»."] },
    }[(root.lang || "en").slice(0, 2)] || null;
    const text = TEXT || { label: "Take the drone apart in 3D", tip: "Take me apart", say: ["Whoa, slow down! My props can't keep up."] };

    /* scene: one small canvas that follows the drone, so the GPU only ever
       draws SIZE x SIZE px, never the whole page */
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
    renderer.setSize(SIZE, SIZE);
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

    // Everything below works in "foot" coordinates: the lowest pixel of the
    // drone as drawn. From a three-quarter view that is a front leg, not the
    // middle, so take the lowest projected corner of the bounding box.
    let footPx = 0;
    for (let i = 0; i < 8; i++) {
      const c = new THREE.Vector3(i & 1 ? bounds.max.x : bounds.min.x,
        i & 2 ? bounds.max.y : bounds.min.y, i & 4 ? bounds.max.z : bounds.min.z).project(camera);
      footPx = Math.max(footPx, (-c.y * 0.5 + 0.5) * SIZE);
    }
    const lift = footPx - SIZE / 2;      // body centre is this far above the feet

    const link = document.createElement("a");
    link.className = "drone-link";
    link.href = "work/drone.html";
    link.setAttribute("aria-label", text.label);
    link.dataset.tip = text.tip;
    const LW = Math.round(SIZE * 0.55), LH = Math.round(SIZE * 0.3);   // hit box over the body
    link.style.width = LW + "px"; link.style.height = LH + "px";
    // Speech bubble. Decorative, so screen readers are not interrupted by it.
    const bubble = document.createElement("div");
    bubble.className = "drone-say";
    bubble.setAttribute("aria-hidden", "true");
    const words = document.createElement("span");
    bubble.append(words);
    document.body.append(canvas, link, bubble);

    /* the flight path: one stop per section, measured from the live layout */
    const ids = ["work", "services", "skills", "security", "about", "contact"];
    let stops = [], keys = [];
    const BAND = 0.4;                    // stops sit 40% down the viewport
    function measure() {
      const sy = scrollY, H = innerHeight;
      const maxS = Math.max(0, root.scrollHeight - H);
      stops = [];
      // The hero art if it is shown, otherwise the hero block itself.
      const img = document.querySelector(".hero .stage3d img");
      const r = (img && img.offsetWidth && innerWidth >= 900 ? img : document.querySelector(".hero")).getBoundingClientRect();
      // Hover over the empty top corner of the hero image, body clear of the nav.
      stops.push({ x: rtl ? r.left + SIZE * 0.36 : r.right - SIZE * 0.36, y: r.top + sy + 70 + lift, land: "hero" });
      ids.forEach((id, i) => {
        const sec = document.getElementById(id);
        if (!sec) return;
        if (id === "contact") {
          // Land on the footer line, bottom corner: the end of the page is the
          // ground. There is not room above the contact card at full scroll.
          const ground = document.querySelector("footer") || sec;
          const rg = ground.getBoundingClientRect();
          stops.push({ x: rtl ? rg.left + 60 + SIZE * 0.45 : rg.right - 60 - SIZE * 0.45, y: rg.top + sy + 1, land: "contact" });
          return;
        }
        // Hover just above the heading, on the side the text does not reach.
        const h = sec.querySelector("h2") || sec;
        const rh = h.getBoundingClientRect(), rs = sec.getBoundingClientRect();
        const inset = SIZE * 0.55 + (i % 2) * Math.min(170, innerWidth * 0.12);   // weave: near the edge, then further in
        // On phones headings run the full width, so leave a bit more air under the legs.
        stops.push({ x: rtl ? rs.left + inset : rs.right - inset, y: rh.top + sy - 8 - (innerWidth < 700 ? 18 : 0) });
      });
      // The scroll position at which the drone should be at each stop.
      keys = stops.map((p, i) => (i === 0 ? 0 : Math.min(maxS, Math.max(0, p.y - BAND * H))));
      for (let i = keys.length - 2; i > 0; i--) keys[i] = Math.min(keys[i], keys[i + 1] - 40);
      for (let i = 1; i < keys.length; i++) keys[i] = Math.max(keys[i], keys[i - 1] + 1);
    }

    const smooth = (t) => t * t * (3 - 2 * t);
    const goal = { x: 0, y: 0, land: null };
    let leg = 0;                         // index of the stop the drone last left
    function target(s) {
      const n = stops.length - 1;
      if (s <= keys[0]) return set(stops[0].x, stops[0].y, stops[0].land);
      if (s >= keys[n]) return set(stops[n].x, stops[n].y, stops[n].land);
      let i = 0;
      while (s >= keys[i + 1]) i++;
      leg = i;
      const t = (s - keys[i]) / (keys[i + 1] - keys[i]);
      const a = stops[i], b = stops[i + 1];
      return set(a.x + (b.x - a.x) * smooth(t), a.y + (b.y - a.y) * t - Math.sin(Math.PI * t) * SIZE * 0.16, null);
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
      // Real elapsed time, integrated in small steps, so a slow frame rate
      // makes the motion choppier but never slower.
      const dt = Math.min((now - clock) / 1000, 0.25); clock = now; t += dt;

      target(scrollY);
      let landed = false, parked = false;
      for (let left = dt; left > 1e-6; left -= 1 / 120) {
        const h = Math.min(left, 1 / 120);
        const dx = goal.x - p.x, dy = goal.y - p.y;
        const near = Math.hypot(dx, dy) < 4 && Math.hypot(v.x, v.y) < 25;
        landed = goal.land === "contact" && near;
        parked = goal.land === "hero" && near;
        // On the ground the motors stop; it has to spin up before it can move again.
        thrust += ((landed ? 0 : 1) - thrust) * Math.min(1, h * (landed ? 1.5 : 3));
        const ax = (dx * K) * thrust - v.x * C, ay = (dy * K) * thrust - v.y * C;
        v.x += ax * h; v.y += ay * h;
        p.x += v.x * h; p.y += v.y * h;
        acc.x += (ax - acc.x) * Math.min(1, h * 8);
        acc.y += (ay - acc.y) * Math.min(1, h * 8);
      }

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
      link.style.transform = `translate(${(sx - LW / 2).toFixed(1)}px, ${(sy - lift - LH / 2).toFixed(1)}px)`;

      // Too fast? A flick of the wheel reads at 3,000+ px/s; reading is under 1,500.
      // Thumbs flick much faster than wheels, so phones need a higher bar.
      speed += (Math.abs(scrollY - lastY) / Math.max(dt, 1e-3) - speed) * Math.min(1, dt * 6);
      lastY = scrollY;
      // A link jump stays exempt until the page has actually stopped moving.
      if (now < jumpUntil && speed > 150) jumpUntil = now + 400;
      if (speed > (touch ? 7000 : 3000) && !jumping() && now - saidAt > 12000 && said < 4) shout(now);
      if (bubble.classList.contains("on")) {
        // Long enough to read: 5 s, plus a little per character for the long lines.
        if (now - saidAt > Math.max(5000, 2500 + words.textContent.length * 60)) bubble.classList.remove("on");
        // Above the body, kept below the sticky nav.
        const top = Math.max(96 + words.offsetHeight, sy - lift - SIZE * 0.16);
        bubble.style.transform = `translate(${sx.toFixed(1)}px, ${top.toFixed(1)}px)`;
      }
      if (onScreen) renderer.render(scene, camera);
      requestAnimationFrame(frame);
    }

    /* "slow down" bubble */
    let speed = 0, lastY = scrollY, saidAt = -1e9, said = 0, jumpUntil = 0, line = 0;
    // Clicking a menu link or back-to-top scrolls fast on purpose: no telling off.
    const jumping = () => performance.now() < jumpUntil;
    document.addEventListener("click", (e) => {
      const a = e.target.closest && e.target.closest("a[href*='#']");
      if (a) jumpUntil = performance.now() + 2500;
    });
    function shout(now) {
      const n = Math.max(1, Math.min(leg, ids.length)) - 1;   // stop k is section k-1
      const nav = document.querySelector(`.links a[href$="#${ids[n]}"]`);
      const name = (nav && nav.textContent.trim()) || ids[n];
      words.textContent = text.say[line++ % text.say.length].replace("{s}", name);
      bubble.classList.add("on");
      saidAt = now; said++; wobble = 0.7;
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
