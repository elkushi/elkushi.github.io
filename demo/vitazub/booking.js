/* Онлайн-запись — демо для «Стоматологии на Страстном» (Moustafa, 2026-11-16).
   Окно «C · три поля» из шаблона «Вилла Дентос»: любая кнопка «Записаться» открывает его поверх
   страницы, на телефоне — панелью снизу. Карточка в первом экране показывает ближайшее время
   терапевта, и каждое время открывает окно уже выбранным.
   Ничего не сохраняет и никуда не отправляет. Услуги, цены и врачи — с сайта клиники (прайс и
   страница врачей); свободное время придумано. Часы — Пн–Пт 9:00–20:00, как на странице «Контакты». */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var pop = $("zp-pop"), scrim = $("zp-scrim");
  if (!pop || !scrim) { return; }

  // [id, название, цена из прайса, врачи (пусто = все)]
  var SERVICES = [
    ["cons", "Консультация", "от 3 000 ₽", []],
    ["ter", "Лечение кариеса", "пломба 9 100 ₽", ["shad"]],
    ["impl", "Имплантация", "имплантат 78 000 ₽", ["ruz"]],
    ["udal", "Удаление зуба", "", ["ruz"]],
    ["prot", "Коронки и виниры", "коронка от 27 600 ₽", ["lop"]],
    ["gig", "Гигиена AIR-FLOW", "2 200 ₽ за сегмент", ["bus"]],
    ["otb", "Отбеливание", "от 8 000 ₽", ["bus"]],
    ["par", "Лечение дёсен, Vector", "24 000 ₽", ["ruz", "shad"]],
    ["kt", "КТ, 3D-снимок", "3 000 ₽", ["bus"]]
  ];
  var DOCTORS = [
    ["any", "Любой свободный"],
    ["lop", "Лопаева О. Ж."],
    ["ruz", "Рузняев А. В."],
    ["shad", "Шадунц А. Г."],
    ["bus", "Бусурова Т."]
  ];
  var OPEN = 9, CLOSE = 20, NDAYS = 7;            // Пн–Пт 09:00–20:00
  var WD = ["вс", "пн", "вт", "ср", "чт", "пт", "сб"];
  var MON = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа",
             "сентября", "октября", "ноября", "декабря"];

  var st = { s: "cons", d: "any", day: null, t: null, all: false }, opener = null;

  // Ближайшие рабочие дни (суббота и воскресенье пропускаются).
  function days() {
    var out = [], d = new Date(); d.setHours(0, 0, 0, 0);
    while (out.length < NDAYS) {
      if (d.getDay() !== 0 && d.getDay() !== 6) { out.push(new Date(d.getTime())); }
      d = new Date(d.getTime() + 86400000); d.setHours(0, 0, 0, 0);
    }
    return out;
  }
  function rel(d) {
    var t = new Date(); t.setHours(0, 0, 0, 0);
    return Math.round((d.getTime() - t.getTime()) / 86400000);
  }
  function dayName(d) {
    var dm = d.getDate() + " " + MON[d.getMonth()], r = rel(d);
    return r === 0 ? "сегодня, " + dm : r === 1 ? "завтра, " + dm : WD[d.getDay()] + ", " + dm;
  }
  function dayShort(d) {
    var r = rel(d);
    return r === 0 ? "сегодня" : r === 1 ? "завтра" : WD[d.getDay()] + ", " + d.getDate() + " " + MON[d.getMonth()];
  }

  // Занятость — по постоянному правилу, а не случайно: время не «прыгает», если вернуться к дню.
  function busy(d, h, half, doc) {
    var k = d.getDate() + d.getMonth() * 31;
    var seed = k * 97 + h * 13 + (half ? 7 : 0) + doc.charCodeAt(0) * 31 + doc.charCodeAt(1) * 17;
    return (seed * 2654435761 % 100) < 45;
  }
  function docsFor(s) {
    var only = SERVICES.filter(function (x) { return x[0] === s; })[0][3];
    return DOCTORS.filter(function (d) { return d[0] === "any" || !only.length || only.indexOf(d[0]) >= 0; });
  }
  function freeFor(svc, doc, d) {
    var out = [], now = Date.now(), real = docsFor(svc).filter(function (x) { return x[0] !== "any"; });
    for (var h = OPEN; h < CLOSE; h++) {
      for (var half = 0; half < 2; half++) {
        var when = new Date(d.getTime()); when.setHours(h, half ? 30 : 0, 0, 0);
        if (when.getTime() < now + 2 * 3600000) { continue; }
        var ok = doc === "any"
          ? real.some(function (x) { return !busy(d, h, half, x[0]); })
          : !busy(d, h, half, doc);
        if (ok) { out.push(("0" + h).slice(-2) + ":" + (half ? "30" : "00")); }
      }
    }
    return out;
  }
  function free(i) { return freeFor(st.s, st.d, days()[i]); }
  function fill(sel, items, val) {
    sel.textContent = "";
    items.forEach(function (it) { var o = document.createElement("option"); o.value = it[0]; o.textContent = it[1]; sel.appendChild(o); });
    sel.value = val;
  }

  function render() {
    var docs = docsFor(st.s);
    if (!docs.some(function (d) { return d[0] === st.d; })) { st.d = "any"; }
    var ds = days();
    if (st.day === null) {
      st.day = 0;
      while (st.day < ds.length - 1 && !free(st.day).length) { st.day++; }
    }
    var f = free(st.day);
    if (f.indexOf(st.t) < 0) { st.t = f[0] || null; }
    if (f.indexOf(st.t) > 3) { st.all = true; }

    fill($("zp-svc"), SERVICES.map(function (s) { return [s[0], s[1] + (s[2] ? " · " + s[2] : "")]; }), st.s);
    fill($("zp-doc"), docs.map(function (d) { return [d[0], d[1]]; }), st.d);
    fill($("zp-day"), ds.map(function (d, i) { return [String(i), dayName(d) + (free(i).length ? "" : " · мест нет")]; }), String(st.day));

    var box = $("zp-times"); box.textContent = "";
    if (!f.length) {
      var n = document.createElement("p"); n.className = "zp-none";
      n.textContent = "В этот день свободного времени нет — выберите другой день.";
      box.appendChild(n);
    }
    (st.all ? f : f.slice(0, 4)).forEach(function (t) {
      var b = document.createElement("button");
      b.type = "button"; b.className = "zp-t"; b.textContent = t;
      b.setAttribute("aria-pressed", t === st.t ? "true" : "false");
      b.onclick = function () { st.t = t; render(); };
      box.appendChild(b);
    });
    if (f.length > 4) {
      var m = document.createElement("button");
      m.type = "button"; m.className = "zp-more";
      m.textContent = st.all ? "Показать меньше" : "Другое время · ещё " + (f.length - 4);
      m.onclick = function () { st.all = !st.all; render(); };
      box.appendChild(m);
    }
    var go = $("zp-go");
    go.disabled = !st.t;
    go.textContent = st.t ? "Записаться на " + dayShort(ds[st.day]) + ", " + st.t : "Выберите другой день";
  }

  $("zp-svc").onchange = function () { st.s = this.value; st.t = null; st.all = false; render(); };
  $("zp-doc").onchange = function () { st.d = this.value; st.t = null; st.all = false; render(); };
  $("zp-day").onchange = function () { st.day = +this.value; st.t = null; st.all = false; render(); };

  $("zp-go").onclick = function () {
    var ds = days(), svc = SERVICES.filter(function (s) { return s[0] === st.s; })[0][1];
    var doc = DOCTORS.filter(function (d) { return d[0] === st.d; })[0][1];
    $("zp-done-text").textContent = svc + " · " + doc + " · " + dayName(ds[st.day]) + ", " + st.t;
    $("zp-form").hidden = true; $("zp-done").hidden = false;
    $("zp-again").focus();
  };
  $("zp-again").onclick = function () {
    $("zp-done").hidden = true; $("zp-form").hidden = false;
    st = { s: "cons", d: "any", day: null, t: null, all: false }; render();
  };

  function open(from) {
    opener = from;
    var svc = from.getAttribute("data-svc"), doc = from.getAttribute("data-doc"),
        day = from.getAttribute("data-day"), t = from.getAttribute("data-t");
    if (svc || doc) {
      st = { s: svc || "cons", d: doc || "any", day: day === null ? null : +day, t: t || null, all: false };
    }
    render();
    $("zp-done").hidden = true; $("zp-form").hidden = false;
    scrim.hidden = false; pop.hidden = false; document.body.classList.add("zp-open");
    $("zp-x").focus();
  }
  function close() {
    if (pop.hidden) { return; }
    pop.hidden = true; scrim.hidden = true; document.body.classList.remove("zp-open");
    if (opener) { opener.focus(); }
  }
  document.addEventListener("click", function (e) {
    var a = e.target.closest ? e.target.closest('a[href="#zapis"]') : null;
    if (!a) { return; }
    e.preventDefault(); open(a);
  });
  $("zp-x").onclick = close;
  scrim.onclick = close;
  document.addEventListener("keydown", function (e) {
    if (pop.hidden) { return; }
    if (e.key === "Escape") { close(); return; }
    if (e.key === "Tab") {                      // keep focus inside the window
      var f = pop.querySelectorAll("button:not([disabled]), select");
      f = Array.prototype.filter.call(f, function (x) { return x.offsetParent !== null; });
      if (!f.length) { return; }
      if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
      else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
    }
  });

  // Карточка в первом экране: три ближайших времени терапевта, каждое открывает окно с ним.
  var teaser = $("hero-times"), tday = $("hero-day");
  if (teaser) {
    var ds = days(), picks = [];
    for (var i = 0; i < ds.length && picks.length < 4; i++) {
      freeFor("ter", "shad", ds[i]).slice(0, 4 - picks.length).forEach(function (t) { picks.push([i, t]); });
    }
    teaser.textContent = "";
    picks.forEach(function (p) {
      var a = document.createElement("a");
      a.href = "#zapis"; a.className = "slot";
      a.setAttribute("data-svc", "ter"); a.setAttribute("data-doc", "shad");
      a.setAttribute("data-day", String(p[0])); a.setAttribute("data-t", p[1]);
      a.innerHTML = "<small></small>"; a.firstChild.textContent = dayShort(ds[p[0]]).replace(/, \d+ .*/, "");
      a.appendChild(document.createTextNode(p[1]));
      teaser.appendChild(a);
    });
    if (tday && picks.length) { tday.textContent = "Ближайшее: " + dayName(ds[picks[0][0]]); }
  }
}());
