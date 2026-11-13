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
      "name": "Онучин К. В.",
      "role": "врач клиники",
      "does": [
        "cons",
        "karies",
        "gig",
        "ortoped",
        "impl"
      ]
    }
  ],
  "open": 10,
  "close": 21,
  "closed": [],
  "address": "Большая Переяславская ул., 10, помещение 1/1",
  "hours_by_day": {
    "0": [
      11,
      18
    ],
    "6": [
      11,
      18
    ]
  }
};
