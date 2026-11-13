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
    }
  ],
  "doctors": [
    {
      "id": "d1",
      "name": "Гаглоев В. Х.",
      "role": "главный врач, стоматолог-универсал",
      "does": [
        "cons",
        "karies",
        "gig",
        "ortoped"
      ]
    },
    {
      "id": "d2",
      "name": "Ремизова Е. В.",
      "role": "стоматолог-терапевт",
      "does": [
        "cons",
        "karies",
        "gig"
      ]
    },
    {
      "id": "d3",
      "name": "Жарук А. В.",
      "role": "хирург-имплантолог",
      "does": [
        "cons",
        "udal",
        "impl"
      ]
    },
    {
      "id": "d4",
      "name": "Карасалихова З. М.",
      "role": "хирург, имплантолог",
      "does": [
        "cons",
        "udal",
        "impl"
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
        "impl"
      ],
      "any": true
    }
  ],
  "open": 9,
  "close": 21,
  "closed": [],
  "address": "Малый Краснопрудный тупик, 2, цокольный этаж"
};
