# AquaTwin 1.4 — English interface

The entire application interface is now English: farm overview, five monitoring areas, 24/48-hour simulation forecasts, quality flags, forms, guidance, exports, technical tools and local Ditto gateway errors.

Raw observation values, source identifiers, timestamps, QC results and forecasting calculations are unchanged. Existing user-authored logbook notes are preserved as entered; changing interface language does not translate private user content.

## Run locally

Double-click `Mo_AquaTwin.cmd`, or run `python server.py` and open http://127.0.0.1:8765 . The launcher reuses the local gateway. Browser data and trial ranges remain local to each origin.

## Public prototype

https://aquatwin-farm-observation.mellow-wave-4979.chatgpt.site

The public site serves a historical snapshot of 1,333 real records. It does not connect to local Ditto or actuate equipment. Simulation forecasts are experimental, not independently validated operational predictions. Conductivity is in mS/cm; the original `salinity` key must not be interpreted as Practical Salinity.

## Checks

`node tests.cjs`, `node forecast-tests.cjs`, `node english-tests.cjs`, and `python -m unittest test_bridge.py` cover core behavior, simulation, interface language and the mock Ditto bridge. `node browser_test.cjs` tests desktop/mobile interactions and the English technical screens with an isolated local Chrome QA session.
