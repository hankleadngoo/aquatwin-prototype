# AquaTwin architecture alignment — implementation 1.5.0

Updated 2026-11-17. This is a local implementation update, not a new hosted deployment.

## 1. Scope and standards basis

ISO/IEC 30188:2026 is the general reference-architecture basis. ISO 23247 Parts 1–4 (2021) are adapted as a manufacturing-specific pattern, not claimed as an aquaculture standard. Part 2 informs functional/entity allocation, Part 3 information attributes and Part 4 information exchange. ISO 23247 is a series, not just Part 3. This mapping is provisional, based on the project design document and public standard scopes; a full licensed-text clause review and reviewer signoff remain pending. No certification or complete conformity is claimed.

Sources: https://www.iso.org/standard/53308.html, https://www.iso.org/standard/75066.html, https://www.iso.org/standard/78743.html, https://www.iso.org/standard/78744.html, https://www.iso.org/standard/78745.html.

Project choices such as JSON envelopes, REST, Ditto, QC, a 1,800-second staleness limit and state labels are application contracts. They must not be attributed as verbatim ISO mandates.

## 2. Target and entity model

`dist/architecture-profile.json` is the versioned, single-target local registry. The target is the water-quality observation station `urn:aquatwin:station:nuoibien-2`, represented by Ditto Thing `aquatwin:nuoibien-2`. A station is not a whole-farm behavioral model. Site and acquisition device are explicitly related. Individual probe identities, location, depth, calibration and relationship validity intervals remain unknown. No cage, stock or biomass identity is invented.

The local registry is not a global GDT Twin Registry. An approved profile revision is required before introducing metadata or another target; the runtime rejects other source identities and units.

## 3. Functional allocation (ISO 23247 adaptation)

| Responsibility | Component | Boundary |
|---|---|---|
| Observable domain | Physical station and acquisition device | Outside the software; no field connector in this checkout |
| Device communication entity | `prepare_data.py`, snapshot adapter in `standards.py` | Historical source only |
| Digital twin entity | `server.snapshot`, `core.currentTwin`, Ditto adapter, research simulator | Current state and isolated research simulation |
| User entity | Existing web workspace and Architecture & evidence view | Historical data; human interpretation |
| Cross-system entity | Local origin checks, Ditto Policy, source/profile validation | Partial; no production tenant governance |

## 4. ISO/IEC 30188 viewpoints

Foundational: declared target identity, state kinds, source authority and synchronization scope in the profile. Functional: observation validation, QC projection, model use gate and user access. Implementation: explicit interfaces in `openapi.json`, local gateway–Ditto connection, snapshot UI and model contract. Architecture pattern: this station-observation specialization and its known gaps. These viewpoints are not the three functional/information/networking views of ISO 23247 and are not a mandatory six-layer software stack.

## 5. State and observation contracts

`schemas/observation.schema.json` documents the envelope. `standards.validate_observation` enforces project semantics before Python projection: registered source/target, known quantity/unit, finite numeric or null values, missing flag consistency, source time, provenance and deterministic observation ID. Booleans and NaN are rejected. Unknown metadata remains null; `receivedAt` is unavailable in this historical source and must not be replaced by replay time. Device identifiers refer to acquisition devices, not verified individual probes.

`observed`, `estimated`, `predicted`, `simulated` and `desired` are declared separately. This gateway produces only observed projections. Research simulator outputs are `simulated`, include model version, input snapshot, training window, seed and validation status, and are not written into Thing observations. This checkout does not implement PSS-78 estimated values or a predicted-state service.

## 6. Synchronization and interfaces

GET `/api/architecture`: local profile. GET `/api/observations?cursor=N`: five validated events at a historical cursor. GET `/api/state/health`: wall-clock age of the latest snapshot observation, stale status and clock warning, not a declaration of the age of an independently running Ditto instance. All are read-only and share existing local Host/Origin validation. POST `/api/ditto/sync` remains observed-only; ETag protects concurrent updates, source-time guard prevents rollback, duplicate snapshots do not write, readback verifies features, unrelated attributes/features are preserved. Owned architecture metadata is upgraded on sync.

The 30-minute staleness bound is provisional project configuration, not an ISO value or fish-safety threshold. Freshness is computed on GET/UI render rather than embedded in idempotent snapshots. No live ingest service, append-only revision history, formal watermark, event bus, offline edge buffer or production authentication is implemented here. `openapi.json` is the HTTP contract; view labels describe architectural responsibilities, not four physically deployed networks.

## 7. Model validity and decision boundary

`water-scenario-1.0` remains a research-only statistical simulator. `simulate` rejects any explicit purpose other than `research-simulation`; output declares operational use and actuation false. `standards-core.modelGate` exposes the same boundary for consumers. This is an application-level research guard, not a security sandbox against a user modifying JavaScript. No actuator endpoint exists. Operational release requires independent validation and an approved site/species envelope; current backtest does not provide it.

## 8. Verification and remaining work

Run `npm test` in this folder. Tests exercise invalid identities/units, missing data, cross-kind rejection, stale/future clocks, duplicate/late/conflict handling, preservation of foreign fields and model purpose gates. Results are in `standards-verification.json` after the verification runner. These tests validate implementation rules, not every normative ISO clause.

The newer MinIO/TimescaleDB/FastAPI pipeline described in `1611_tien_do/prototype.md` is not present in this checkout. Its 115 pytest claims cannot be incorporated as fresh evidence. Next steps: obtain its pinned source and reports; complete metadata and calibration; map licensed standard clauses to code/test evidence; implement lifecycle/retirement/rollback, revision storage and edge recovery; then independently review acceptance criteria. Historical progress reports are preserved as historical artifacts.
