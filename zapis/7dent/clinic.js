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
      "id": "gig",
      "name": "Профгигиена",
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
    },
    {
      "id": "ortho",
      "name": "Брекеты и элайнеры",
      "mins": 45,
      "note": "консультация ортодонта"
    }
  ],
  "doctors": [
    {
      "id": "d1",
      "name": "Исупова Ю. А.",
      "role": "терапевт, детский стоматолог",
      "does": [
        "cons",
        "karies",
        "gig"
      ]
    },
    {
      "id": "d2",
      "name": "Погорелый В. В.",
      "role": "ортопед",
      "does": [
        "cons",
        "ortoped"
      ]
    },
    {
      "id": "d3",
      "name": "Козлов Н. М.",
      "role": "хирург-имплантолог",
      "does": [
        "cons",
        "udal",
        "impl"
      ]
    },
    {
      "id": "d4",
      "name": "Мрыхин С. В.",
      "role": "ортодонт",
      "does": [
        "cons",
        "ortho"
      ]
    },
    {
      "id": "dany",
      "name": "Любой свободный",
      "role": "подберём врача",
      "does": [
        "cons",
        "karies",
        "gig",
        "udal",
        "ortoped",
        "impl",
        "ortho"
      ],
      "any": true
    }
  ],
  "open": 9,
  "close": 21,
  "closed": [],
  "address": "ул. Булатниковская, 6 к1"
};
