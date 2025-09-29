# 📘 Historical Sports Odds API (v4)

This document provides chatbot-ready reference material for the historical sports odds API.
It includes:

1. Human-readable documentation (Markdown).
2. Machine-friendly JSONL chunks (for retrieval/embedding).

---

## 🔹 `/v4/historical/sports/{sport}/odds`

Returns a list of live and upcoming events at a point in time for a given sport, including bookmaker odds.
➡️ Previously `/v4/sports/{sport}/odds-history` (deprecated).

### Parameters

* **sport** *(string)* – The sport key
* **apiKey** *(string)*
* **regions** *(string)* – Region of bookmakers
* **markets** *(string)* – Odds market(s) to return

  * Available: `h2h`, `spreads`, `totals`, `outrights`
  * Default: `h2h`
  * Example: `h2h,spreads`
* **dateFormat** – `iso` (ISO8601) or `unix`
* **oddsFormat** – Format of odds (decimal, American, etc.)
* **eventIds** – Specific event IDs
* **bookmakers** – Comma-separated bookmaker keys
* **date** – Snapshot timestamp

### Example Response

```json
{
  "timestamp": "2023-10-10T12:10:39Z",
  "previous_timestamp": "2023-10-10T12:05:39Z",
  "next_timestamp": "2023-10-10T12:15:39Z",
  "data": [
    {
      "id": "e912304de2b2ce35b473ce2ecd3d1502",
      "sport_key": "americanfootball_nfl",
      "sport_title": "NFL",
      "commence_time": "2023-10-11T23:10:00Z",
      "home_team": "Houston Texans",
      "away_team": "Kansas City Chiefs",
      "bookmakers": [
        {
          "key": "draftkings",
          "title": "DraftKings",
          "last_update": "2023-10-10T12:10:29Z",
          "markets": [
            {
              "key": "h2h",
              "last_update": "2023-10-10T12:10:29Z",
              "outcomes": [
                { "name": "Houston Texans", "price": 2.23 },
                { "name": "Kansas City Chiefs", "price": 1.45 }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 🔹 `/v4/historical/sports/{sport}/events`

Returns a list of events for the specified sport as they appeared at the given timestamp.
⚠️ Odds are **not included**.

### Parameters

* **sport** *(string)*
* **apiKey** *(string)*
* **dateFormat** *(string)*
* **eventIds** *(string)*
* **commenceTimeFrom** *(string)*
* **commenceTimeTo** *(string)*
* **date** *(string)* – Snapshot timestamp

### Example Response

```json
{
  "timestamp": "2023-10-10T12:10:39Z",
  "previous_timestamp": "2023-10-10T12:05:39Z",
  "next_timestamp": "2023-10-10T12:15:39Z",
  "data": [
    {
      "id": "e912304de2b2ce35b473ce2ecd3d1502",
      "sport_key": "americanfootball_nfl",
      "sport_title": "NFL",
      "commence_time": "2023-10-11T23:10:00Z",
      "home_team": "Houston Texans",
      "away_team": "Kansas City Chiefs"
    }
  ]
}
```

---

## 🔹 `/v4/historical/sports/{sport}/events/{eventId}/odds`

Returns bookmaker odds for a **single event** at the specified timestamp.
➡️ For featured markets only, use `/v4/historical/sports/{sport}/odds`.

### Parameters

* **sport** *(string)*
* **eventId** *(string)* – Found in `/events` response (`id` field)
* **apiKey** *(string)*
* **dateFormat** *(string)* – `iso` or `unix`
* **regions** *(string)* – Region of bookmakers
* **markets** *(string)* – Comma-separated list of markets (default: `h2h`)
* **oddsFormat** – Format of odds
* **bookmakers** *(string)* – Comma-separated bookmaker keys

  * Precedence: `bookmakers` > `regions`
  * Billing: every **10 bookmakers = 1 request**
* **date** *(string)* – Snapshot timestamp

### Example Response

```json
{
  "timestamp": "2023-10-10T12:10:39Z",
  "previous_timestamp": "2023-10-10T12:05:39Z",
  "next_timestamp": "2023-10-10T12:15:39Z",
  "data": {
    "id": "e912304de2b2ce35b473ce2ecd3d1502",
    "sport_key": "americanfootball_nfl",
    "sport_title": "NFL",
    "commence_time": "2023-10-11T23:10:00Z",
    "home_team": "Houston Texans",
    "away_team": "Kansas City Chiefs",
    "bookmakers": [
      {
        "key": "draftkings",
        "title": "DraftKings",
        "markets": [
          {
            "key": "alternate_spreads",
            "last_update": "2023-10-10T12:10:29Z",
            "outcomes": [
              { "name": "Houston Texans", "price": 5.08, "point": -23 },
              { "name": "Houston Texans", "price": 4.82, "point": -22.5 },
              { "name": "Houston Texans", "price": 4.66, "point": -22 },
              { "name": "Kansas City Chiefs", "price": 1.15, "point": 23 },
              { "name": "Kansas City Chiefs", "price": 1.17, "point": 22.5 },
              { "name": "Kansas City Chiefs", "price": 1.17, "point": 22 }
            ]
          }
        ]
      }
    ]
  }
}
```

---

# 📂 JSONL Chunks for Retrieval

Below are machine-friendly **chunks** of the same documentation.
Each record can be embedded in a vector database.

```jsonl
{"id":"1","endpoint":"/v4/historical/sports/{sport}/odds","section":"description","text":"Returns a list of live and upcoming events at a point in time for a given sport, including bookmaker odds. Previously /v4/sports/{sport}/odds-history (deprecated)."}
{"id":"2","endpoint":"/v4/historical/sports/{sport}/odds","section":"parameters","text":"sport (string), apiKey (string), regions (string), markets (string: h2h, spreads, totals, outrights; default h2h), dateFormat (iso/unix), oddsFormat, eventIds, bookmakers, date"}
{"id":"3","endpoint":"/v4/historical/sports/{sport}/odds","section":"example_response","text":"JSON response with timestamp, event id, sport_key, sport_title, commence_time, teams, bookmakers, markets, outcomes with odds."}

{"id":"4","endpoint":"/v4/historical/sports/{sport}/events","section":"description","text":"Returns a list of events for the specified sport as they appeared at the given timestamp. Odds are not included."}
{"id":"5","endpoint":"/v4/historical/sports/{sport}/events","section":"parameters","text":"sport (string), apiKey (string), dateFormat (string), eventIds (string), commenceTimeFrom (string), commenceTimeTo (string), date (string)"}
{"id":"6","endpoint":"/v4/historical/sports/{sport}/events","section":"example_response","text":"JSON response with timestamp fields and events including id, sport_key, sport_title, commence_time, home_team, away_team."}

{"id":"7","endpoint":"/v4/historical/sports/{sport}/events/{eventId}/odds","section":"description","text":"Returns bookmaker odds for a single event at the specified timestamp. For featured markets only, use /v4/historical/sports/{sport}/odds."}
{"id":"8","endpoint":"/v4/historical/sports/{sport}/events/{eventId}/odds","section":"parameters","text":"sport (string), eventId (string), apiKey (string), dateFormat (iso/unix), regions (string), markets (string; default h2h), oddsFormat, bookmakers (comma separated; precedence over regions; billing note about 10 bookmakers per request), date (string)"}
{"id":"9","endpoint":"/v4/historical/sports/{sport}/events/{eventId}/odds","section":"example_response","text":"JSON response with timestamp fields, event details (id, sport_key, sport_title, commence_time, teams), and bookmakers with markets and alternate spreads outcomes."}
```
