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
      "id": "ortho",
      "name": "Брекеты и элайнеры",
      "mins": 45,
      "note": "консультация ортодонта"
    }
  ],
  "doctors": [
    {
      "id": "d1",
      "name": "Кабацкая Е. Н.",
      "role": "стоматолог-терапевт",
      "does": [
        "cons",
        "karies",
        "gig"
      ]
    },
    {
      "id": "d2",
      "name": "Юсуфов Р. О.",
      "role": "терапевт, ортопед",
      "does": [
        "cons",
        "karies",
        "ortoped"
      ]
    },
    {
      "id": "d3",
      "name": "Кривоносова П. А.",
      "role": "хирург",
      "does": [
        "cons",
        "udal"
      ]
    },
    {
      "id": "d4",
      "name": "Медведев О. А.",
      "role": "ортодонт, детский стоматолог",
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
        "ortho"
      ],
      "any": true
    }
  ],
  "open": 9,
  "close": 21,
  "closed": [],
  "address": "Первомайская ул., 35/18, вход со двора"
};
