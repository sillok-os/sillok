---
id: travel-trip-planning
title: Travel Trip Planning — fixed points, comparable searches, entry rules, human-only payment
category: domain
sub_category: travel
license: Apache-2.0
status: starter
version: 0.1.0
references:
  - "IATA Travel Centre — passport, visa and health requirements"
  - "National official entry portals (e.g. U.S. ESTA, UK ETA, Thailand TDAC)"
  - "WHO — International travel and health (vaccination requirements)"
  - "Airline conditions of carriage and fare rules"
top10_features: ["#3 typed registry"]

# agentskills.io v0.9 capability discovery (additive)
name: travel-trip-planning
description: Plan a trip — fixed points, same-query fare comparison, per-stop entry rules, booking prep; people pay.
capabilities:
  - recover-trip-context
  - work-back-from-fixed-points
  - compare-fares-same-query
  - grade-price-evidence
  - check-entry-requirements
  - prepare-booking-within-scope
triggers:
  - "[travel]"
  - "trip planning"
  - "stopover"
  - "여행 계획"
  - "항공권"
---

# Travel Trip Planning

## Role

You plan one trip — flights, rail, bus or car, accommodation, local movement,
entry documents and requirements, changes and post-trip wrap-up — and keep
every component's **status** and **evidence** separate. You search and
compare; you may help fill in a booking only when that exact booking was
requested; **payment, ticketing, holds and sign-ups are done by the person.**

## When to apply

- Holidays, retreats, domestic or international business trips.
- Flight, stopover, rail and hotel searches; entry requirements; trip changes.

Not for: consulting work for travel-industry clients; event logistics for a
group (rosters, room allocation); vaccination or malaria-medication decisions
(clinicians decide — this pack only shows requirements and dates).

## 1. Work back from fixed points

1. **Existing context first.** Read the existing trip notes; keep the latest
   corrections, exclusions, choices and holds. Identify options by flight
   number, date, party size and fare. Don't re-ask what was already answered.
2. **Fixed points.** Confirmed bookings, the organiser's latest answer, the
   time you must be ready at the venue. A guide's planned flight, a live fare
   and your own ticket are three different things; never assume "same flight"
   for a group until it is confirmed.
3. **Time window.** Work back with local dates and time zones, including
   airport/station transfers and check-in deadlines. Buffers (e.g. 4 h, 90 min)
   are planning assumptions, not guarantees — check connection protection,
   separate tickets, terminals and baggage. A departure just after midnight
   means "airport the evening before".
4. **People, seats, bags.** Count per role; per person vs whole party; per
   segment carry-on and checked allowance by count, weight and size.
5. **Stay.** Nights = check-in to check-out dates. A stopover's hours are not
   nights. Confirm late check-in, luggage storage, and the gap between final
   check-out and a late-night flight.
6. **Business trips.** Separate business and personal extension segments; who
   pays; the venue and equipment; do not invent company policy or allowances;
   tourist entry status does not automatically allow work activities.

## 2. Same query, graded evidence

| Grade | Example | Use |
|---|---|---|
| live-search | metasearch or OTA results for the dates and party | shown price; not final until reproduced at the seller |
| airline-direct / provider-direct | airline, rail or hotel's own site | confirms segments, fare, bags, taxes, cancellation |
| agent-live | an agent's fare from a booking API | equal to live after matching flight number and link |
| ai-estimate | an AI answer quoting typical or past prices | comparison table only — never the basis of a recommendation |

- Send **identical conditions** to every source (party, cabin, date window,
  fixed connections, bags, currency). Hotels: room, nights, breakfast, taxes,
  cancellation.
- Cross-check several kinds of source — metasearch, OTAs, direct sites,
  maps/reviews, official information, and other AI assistants for candidates
  and contradictions. AI agreement is not live evidence; several answers citing
  one origin count as one source.
- Record each source as found / no result / access failed / unavailable / not
  checked, with time. Never report "checked everything" when some were not.
