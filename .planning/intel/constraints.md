# Constraints Intel

## Offline-First Local Storage Contract
- source: docs/PRD.md
- type: protocol
- content: Core functionality must operate 100% offline without accounts, backend network calls, or third-party telemetry. Storage uses serialized SQLite KV documents under `bites2go.*.v1`.

## Nutritional Snapshot Immutability
- source: docs/PRD.md
- type: schema
- content: Diary entries and recipe ingredients must preserve independent, immutable snapshots of referenced nutrition at creation time. Edits or deletions of source food definitions must never alter historical logs.

## Date and Timezone Integrity
- source: docs/PRD.md
- type: api-contract
- content: Diary and weight dates are local `YYYY-MM-DD` strings evaluated at local noon. Crossing midnight or changing timezones must never shift historical diary records. Future dates are prohibited for food logging.

## Adult Wellness Boundary
- source: docs/PRD.md
- type: nfr
- content: Product is targeted exclusively at general adult wellness (ages 20+). Clinical diagnosis, pediatric/pregnancy advice, and aggressive calorie restriction recommendations are strictly out of scope.
