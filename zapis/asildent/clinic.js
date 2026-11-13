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
      "name": "Исмоилов А. Б.",
      "role": "стоматолог, директор клиники",
      "does": [
        "cons",
        "karies",
        "gig",
        "ortoped"
      ]
    },
    {
      "id": "d2",
      "name": "Исмоилов Ж. Б.",
      "role": "стоматолог",
      "does": [
        "cons",
        "karies",
        "gig"
      ]
    },
    {
      "id": "d3",
      "name": "Азизов А. С.",
      "role": "стоматолог",
      "does": [
        "cons",
        "karies",
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
  "close": 19,
  "closed": [],
  "address": "г. Краснотурьинск, ул. Чкалова, 12, помещение № 8",
  "hours_by_day": {
    "0": [
      10,
      14
    ],
    "6": [
      10,
      14
    ]
  }
};
