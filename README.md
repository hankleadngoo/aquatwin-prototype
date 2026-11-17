# AquaTwin aquaculture prototype

Aquaculture monitoring and Digital Twin research prototype, with five water-quality workspaces and 24?48 hour simulation forecasts.

## Repository contents

- `aquatwin-app/`: English web interface, browser-side simulation and forecasting, local Python gateway, tests, and Ditto examples.
- `aquatwin-backend/`: standalone Python gateway, Ditto integration, data preparation, tests, and local sample data.
- `Data/`: cleaned observations and data documentation used by the prototype.
- `Bao_cao_DT_Aquaculture/`: project reports and diagrams. Reports reflect the versions described within them and may predate the current interface.
- Root Python scripts and `prototype.md`: report generation and research context. Some scripts retain original local input paths and require those source documents to regenerate reports.

## Run locally

Run `aquatwin-app/Mo_AquaTwin.cmd` on Windows for the complete prototype (http://127.0.0.1:8765).

For the standalone gateway run `aquatwin-backend/Run_Backend.cmd` (http://127.0.0.1:8770). See each folder's README for details. The standalone gateway does not serve the frontend and does not automatically replace the app's gateway.

## Data and modeling limits

The prototype contains 1,333 historical observations. The original `salinity` field represents conductivity (mS/cm); it must not be treated as salinity in oxygen-solubility calculations. Forecasts are research simulations running in the browser, not validated operational predictions. Ditto requires a separately configured local instance. The prototype does not actuate farm equipment.

VPN configuration, credentials, browser profiles, runtime files, deployment archives, and third-party source publications are excluded.


## Version 1.5.0 ? architecture alignment (2026-11-17)

Added a versioned station target/relationship profile, validated observation contract and source provenance, read-only architecture/observation/freshness APIs, an explicit research-only model boundary and the Architecture & evidence screen. See `aquatwin-app/ARCHITECTURE_ALIGNMENT.md` and `standards-traceability.csv`. This is provisional architecture alignment with ISO/IEC 30188 and adapted ISO 23247 patterns, not a complete conformity or certification claim.

Public demo: https://aquatwin-farm-observation.mellow-wave-4979.chatgpt.site/#architecture . The public demo is static; Python API/real Ditto integration requires the local gateway.
