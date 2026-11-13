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
      "name": "Сысоева Н. Ю.",
      "role": "терапевт, ортопед, эндодонтист",
      "does": [
        "cons",
        "karies",
        "gig",
        "ortoped"
      ]
    },
    {
      "id": "d2",
      "name": "Тагиров А. А.",
      "role": "терапевт-микроскопист",
      "does": [
        "cons",
        "karies"
      ]
    },
    {
      "id": "d3",
      "name": "Заболотний В. Н.",
      "role": "хирург-имплантолог",
      "does": [
        "cons",
        "udal",
        "impl"
      ]
    },
    {
      "id": "d4",
      "name": "Пушкаш А. О.",
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
  "address": "проезд Русанова, 11, помещение 1"
};
