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
      "id": "r1",
      "name": "Стоматолог-терапевт",
      "role": "лечение, гигиена",
      "does": [
        "cons",
        "karies",
        "gig"
      ]
    },
    {
      "id": "r2",
      "name": "Хирург-имплантолог",
      "role": "удаление, импланты",
      "does": [
        "cons",
        "udal",
        "impl"
      ]
    },
    {
      "id": "r3",
      "name": "Ортопед",
      "role": "коронки и протезы",
      "does": [
        "cons",
        "ortoped"
      ]
    },
    {
      "id": "r4",
      "name": "Ортодонт",
      "role": "брекеты и элайнеры",
      "does": [
        "cons",
        "ortho"
      ]
    },
    {
      "id": "rany",
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
  "open": 0,
  "close": 24,
  "closed": [],
  "address": "круглосуточные клиники в Москве и области"
};
