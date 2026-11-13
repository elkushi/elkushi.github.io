/* Booking demo for clinic owners. Everything runs in the page: no network, no storage,
   nothing is submitted. Slots are generated from the demo clinic's own hours so the
   screen behaves the way a real one would (Sunday closed, past hours gone today). */
(function () {
  "use strict";

  var SERVICES = [
    { id: "cons",  name: "Консультация",        mins: 30 },
    { id: "karies",name: "Лечение кариеса",     mins: 60 },
    { id: "gig",   name: "Профгигиена",         mins: 60 },
    { id: "impl",  name: "Имплантация",         mins: 90, note: "консультация хирурга" },
    { id: "ortho", name: "Брекеты и элайнеры",  mins: 45, note: "консультация ортодонта" }
  ];
  var DOCTORS = [
    { id: "d1", name: "Анна Сергеевна",  role: "стоматолог-терапевт", does: ["cons","karies","gig"] },
    { id: "d2", name: "Игорь Павлович",  role: "хирург-имплантолог",  does: ["cons","impl"] },
    { id: "d3", name: "Мария Олеговна",  role: "ортодонт",            does: ["cons","ortho"] },
    { id: "d4", name: "Любой свободный", role: "подберём врача",      does: ["cons","karies","gig","impl","ortho"] }
  ];
  var OPEN = 9, CLOSE = 21;          // Пн–Сб 09:00–21:00
  var WD = ["воскресенье","понедельник","вторник","среда","четверг","пятница","суббота"];
  var WD_SHORT = ["вс","пн","вт","ср","чт","пт","сб"];
  var MON = ["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"];

  var ANY = "d4";                    // «Любой свободный» is a choice, not a doctor
  var state = { service: null, doctor: null, day: null, slot: null, assigned: null };
  var $ = function (id) { return document.getElementById(id); };

  /* A slot is "taken" by a stable pseudo-random rule rather than Math.random, so the grid does
     not reshuffle every time the owner changes the day and back — that looks broken. */
  function taken(dayIndex, hour, half, doctorId) {
    var seed = dayIndex * 97 + hour * 13 + (half ? 7 : 0) + doctorId.charCodeAt(1) * 31;
    return (seed * 2654435761 % 100) < 42;
  }

  function days() {
    var out = [], d = new Date(), i;
    d.setHours(0, 0, 0, 0);
    for (i = 0; out.length < 6 && i < 14; i++) {
      var x = new Date(d.getTime() + i * 86400000);
      if (x.getDay() === 0) continue;                 // воскресенье выходной
      out.push({ date: x, offset: i });
    }
    return out;
  }

  /* «Любой свободный»: a slot is free when any real doctor who does the chosen service is free
     then, and the booking goes to that doctor. The bot and the admin card name them, because a
     patient told "you are booked with Любой свободный" would think the page is broken. */
  function freeDoctor(dayIndex, h, half) {
    var c = DOCTORS.filter(function (d) {
      return d.id !== ANY && (!state.service || d.does.indexOf(state.service) >= 0) &&
             !taken(dayIndex, h, half, d.id);
    });
    return c.length ? c[0].id : null;
  }

  function slotsFor(day, doctorId) {
    var out = [], now = new Date(), h, half;
    for (h = OPEN; h < CLOSE; h++) {
      for (half = 0; half < 2; half++) {
        var when = new Date(day.date.getTime());
        when.setHours(h, half ? 30 : 0, 0, 0);
        if (when.getTime() < now.getTime() + 2 * 3600000) continue;  // не раньше чем через 2 часа
        var doc = doctorId === ANY ? freeDoctor(day.offset, h, half)
                                   : (taken(day.offset, h, half, doctorId) ? null : doctorId);
        out.push({
          label: ("0" + h).slice(-2) + ":" + (half ? "30" : "00"),
          free: !!doc,
          doc: doc,
          when: when
        });
      }
    }
    return out;
  }

  function button(label, meta, on, disabled) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "opt";
    b.setAttribute("aria-pressed", on ? "true" : "false");
    if (disabled) { b.disabled = true; }
    b.appendChild(document.createTextNode(label));
    if (meta) {
      var s = document.createElement("span");
      s.className = "meta";
      s.textContent = meta;
      b.appendChild(s);
    }
    return b;
  }

  function fmtDay(d) {
    return WD_SHORT[d.getDay()] + ", " + d.getDate() + " " + MON[d.getMonth()];
  }

  function render() {
    // services
    var box = $("services");
    box.textContent = "";
    SERVICES.forEach(function (s) {
      var b = button(s.name, s.note || (s.mins + " мин"), state.service === s.id, false);
      b.onclick = function () {
        state.service = s.id;
        if (state.doctor) {
          var d = DOCTORS.filter(function (x) { return x.id === state.doctor; })[0];
          if (d && d.does.indexOf(s.id) < 0) { state.doctor = null; state.slot = null; }
        }
        if (state.doctor === ANY) { state.slot = null; }   // who is free depends on the service
        render();
      };
      box.appendChild(b);
    });

    // doctors — only those who do the chosen service
    box = $("doctors");
    box.textContent = "";
    DOCTORS.forEach(function (d) {
      var can = !state.service || d.does.indexOf(state.service) >= 0;
      var b = button(d.name, can ? d.role : "не ведёт эту услугу", state.doctor === d.id, !can);
      b.onclick = function () { state.doctor = d.id; state.slot = null; state.assigned = null; render(); };
      box.appendChild(b);
    });

    // days
    box = $("days");
    box.textContent = "";
    days().forEach(function (day) {
      var label = day.offset === 0 ? "сегодня" : day.offset === 1 ? "завтра" : fmtDay(day.date);
      var b = button(label, day.offset <= 1 ? fmtDay(day.date) : WD[day.date.getDay()],
                     state.day === day.offset, false);
      b.onclick = function () { state.day = day.offset; state.slot = null; state.assigned = null; render(); };
      box.appendChild(b);
    });

    // slots
    box = $("slots");
    box.textContent = "";
    if (state.day === null || !state.doctor) {
      var hint = document.createElement("p");
      hint.className = "hint";
      hint.textContent = "Выберите врача и день — свободные окна появятся здесь.";
      box.appendChild(hint);
    } else {
      var day = days().filter(function (d) { return d.offset === state.day; })[0];
      var list = slotsFor(day, state.doctor), free = 0;
      list.forEach(function (s) {
        if (!s.free) { return; }
        free++;
        var b = button(s.label, null, state.slot === s.label, false);
        b.onclick = function () { state.slot = s.label; state.when = s.when; state.assigned = s.doc; render(); };
        box.appendChild(b);
      });
      if (!free) {
        var none = document.createElement("p");
        none.className = "hint";
        none.textContent = "В этот день у врача всё занято — выберите другой день.";
        box.appendChild(none);
      }
    }

    // progress + summary + button
    var done = { 1: !!state.service, 2: !!state.doctor, 3: state.day !== null, 4: !!state.slot };
    Array.prototype.forEach.call($("steps").children, function (li) {
      var n = li.getAttribute("data-step");
      li.removeAttribute("data-on"); li.removeAttribute("data-done");
      if (done[n]) { li.setAttribute("data-done", "1"); }
      else if (!li.previousElementSibling || done[n - 1]) { li.setAttribute("data-on", "1"); }
    });

    var parts = [];
    if (state.service) { parts.push(["Услуга", name(SERVICES, state.service)]); }
    if (state.doctor)  { parts.push(["Врач", doctorLabel()]); }
    if (state.day !== null) {
      parts.push(["День", fmtDay(days().filter(function (d) { return d.offset === state.day; })[0].date)]);
    }
    if (state.slot) { parts.push(["Время", state.slot]); }
    var sum = $("summary");
    sum.textContent = "";
    parts.forEach(function (p) {
      var el = document.createElement("div");
      el.appendChild(document.createTextNode(p[0] + ": "));
      var b = document.createElement("b");
      b.textContent = p[1];
      el.appendChild(b);
      sum.appendChild(el);
    });

    var go = $("go");
    go.disabled = !(state.slot && state.service);
    go.textContent = !state.slot ? "Выберите время"
                   : !state.service ? "Выберите услугу"
                   : "Записаться на " + state.slot;
  }

  // The doctor the patient is actually booked with: for «Любой свободный», the one we assigned.
  function bookedDoctor() {
    return name(DOCTORS, state.doctor === ANY ? state.assigned : state.doctor);
  }

  function doctorLabel() {
    if (state.doctor !== ANY) { return name(DOCTORS, state.doctor); }
    if (!(state.slot && state.assigned)) { return "любой свободный"; }
    var free = state.assigned === "d2" ? "свободен" : "свободна";   // Игорь Павлович
    return bookedDoctor() + " (" + free + " в это время)";
  }

  function name(list, id) {
    var x = list.filter(function (i) { return i.id === id; })[0];
    return x ? x.name : "";
  }

  function msg(text, mine, time, buttons) {
    var m = document.createElement("div");
    m.className = "msg" + (mine ? " me" : "");
    text.split("\n").forEach(function (line, i) {
      if (i) { m.appendChild(document.createElement("br")); }
      m.appendChild(document.createTextNode(line));
    });
    if (buttons) {
      var row = document.createElement("div");
      row.className = "btn-row";
      buttons.forEach(function (b) {
        var s = document.createElement("span");
        s.textContent = b;
        row.appendChild(s);
      });
      m.appendChild(row);
    }
    var t = document.createElement("span");
    t.className = "t";
    t.textContent = time;
    m.appendChild(t);
    return m;
  }

  function tag(text) {
    var d = document.createElement("div");
    d.className = "tag";
    d.textContent = text;
    return d;
  }

  function book() {
    var svc = name(SERVICES, state.service),
        doc = bookedDoctor(),
        day = fmtDay(days().filter(function (d) { return d.offset === state.day; })[0].date);

    $("form").style.display = "none";
    $("done").classList.add("on");
    $("done-text").textContent = svc + " · " + doc + " · " + day + ", " + state.slot + ".";

    var chat = $("chat");
    chat.textContent = "";
    chat.appendChild(msg("Здравствуйте! Записал вас:\n" + svc + "\n" + doc + "\n" + day +
                         ", " + state.slot + "\nАдрес и как пройти — в закреплённом сообщении.",
                         false, "сейчас"));
    chat.appendChild(tag("накануне визита"));
    chat.appendChild(msg("Напоминаю: завтра в " + state.slot + ", " + doc + ".", false,
                         "за сутки", ["Приду", "Перенести"]));
    chat.appendChild(tag("в день визита"));
    chat.appendChild(msg("Ждём вас через 2 часа. Если планы поменялись — нажмите «Перенести», " +
                         "окно уйдёт другому пациенту.", false, "за 2 часа", ["Приду", "Перенести"]));
    chat.appendChild(tag("после приёма"));
    chat.appendChild(msg("Спасибо, что были у нас! Если всё понравилось, оставьте, пожалуйста, " +
                         "отзыв на Яндекс Картах — это займёт минуту.", false, "вечером",
                         ["Оставить отзыв"]));

    $("admin-when").textContent = "заявка пришла только что";
    $("admin-service").textContent = svc;
    $("admin-doctor").textContent = doc;
    $("admin-time").textContent = day + ", " + state.slot;
    $("admin-state").classList.remove("on");
  }

  function reset() {
    state = { service: null, doctor: null, day: null, slot: null, assigned: null };
    $("form").style.display = "";
    $("done").classList.remove("on");
    var chat = $("chat");
    chat.textContent = "";
    chat.appendChild(tag("здесь появятся сообщения пациенту"));
    $("admin-when").textContent = "ждёт записи слева";
    $("admin-service").textContent = "—";
    $("admin-doctor").textContent = "—";
    $("admin-time").textContent = "—";
    $("admin-state").classList.remove("on");
    render();
  }

  $("go").onclick = book;
  $("again").onclick = reset;
  $("confirm").onclick = function () {
    if ($("admin-service").textContent === "—") { return; }
    $("admin-state").classList.add("on");
  };

  render();
}());
