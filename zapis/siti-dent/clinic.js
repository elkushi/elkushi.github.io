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
      "name": "Багдасарьян Виолета Арсеновна",
      "role": "терапевт, ортопед",
      "does": [
        "cons",
        "karies",
        "gig",
        "ortoped"
      ]
    },
    {
      "id": "d2",
      "name": "Арестов Дмитрий Сергеевич",
      "role": "имплантолог, ортопед, хирург",
      "does": [
        "cons",
        "udal",
        "ortoped",
        "impl"
      ]
    },
    {
      "id": "d3",
      "name": "Эльдаров Муслим Камилович",
      "role": "имплантолог, хирург, ортопед",
      "does": [
        "cons",
        "udal",
        "ortoped",
        "impl"
      ]
    },
    {
      "id": "d4",
      "name": "Ярош Анастасия Игоревна",
      "role": "ортодонт, терапевт",
      "does": [
        "cons",
        "karies",
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
  "address": "Багратионовский проезд, 7, корп. 20В"
};
