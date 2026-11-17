# Rules – Mandatory Requirements for Building an Aquaculture Digital Twin (AquaTwin)

> Source: *Digital Twin Platform Design (EN).docx*, Chapter 3 (GDT platform) and Chapter 5 (AquaTwin). Section/table numbers are given in square brackets.
> Convention: **MUST** = mandatory · **MUST NOT** = prohibited. This file records only requirements stated in the document; it does not prescribe technologies.

---

## 1. Identity and target entities

- **R1.1** Every twin **MUST** reference exactly one real target entity and one canonical twinId in the GDT core Twin Registry. [AQ-01, AR-01]
- **R1.2** AquaTwin domain profiles **MUST NOT** create an independent twin namespace; a profile that does not resolve to a canonical twinId is rejected. [Table 5.19, 5.21]
- **R1.3** Cohort–cage/tank relationships **MUST** be time-bounded: a move or restocking closes the old interval and opens a new one. History **MUST NOT** be rewritten; overlapping conflicting assignments are rejected. [5.17.4, Table 5.21]
- **R1.4** The ontology **MUST** be a versioned machine-readable artifact with SHACL-like shape validation (or equivalent tests) and named vocabulary owners. [5.17.4]

## 2. State kinds

- **R2.1** Five state kinds **MUST** be kept separate: *observed*, *estimated*, *predicted*, *simulated*, *desired*. [AQ-02, 5.17.7]
- **R2.2** Simulated or predicted state **MUST NOT** be treated as a physical measurement; cross-kind overwrites are **prohibited**. [AQ-07, Table 5.19]
- **R2.3** A simulation run **MUST** write only to the *simulated* projection. [Table 5.23]
- **R2.4** *Estimated* and *predicted* states **MUST** reference the model and the input snapshot; release is blocked if the references are missing. [Table 5.21]
- **R2.5** Historical observations, predictions, simulations and decisions **MUST** be distinguishable. [AR-11]

## 3. Observation data

- **R3.1** Every sensor record **MUST** include time, quantity, unit, location/depth and QC source. [AQ-03]
- **R3.2** The CloudEvents-style envelope **MUST** include `id, source, type, time, subject, data`. The payload **MUST** include `siteId, unitId, sensorId, parameter, value, unit, phenomenonTime, receivedAt, qualityFlag, sourceAuthority`. Optional fields: `depthM, calibrationRef, uncertainty`. [5.17.6]
- **R3.3** Schemas **MUST** be versioned; event IDs support deduplication and end-to-end tracing. [5.17.6]
- **R3.4** Records whose parameter, unit, depth or coordinates do not match the schema **MUST** be quarantined. [Table 5.21]
- **R3.5** The data mapper **MUST NOT** infer missing calibration, sample location or sensor units without a recorded transformation rule. [5.17.5]
- **R3.6** Every derived feature (e.g. from video) **MUST** link its input source, transform version, time window and quality check. [5.17.16]
- **R3.7** Audio and video files **MUST** be stored as protected objects with stable references. [5.17.16]

## 4. Synchronization and replay

- **R4.1** Each source **MUST** declare `phenomenonTime`, `ingestTime`, watermark, clock quality, revision policy and maximum acceptable staleness per use. [5.17.7]
- **R4.2** The state projector **MUST** use event-time ordering and idempotency keys. [5.17.7]
- **R4.3** Water-quality data **MUST** be replayable without silently losing or duplicating state transitions. [AQ-04]
- **R4.4** Required behaviour per scenario [Table 5.23]:

| Scenario | Required behaviour |
|---|---|
| Duplicate observation | One logical state update |
| Late but valid record | Historical correction; current state is not silently moved backwards |
| Sensor calibration expires | QC downgraded; related decisions disabled |
| Temporary edge outage | Buffered records replayed on reconnection; no silent drop |
| Simulation run | Writes only the *simulated* projection |

- **R4.5** When mandatory sensor data are missing, decisions **MUST** fail closed or escalate to humans. [5.17.7]
- **R4.6** Synchronization mechanisms **MUST** meet application-specific requirements. [AR-03]

## 5. Edge and offline operation

- **R5.1** The farm edge **MUST** buffer observations while offline and recover consistently. [AQ-09]
- **R5.2** A disconnected edge **MUST** continue approved local monitoring and keep fail-safe action boundaries. [5.17.14]
- **R5.3** Device/OT subnets **MUST** be isolated from tenant-facing cloud APIs. [5.17.14]
- **R5.4** Physical protection systems, emergency stops and local safety interlocks **MUST** remain independent of cloud availability. [5.17.8.3]

## 6. Models and VVUQ

