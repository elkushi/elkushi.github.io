/* Clinic data for this demo: public facts from the clinic's own site (see its study.md).
   page.js reads window.CLINIC; nothing else here is clinic-specific. */
window.CLINIC = {
  "services": [
    {
      "id": "cons",
      "name": "Осмотр и консультация",
      "mins": 30
    },
    {
      "id": "karies",
      "name": "Лечение кариеса",
      "mins": 60
    },
    {
      "id": "udal",
      "name": "Удаление зуба",
      "mins": 45,
      "note": "хирург"
    },
    {
      "id": "ortoped",
      "name": "Коронка или протез",
      "mins": 60,
      "note": "консультация ортопеда"
    },
    {
      "id": "impl",
      "name": "Имплантация",
      "mins": 90,
      "note": "консультация хирурга"
    }
  ],
  "doctors": [
    {
      "id": "d1",
      "name": "Атаманюк Елена Владимировна",
      "role": "стоматолог-терапевт, пародонтолог",
      "does": [
        "cons",
        "karies"
      ]
    },
    {
      "id": "d2",
      "name": "Мороян Абрам Карапетович",
      "role": "терапевт, хирург, ортопед",
      "does": [
        "cons",
        "karies",
        "udal",
        "ortoped",
        "impl"
      ]
    },
    {
      "id": "d3",
      "name": "Графский Дмитрий Михайлович",
      "role": "терапевт, ортопед",
      "does": [
        "cons",
        "karies",
        "ortoped"
      ]
    },
    {
      "id": "d4",
      "name": "Любой свободный",
      "role": "подберём врача",
      "does": [
        "cons",
        "karies",
        "udal",
        "ortoped",
        "impl"
      ]
    }
  ],
  "open": 9,
  "close": 21,
  "closed": [
    0
  ],
  "address": "ул. Бибиревская, 9 к1, вход со двора"
};
