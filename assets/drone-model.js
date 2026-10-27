// The drone from work/drone/, as a model other pages can build. Same parts,
// same sizes, same base/offset vectors as the viewer, so an exploded pose here
// matches the one there. The viewer still carries its own inline copy.
//
//   const d = DroneModel.build(THREE, { textureUrl, segments: 24 });
//   scene.add(d.group);  d.props[i].rot.rotation.y += ...;  d.blink(dt);
window.DroneModel = (function () {
  function build(THREE, opts) {
    opts = opts || {};
    const seg = opts.segments || 56;            // cylinder detail; lower for small renders
    const shadows = !!opts.shadows;
    const lin = (hex) => new THREE.Color(hex).convertSRGBToLinear();

    const M = {
      shell: new THREE.MeshStandardMaterial({ color: lin(0x3b424b), roughness: .45, metalness: .15 }),
      shellDark: new THREE.MeshStandardMaterial({ color: lin(0x262b32), roughness: .55 }),
      black: new THREE.MeshStandardMaterial({ color: 0x202326, roughness: .5, metalness: .2 }),
      metal: new THREE.MeshStandardMaterial({ color: lin(0xb9c1c9), roughness: .25, metalness: .9 }),
      copper: new THREE.MeshStandardMaterial({ color: 0xb87333, roughness: .35, metalness: .9 }),
      pcb: new THREE.MeshStandardMaterial({ color: 0x1d4f3a, roughness: .55 }),
      pcbBlue: new THREE.MeshStandardMaterial({ color: 0x1d3550, roughness: .55 }),
      chip: new THREE.MeshStandardMaterial({ color: 0x151719, roughness: .4 }),
      gold: new THREE.MeshStandardMaterial({ color: 0xd4a64a, roughness: .3, metalness: .9 }),
      tip: new THREE.MeshStandardMaterial({ color: lin(0xa855f7), roughness: .4 }),
      lens: new THREE.MeshStandardMaterial({ color: 0x0b1a2a, roughness: .05, metalness: .6 }),
      battery: new THREE.MeshStandardMaterial({ color: lin(0x565e69), roughness: .45 }),
      led: new THREE.MeshStandardMaterial({ color: 0x58d68d, emissive: 0x2ecc71, emissiveIntensity: .8 }),
      wire: new THREE.MeshStandardMaterial({ color: 0xc0392b, roughness: .6 }),
      wire2: new THREE.MeshStandardMaterial({ color: 0x222222, roughness: .6 }),
      navG: new THREE.MeshStandardMaterial({ color: 0x0b1a12, emissive: lin(0x19ff86), emissiveIntensity: 2.2, roughness: .3 }),
      navR: new THREE.MeshStandardMaterial({ color: 0x1a0b0b, emissive: lin(0xff2d55), emissiveIntensity: 2.2, roughness: .3 }),
      navW: new THREE.MeshStandardMaterial({ color: 0x151719, emissive: lin(0xc9b7ff), emissiveIntensity: 2.6, roughness: .3 }),
    };
    if (opts.textureUrl) {
      const t = new THREE.TextureLoader().load(opts.textureUrl);
      t.encoding = THREE.sRGBEncoding; t.anisotropy = 4;
      M.mai = new THREE.MeshStandardMaterial({ map: t, transparent: true, roughness: .5, metalness: 0, depthWrite: false });
    }

    function mesh(g, m) { const o = new THREE.Mesh(g, m); o.castShadow = shadows; o.receiveShadow = shadows; return o; }
    function box(w, h, d, m) { return mesh(new THREE.BoxGeometry(w, h, d), m); }
    function cyl(rt, rb, h, m, s) { return mesh(new THREE.CylinderGeometry(rt, rb, h, Math.min(s || 56, seg)), m); }
    function roundedSlab(w, d, h, r, mat) {
      const s = new THREE.Shape(), x = -w / 2, y = -d / 2;
      s.moveTo(x + r, y); s.lineTo(x + w - r, y); s.quadraticCurveTo(x + w, y, x + w, y + r);
      s.lineTo(x + w, y + d - r); s.quadraticCurveTo(x + w, y + d, x + w - r, y + d);
      s.lineTo(x + r, y + d); s.quadraticCurveTo(x, y + d, x, y + d - r);
      s.lineTo(x, y + r); s.quadraticCurveTo(x, y, x + r, y);
      const bev = Math.min(h * 0.35, 0.06);
      const g = new THREE.ExtrudeGeometry(s, { depth: h - bev * 2, bevelEnabled: true, bevelThickness: bev,
        bevelSize: bev, bevelSegments: seg < 56 ? 4 : 10, curveSegments: seg < 56 ? 12 : 32 });
      g.translate(0, 0, -(h - bev * 2) / 2); g.rotateX(-Math.PI / 2);
      return mesh(g, mat);
    }

    const root = new THREE.Group();
    const parts = [], props = [], navLights = [];
    function addPart(name, base, offset, fill) {
      const g = new THREE.Group();
      fill(g);
      g.position.set(...base);
      root.add(g);
      parts.push({ name, group: g, base: new THREE.Vector3(...base), offset: new THREE.Vector3(...offset) });
      return g;
    }
    function navLight(parent, mat, pos, r) {
      const m = new THREE.Mesh(new THREE.SphereGeometry(r || 0.055, 16, 12), mat);
      m.position.set(...pos); parent.add(m);
      navLights.push({ mesh: m, base: mat.emissiveIntensity, strobe: mat === M.navW });
    }

    /* main frame / lower shell */
    addPart('Main frame', [0, 0, 0], [0, 0, 0], g => {
      g.add(roundedSlab(1.5, 2.3, 0.34, 0.32, M.shell));
      const vent = box(0.9, 0.02, 0.5, M.shellDark); vent.position.set(0, -0.17, 0.1); g.add(vent);
      [-0.35, 0.35].forEach(x => { const s = cyl(0.075, 0.075, 0.05, M.lens, 24); s.rotation.x = Math.PI / 2; s.position.set(x, 0.02, 1.16); g.add(s); });
      [[1, 1], [-1, 1], [1, -1], [-1, -1]].forEach(([sx, sz]) => { const h = cyl(0.11, 0.11, 0.3, M.shellDark, 20); h.position.set(sx * 0.68, 0, sz * 0.95); g.add(h); });
    });

    /* ESC board */
    addPart('ESC board', [0, 0.2, 0.15], [0, 0.85, 0], g => {
      g.add(box(1.05, 0.035, 1.1, M.pcbBlue));
      for (let i = 0; i < 4; i++) { const c = box(0.16, 0.05, 0.16, M.chip); c.position.set(i % 2 ? 0.3 : -0.3, 0.04, i < 2 ? 0.3 : -0.3); g.add(c); }
      for (let i = 0; i < 8; i++) { const c = box(0.05, 0.04, 0.09, M.metal); c.position.set(-0.42 + i * 0.12, 0.035, -0.47); g.add(c); }
      const w1 = cyl(0.025, 0.025, 0.6, M.wire, 10); w1.rotation.x = Math.PI / 2; w1.position.set(0.1, 0.02, -0.8); g.add(w1);
      const w2 = cyl(0.025, 0.025, 0.6, M.wire2, 10); w2.rotation.x = Math.PI / 2; w2.position.set(-0.1, 0.02, -0.8); g.add(w2);
    });

    /* flight controller */
    addPart('Flight controller', [0, 0.28, 0.15], [0, 1.6, 0], g => {
      g.add(box(0.95, 0.035, 1.0, M.pcb));
      const soc = box(0.3, 0.05, 0.3, M.chip); soc.position.set(0, 0.04, 0.05); g.add(soc);
      const imu = box(0.12, 0.04, 0.12, M.chip); imu.position.set(0.3, 0.035, -0.25); g.add(imu);
      const sh = box(0.32, 0.06, 0.22, M.metal); sh.position.set(-0.24, 0.045, -0.25); g.add(sh);
      const led = box(0.04, 0.03, 0.04, M.led); led.position.set(0.38, 0.04, 0.38); g.add(led);
      for (let i = 0; i < 6; i++) { const p = box(0.03, 0.02, 0.07, M.gold); p.position.set(-0.4 + i * 0.07, 0.03, 0.43); g.add(p); }
    });

    /* GPS */
    addPart('GPS + compass', [0, 0.38, 0.35], [0, 2.3, 0], g => {
      g.add(box(0.48, 0.06, 0.48, M.pcb));
      const ant = box(0.34, 0.06, 0.34, M.gold); ant.position.y = 0.06; g.add(ant);
      const cer = box(0.26, 0.04, 0.26, M.shellDark); cer.position.y = 0.1; g.add(cer);
    });

    /* top cover, MAI badge, navigation lights */
    addPart('Top cover', [0, 0.38, 0], [0, 3.05, 0], g => {
      g.add(roundedSlab(1.42, 2.2, 0.2, 0.3, M.shell));
      const ridge = roundedSlab(0.8, 1.3, 0.06, 0.2, M.shellDark); ridge.position.y = 0.11; g.add(ridge);
      const l = box(0.14, 0.02, 0.04, M.led); l.position.set(0, 0.12, -0.9); g.add(l);
      if (M.mai) {
        const badge = new THREE.Mesh(new THREE.PlaneGeometry(0.52, 0.52), M.mai);
        badge.rotation.x = -Math.PI / 2; badge.position.set(0, 0.1425, 0.12); g.add(badge);
      }
      [[0.56, 0.86], [0.56, -0.86], [-0.56, 0.86], [-0.56, -0.86]].forEach(([x, z]) => {
        navLight(g, x > 0 ? M.navG : M.navR, [x, 0.105, z], 0.055);
      });
    });

    addPart('_strobe', [0, 0, 0], [0, 0, 0], g => { navLight(g, M.navW, [0, -0.02, 1.12], 0.045); });

    /* battery */
    addPart('Battery', [0, 0.12, -1.05], [0, 0.15, -2.2], g => {
      g.add(roundedSlab(0.95, 0.75, 0.36, 0.12, M.battery));
      for (let i = 0; i < 4; i++) { const d = box(0.1, 0.02, 0.04, i < 3 ? M.led : M.shellDark); d.position.set(-0.2 + i * 0.13, 0.19, -0.25); g.add(d); }
      const grip = box(0.5, 0.03, 0.08, M.shellDark); grip.position.set(0, 0.19, 0.15); g.add(grip);
    });

    /* gimbal + camera */
    addPart('Gimbal camera', [0, -0.18, 1.25], [0, -0.25, 1.7], g => {
      const yoke = box(0.5, 0.08, 0.12, M.black); yoke.position.y = 0.12; g.add(yoke);
      [-0.22, 0.22].forEach(x => { const s = box(0.06, 0.24, 0.12, M.black); s.position.set(x, 0, 0); g.add(s); });
      const cam = roundedSlab(0.36, 0.32, 0.3, 0.1, M.black); cam.position.set(0, -0.02, 0.03); g.add(cam);
      const lens = cyl(0.11, 0.12, 0.08, M.metal, 32); lens.rotation.x = Math.PI / 2; lens.position.set(0, -0.02, 0.22); g.add(lens);
      const glass = cyl(0.085, 0.085, 0.02, M.lens, 32); glass.rotation.x = Math.PI / 2; glass.position.set(0, -0.02, 0.27); g.add(glass);
    });

    /* arms, motors, props */
    [[1, 1], [-1, 1], [1, -1], [-1, -1]].forEach(([sx, sz], i) => {
      const A = new THREE.Vector3(sx * 0.68, 0, sz * 0.95);
      const dir = new THREE.Vector3(sx * 1, 0, sz * 0.72).normalize();
      const L = 1.55;
      const tip = A.clone().addScaledVector(dir, L);
      const ang = Math.atan2(-dir.z, dir.x);

      addPart(i === 0 ? 'Folding arms' : '_arm' + i, [A.x, A.y, A.z], [dir.x * 0.55, 0, dir.z * 0.55], g => {
        const arm = box(L, 0.11, 0.17, M.shell); arm.position.copy(dir.clone().multiplyScalar(L / 2)); arm.rotation.y = ang; g.add(arm);
        if (sz > 0) { const leg = box(0.08, 0.42, 0.1, M.shell); leg.position.copy(dir.clone().multiplyScalar(L - 0.05)); leg.position.y = -0.3; leg.rotation.y = ang; g.add(leg); }
        else { const leg = box(0.08, 0.38, 0.1, M.shellDark); leg.position.copy(dir.clone().multiplyScalar(L * 0.55)); leg.position.y = -0.24; leg.rotation.y = ang; g.add(leg); }
      });

      addPart(i === 0 ? 'Brushless motors' : '_motor' + i, [tip.x, 0.12, tip.z], [dir.x * 1.2, 0.45, dir.z * 1.2], g => {
        g.add(cyl(0.17, 0.17, 0.2, M.black, 56));
        const ring = cyl(0.175, 0.175, 0.05, M.copper, 56); ring.position.y = -0.05; g.add(ring);
        const cap = cyl(0.06, 0.08, 0.06, M.metal, 40); cap.position.y = 0.13; g.add(cap);
      });

      addPart(i === 0 ? 'Propellers' : '_prop' + i, [tip.x, 0.29, tip.z], [dir.x * 1.5, 1.3, dir.z * 1.5], g => {
        const rot = new THREE.Group(); g.add(rot);
        rot.add(cyl(0.07, 0.07, 0.06, M.black, 40));
        const sign = sx * sz > 0 ? 1 : -1;
        [0, Math.PI].forEach(a => {
          const bl = new THREE.Group(); bl.rotation.y = a;
          const blade = box(0.62, 0.018, 0.12, M.black); blade.position.x = 0.36; blade.rotation.x = sign * 0.18; bl.add(blade);
          const t = box(0.1, 0.02, 0.12, M.tip); t.position.x = 0.65; t.rotation.x = blade.rotation.x; bl.add(t);
          rot.add(bl);
        });
        props.push({ rot, dirSign: sign });
      });
    });

    // Navigation lights: wingtips blink together, the white strobe double-flashes.
    let navT = 0;
    function blink(dt) {
      navT += dt;
      const arm = Math.sin(navT * Math.PI * 2 * 1.1) > -0.2 ? 1 : 0.06;
      const ph = navT % 1.6;
      const strobe = (ph < 0.07 || (ph > 0.17 && ph < 0.24)) ? 1 : 0.04;
      navLights.forEach(n => { n.mesh.material.emissiveIntensity = n.base * (n.strobe ? strobe : arm); });
    }

    // 0 = assembled, 1 = fully exploded.
    function explode(k) { parts.forEach(p => p.group.position.copy(p.base).addScaledVector(p.offset, k)); }

    return { group: root, parts, props, navLights, blink, explode };
  }
  return { build };
})();