- **R6.1** Models **MUST** declare species, site, cohort, validity domain and calibration evidence. [AQ-05]
- **R6.2** Biomass, growth and feeding predictions **MUST** show uncertainty and independent validation. [AQ-06]
- **R6.3** Models **MUST** be validated for their intended purposes. [AR-05]
- **R6.4** A model-run request **MUST** include `modelRef`/version, purpose, target units, time horizon, immutable input snapshot, parameter-set ID, site-specific validity profile and computational budget. [5.17.9]
- **R6.5** Outputs **MUST** include scenario state kind, uncertainty summary, model health indicators and provenance. [5.17.9]
- **R6.6** Model and decision results **MUST** be reproducible from pinned inputs and versions. [AQ-12]
- **R6.7** Transfer to a new site or species **MUST** require explicit recalibration and domain review. [AQ-13]
- **R6.8** Co-simulation **MUST** declare exchanged quantities, step sizes, interpolation and boundary assumptions. [5.17.9]
- **R6.9** Every biomass estimate **MUST** be associated with cohort inventory, sample protocol, time interval, prior mortality and model version. [5.17.8.2]
- **R6.10** Water-quality forecasts may be provided only after independent validation. [5.17.8.1]

## 7. Decisions and control

- **R7.1** The optimizer **MUST** return only a ranked set of feasible plans; it **MUST NOT** return actuator commands. [5.17.10]
- **R7.2** A proposal **MUST** record the affected unit/cohort, `proposedFeedKg` (where applicable), time validity, `constraintsChecked`, `modelRunId`, `uncertaintySummary` and reason. [5.17.10]
- **R7.3** The operator may approve, reject, defer or edit a plan. Model output alone does **NOT** constitute permission for automatic feeding. [5.17.10, 5.17.8.2]
- **R7.4** Feeder actuation **MUST** require authorized local operational approval. [AQ-08]
- **R7.5** Before any local actuation, the edge controller **MUST** independently validate approved identity, site time, current equipment health, sensor freshness and local interlocks. On missing or inconsistent inputs the command is blocked and an audit event is emitted. [5.17.10]
- **R7.6** Every command **MUST** pass six gates [3.18.9]:

| Gate | Validation |
|---|---|
| G1 Data and state | Source authority, freshness, measurement quality |
| G2 Model validity | Applicable model envelope, validation date, uncertainty |
| G3 Constraint safety | Hard operational/safety constraints, fallback path |
| G4 Authorization | Authorized initiator and approver; no forbidden separation-of-duties pairing |
| G5 Edge readiness | Target identity, network reachability, safe mode |
| G6 Outcome verification | Device receipt, observed effect, timeout and rollback |

- **R7.7** A command receipt is **NOT** a confirmed physical outcome; the outcome **MUST** be confirmed by a subsequent observation or other authoritative acknowledgement. [3.18.9]
- **R7.8** There **MUST NOT** be a direct AI-to-actuator path, nor uncontrolled cloud-only physical actuation. [ADR-05 in 3.18.20, Table 5.18]
- **R7.9** Operational actions **MUST** be subject to authorization and relevant safety constraints. [AR-08]
- **R7.10** Risk/welfare escalation **MUST** have a named responsible operator. [AQ-14]

## 8. Health and welfare

- **R8.1** Every health alert **MUST** document uncertainty, explanation, responsible reviewer and next-step protocol. [5.17.8.4]
- **R8.2** Treatment decisions **MUST** be made by authorized professionals; the system does **NOT** perform clinical diagnosis or automatic disease treatment. [5.17.8.4, Table 5.18]
- **R8.3** Oxygen, temperature and salinity alarm limits are **NOT** fixed by the platform; they **MUST** be approved locally for each species, life stage, method and equipment context. [5.17.8.1]
- **R8.4** No component may independently reset approval states or mute welfare alerts. [5.17.3]

## 9. Traceability

- **R9.1** Harvest lot history **MUST** survive transformation and custody transfer. [AQ-11]
- **R9.2** Each lot **MUST** carry its cohort and custody chain; unmatched downstream claims are rejected. [Table 5.21]
- **R9.3** Partial harvests, grading, lot splitting/aggregation, packaging and cold-chain handovers **MUST** have explicit derivation and custody events with timestamp, quantity/unit, responsible actor and quality evidence. [5.17.8.5]
- **R9.4** Each stage retains independent source authority; many-to-many lineage **MUST** preserve source event IDs. [5.17.4, 5.17.8.5]

## 10. Integration and data sources

