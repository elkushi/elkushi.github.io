/* Онлайн-запись — демо (Moustafa, 2026-11-16). Карточка «C · три поля», открывается окном по любой
   кнопке «Записаться» / «Выбрать время онлайн» (на телефоне — панелью снизу).
   Ничего не сохраняет и никуда не отправляет. Услуги, цены и имена врачей — с этой же страницы
   (сайт клиники и отзывы на Яндексе); свободное время придумано. */
(function () {
  "use strict";
  var $ = function (id) { return document.getElementById(id); };
  var pop = $("zp-pop"), scrim = $("zp-scrim");
  if (!pop || !scrim) { return; }

  // [id, название, цена со страницы, врачи (пусто = все)]
  var SERVICES = [
    ["cons", "Первичная консультация", "бесплатно", []],
    ["ter", "Лечение кариеса, пломба", "от 4 000 ₽", []],
    ["udal", "Удаление зуба", "от 2 500 ₽", ["tv"]],
    ["impl", "Имплантация", "консультация", ["av"]],
    ["prot", "Коронки и протезы", "от 12 000 ₽", []],
    ["gig", "Профгигиена", "3 500 ₽ за челюсть", []],
    ["rtg", "Снимок зубов (ОПТГ)", "2 000 ₽", []],
    ["kids", "Детский приём", "", []]
  ];
  var DOCTORS = [
    ["any", "Любой свободный"],
    ["tv", "Татьяна Викторовна"],
    ["md", "Максим Дмитриевич"],
    ["av", "Алина Владимировна"],
    ["yv", "Юлия Викторовна"]
  ];
  var OPEN = 9, CLOSE = 21;                       // ежедневно 09:00–21:00
  var WD = ["вс", "пн", "вт", "ср", "чт", "пт", "сб"];
  var MON = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа",
             "сентября", "октября", "ноября", "декабря"];

  var st = { s: "cons", d: "any", day: null, t: null, all: false }, opener = null;

  function days() {
    var out = [], d0 = new Date(); d0.setHours(0, 0, 0, 0);
    for (var i = 0; i < 7; i++) { out.push(new Date(d0.getTime() + i * 86400000)); }
    return out;
  }
  function dayName(d, i) {
    var dm = d.getDate() + " " + MON[d.getMonth()];
    return i === 0 ? "сегодня, " + dm : i === 1 ? "завтра, " + dm : WD[d.getDay()] + ", " + dm;
  }
  function dayShort(i, d) { return i === 0 ? "сегодня" : i === 1 ? "завтра" : WD[d.getDay()] + ", " + d.getDate() + " " + MON[d.getMonth()]; }

  // Занятость — по постоянному правилу, а не случайно: время не «прыгает», если вернуться к дню.
  function busy(i, h, half, doc) {
    var seed = i * 97 + h * 13 + (half ? 7 : 0) + doc.charCodeAt(0) * 31 + doc.charCodeAt(1) * 17;
    return (seed * 2654435761 % 100) < 45;
  }
  function docsFor(s) {
    var only = SERVICES.filter(function (x) { return x[0] === s; })[0][3];
    return DOCTORS.filter(function (d) { return d[0] === "any" || !only.length || only.indexOf(d[0]) >= 0; });
  }
  function free(i) {
    var out = [], ds = days(), now = Date.now(), real = docsFor(st.s).filter(function (d) { return d[0] !== "any"; });
    for (var h = OPEN; h < CLOSE; h++) {
      for (var half = 0; half < 2; half++) {
        var when = new Date(ds[i].getTime()); when.setHours(h, half ? 30 : 0, 0, 0);
        if (when.getTime() < now + 2 * 3600000) { continue; }
        var ok = st.d === "any"
          ? real.some(function (d) { return !busy(i, h, half, d[0]); })
          : !busy(i, h, half, st.d);
        if (ok) { out.push(("0" + h).slice(-2) + ":" + (half ? "30" : "00")); }
      }
    }
    return out;
  }
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

    fill($("zp-svc"), SERVICES.map(function (s) { return [s[0], s[1] + (s[2] ? " · " + s[2] : "")]; }), st.s);
    fill($("zp-doc"), docs.map(function (d) { return [d[0], d[1]]; }), st.d);
    fill($("zp-day"), ds.map(function (d, i) { return [String(i), dayName(d, i) + (free(i).length ? "" : " · мест нет")]; }), String(st.day));

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
    go.textContent = st.t ? "Записаться на " + dayShort(st.day, ds[st.day]) + ", " + st.t : "Выберите другой день";
  }

  $("zp-svc").onchange = function () { st.s = this.value; st.t = null; st.all = false; render(); };
  $("zp-doc").onchange = function () { st.d = this.value; st.t = null; st.all = false; render(); };
  $("zp-day").onchange = function () { st.day = +this.value; st.t = null; st.all = false; render(); };

  $("zp-go").onclick = function () {
    var ds = days(), svc = SERVICES.filter(function (s) { return s[0] === st.s; })[0][1];
    var doc = DOCTORS.filter(function (d) { return d[0] === st.d; })[0][1];
    $("zp-done-text").textContent = svc + " · " + doc + " · " + dayName(ds[st.day], st.day) + ", " + st.t;
    $("zp-form").hidden = true; $("zp-done").hidden = false;
    $("zp-again").focus();
  };
  $("zp-again").onclick = function () {
    $("zp-done").hidden = true; $("zp-form").hidden = false;
    st = { s: "cons", d: "any", day: null, t: null, all: false }; render();
  };

  function open(from, doc) {
    opener = from;
    if (doc) { st.d = doc; st.t = null; st.day = null; }
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
  Array.prototype.forEach.call(document.querySelectorAll('a[href="#zapis"]'), function (a) {
    a.addEventListener("click", function (e) { e.preventDefault(); open(a, a.getAttribute("data-doc")); });
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
}());