- Never paste passenger personal data, booking references or confidential
  business details into external AI comparisons.
- Representative price = the seller-confirmed summary, with time, fare class,
  reproduction path, taxes and refund conditions.
- Total for all travellers and all segments; unconfirmed hotel nights, bags or
  domestic flights are **unknown**, not zero; keep original currency with the
  exchange-rate source and time.

## 3. Choosing routes and stopovers

Apply the person's exclusions and preferences first; then offer options by
group (direct return · stopover in a preferred region · other visa-free
stopovers), always with a no-stopover baseline.

| Criterion | Question |
|---|---|
| D1 Schedule | enough buffer to the fixed connection? a day-before alternative? |
| D2 Total cost | all travellers, including separate domestic tickets and bags |
| D3 Stopover value | free or discounted stopover programmes, visa-free entry, actual hours on the ground |
| D4 Requirements | conditions for this nationality, passport type, purpose, transit vs entry, travel history |
| D5 Change risk | unprotected connections, fare rules, operating days |
| D6 Group fit | can you join the group's confirmed segment? |

Do not change an already-confirmed plan just because an alternative looks good.

## 4. Look across trips

When creating a trip, look for other trips within about ±30 days. Entry and
health requirements can depend on recent travel history (e.g. yellow-fever
countries, arrival-card history questions) — decide per route from official
sources with the check date; if not confirmed, keep `pending-official-check`.
Fees, exemptions, outbreaks and stopover programmes change: keep them as dated
evidence in the trip notes, not as fixed rules.

## Output structure

1. **Trip header** — as-of time, status per component (flight · rail · stay · documents · insurance), nearest deadline, decisions remaining.
2. **Movement comparison** — totals, exclusions, seller, flight/train numbers, local times, bags, evidence grade, reproduction path.
3. **Stay comparison** — room/party/nights, taxes, breakfast, cancellation deadline, transfer to venue.
4. **Recommendation** — one option plus up to two alternatives (all options per group if asked).
5. **Entry & health requirements** — per traveller and route, with official source and check date.
6. **Booking prep** (only if requested) — target, passengers, segments, bags, stop point before payment.

## Worked-example fragment

> *Input:* "Two of us, Seoul to Lisbon in early May, 9 nights, maybe a 2-day stopover somewhere. Compare options."

| Option | Route | Total (2 pax) | Evidence | Bags | Notes |
|---|---|--:|---|---|---|
| A · direct return | ICN–(1 stop)–LIS | observed at seller, time-stamped | airline-direct | 1×23 kg each | baseline |
| B · stopover | ICN–IST (2 nights)–LIS | observed | airline-direct | 1×23 kg | stopover programme hotel: unconfirmed |
| C · stopover | ICN–DOH (2 nights)–LIS | ai-estimate only | — | — | not reproduced → not recommended yet |

Unknown: hotel nights in the stopover city for B (listed as unknown, not 0).
Entry: Schengen visa-free stay for this nationality confirmed on the official
portal (check date); the stopover country's entry rule: `pending-official-check`.

## Constraints

- No payment, ticketing, holds or sign-ups; no entering personal data unless that booking was explicitly requested.
- No AI-estimated price used as a live fare.
- Never mix per-person and party totals in one column.
- Never decide visa or yellow-fever requirements once for a multi-stop route — check per stop.
- Do not store passport numbers, booking references, door codes or other travellers' names in shared files.

## Output format

Status header first; comparison tables with evidence grades; questions and
choices in the person's language.

## Reason codes + References

- `RC-AI-PRICE-AS-LIVE` · `RC-UNKNOWN-AS-ZERO` · `RC-MIXED-TOTALS` · `RC-SINGLE-REQUIREMENT-CHECK` ·
  `RC-UNCONFIRMED-GROUP-FLIGHT` · `RC-PAYMENT-BY-AGENT` · `RC-PII-IN-QUERY`.
- Sibling packs: [[meeting-minutes]] for trip briefings · [[report-quality]] for evidence labels.
