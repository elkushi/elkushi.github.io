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
      "name": "Бабаев А. О.",
      "role": "главный врач",
      "does": [
        "cons",
        "karies",
        "gig"
      ]
    },
    {
      "id": "d2",
      "name": "Сапогов С. В.",
      "role": "стоматолог-терапевт",
      "does": [
        "cons",
        "karies",
        "gig"
      ]
    },
    {
      "id": "d3",
      "name": "Кожевин А. П.",
      "role": "хирург, имплантолог, ортопед",
      "does": [
        "cons",
        "udal",
        "ortoped",
        "impl"
      ]
    },
    {
      "id": "d4",
      "name": "Юнисова К. А.",
      "role": "детский стоматолог",
      "does": [
        "cons",
        "karies"
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
  "open": 10,
  "close": 21,
  "closed": [],
  "address": "Стремянный пер., 38"
};