- **R10.1** Source systems retain their master-data authority. [5.17.1]
- **R10.2** Connector releases **MUST** include synthetic replay tests, field schema samples, owner acceptance, retry/backoff, idempotency and an explicit dead-letter queue. [5.17.5]
- **R10.3** Interoperability mechanisms **MUST** preserve required information semantics. [AR-06]
- **R10.4** Weather, tide and satellite data **MUST** carry attribution and space/time validity. [Table 5.22]
- **R10.5** Domain modules **MUST** operate through defined platform interfaces; deploying a domain twin **MUST NOT** require unnecessary modifications to the shared core. [AR-04, AR-12]
- **R10.6** A change to the core API major version **MUST** be compatibility-tested before any domain deployment. [5.17.2]

## 11. Federation, security and privacy

- **R11.1** Federation **MUST** respect source authority and cross-operator data rights. [AQ-10, AR-07]
- **R11.2** Partners receive only approved fields, precision and time windows; production, disease and commercial data stay restricted. [5.17.12]
- **R11.3** Federated discoverability does **NOT** imply permission to infer sensitive details from aggregated responses. [5.17.12]
- **R11.4** The federation test suite **MUST** verify revocation, audit trails, policy-change propagation, schema preservation and resilience to partner network failures. [5.17.12]
- **R11.5** Mandatory security controls [Table 5.25]:

| Threat / misuse | Mitigation |
|---|---|
| Spoofed sensor or drift | Device identity, QC, calibration, anomaly detection |
| Unauthorized command | Role/scope control, local actuation authorization |
| Cross-farm information leak | Tenant isolation, data minimization, audit |
| Model poisoning / version drift | Version pinning, training provenance, rollback |
| Network outage | Store-and-forward, local controls, recovery procedure |
| Video privacy breach | Access control, capture minimization, retention policy |

- **R11.6** API clients **MUST** use OAuth2 scopes and request IDs; every read, run, proposal and approval **MUST** be correlated in audit records. [5.17.11]
- **R11.7** Retention is configurable by the data owner; deletion and legal-hold policies **MUST** distinguish personal data, commercial records, scientific reproducibility and safety audit artifacts. [5.17.16]

## 12. Lifecycle, performance and acceptance

- **R12.1** The platform **MUST** support lifecycle and version management (upgrade, rollback, retirement). [AR-09]
- **R12.2** Services **MUST** have defined availability, scalability and resilience targets. [AR-10]
- **R12.3** SLOs **MUST** be tied to the use case and **MUST NOT** be copied from generic cloud specifications. [AQ-15]
- **R12.4** Every component **MUST** declare API version, data classification, permitted operations, external dependencies, failure modes, regression tests and model-validation state. [5.17.3]
- **R12.5** An acceptance gate **MUST** be backed by an actual test report (software versions, environment, inputs, reviewer approval), not merely a successful example schema validation. [5.17.17]
- **R12.6** Every claim of ISO alignment **MUST** have verifiable implementation traceability; architectural alignment is **NOT** a certification claim. [AQ-16, 5.17.21]
- **R12.7** Models and states **MUST** be linked to declared sources and versions. [AR-02]

## 13. Out of scope (MUST NOT do)

[Table 5.18]

- Replace licensed safety PLCs or vendor firmware.
- Perform clinical diagnosis or automatic disease treatment.
- Allow uncontrolled cloud-only physical actuation.
- Presume access to supplier, processor or retailer systems.
- Assume that partner APIs, data licenses or validation have been approved.

## 14. Phase gates

[Table 5.17]

| Phase | Exit criteria |
|---|---|
| P0 Requirements and source audit | Approved use cases, safety boundaries, quality baseline |
| P1 Observation DT | AQ-01..AQ-04 and AQ-09 pass |
| P2 Model-based DT | Independent VVUQ approval and declared domain scope |
| P3 Decision support | AQ-06..AQ-08 and AQ-12 pass; welfare approval |
| P4 Integrated FarmOS | Validated operational workflow and outcome logs |
| P5 Multi-site and supply chain | AQ-10..AQ-16 pass; portability and economics evidence |

Any addition of autonomous operations is a separately governed scope change and **MUST** be backed by new assurance evidence. [5.17.22]


## 15. Standards traceability boundary ? 2026-11-17

The R* rules above are project-design requirements, not verbatim normative ISO clauses. Implementation mapping is maintained in `aquatwin-app/standards-traceability.csv` using project IDs AT-xx, with incomplete evidence explicitly marked. `ARCHITECTURE_ALIGNMENT.md` separates ISO/IEC 30188 viewpoints from the ISO 23247 manufacturing adaptation. A licensed-text clause review and independent reviewer signoff remain pending; no full conformity claim is made.
