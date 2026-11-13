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
      "name": "Дьяконова Д. Ю.",
      "role": "терапевт, пародонтолог",
      "does": [
        "cons",
        "karies",
        "gig"
      ]
    },
    {
      "id": "d2",
      "name": "Вишняковский И. А.",
      "role": "ортопед, хирург-имплантолог",
      "does": [
        "cons",
        "udal",
        "ortoped",
        "impl"
      ]
    },
    {
      "id": "d3",
      "name": "Эгембердиев Б. А.",
      "role": "ортопед, хирург",
      "does": [
        "cons",
        "udal",
        "ortoped"
      ]
    },
    {
      "id": "d4",
      "name": "Ильгияева И. И.",
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
  "address": "Цветной бульвар · ул. Фонвизина · Дмитровское шоссе"
};
