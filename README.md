# Stantec Canada Project & GIS Explorer
Independent portfolio demonstration by Jacob Analem. Not affiliated with Stantec.

## Launch on GitHub Pages
1. Extract this ZIP.
2. Upload all contents of `stantec-explorer` into your repository root. **Upload the extracted contents, not the ZIP file.** `index.html`, `app.js`, `style.css`, `data`, `vendor`, `docs`, `scripts`, and `esri` must retain their relative paths.
3. Commit to `main`.
4. Repository Settings → Pages → Deploy from a branch → `main` → `/ (root)` → Save.
5. Open the site URL that GitHub displays after the deployment finishes. No build or API key is required for the custom app.

For local use: `python -m http.server 8000`, then open `http://localhost:8000`. Opening index.html as a file will not load GeoJSON.

## Included
- Source-linked Canadian company project explorer (curated sample, 7 projects).
- Real BC reference data: 1,019 streams and 2,300 roads, terrain and land-use raster clips.
- Three hypothetical routes, calculated measures, adjustable weighted ranking and elevation profiles.
- Twenty synthetic inspection records, local editing and photos, QA checks, CSV/GeoJSON exports, printable view.
- Data register, attribution, reproducible Python acquisition/analysis, Survey123 XLSForm and Field Maps schema.

## What remains separate
The custom interface is built with Leaflet, not Experience Builder or ArcGIS Dashboards. Native Survey123 and Field Maps require publishing using your ArcGIS organization, then configuring item IDs in Field collection. Those services are not provisioned by this ZIP. See docs/ESRI_SETUP.md.
Browser edits are saved only on the current device, not shared to GitHub or a database. Export your records. Static basemaps require internet; tiles are not bundled for offline use. Public source articles and company project facts are curated snapshots, not live feeds.

The design follows the approved two-panel concept, but the generated mock-up was illustrative. Real route measures replace invented numbers; available public terrain replaces the imagined background. No official company images/logo are reproduced.

## Data use
The source register links every external dataset. GeoJSON is EPSG:4326. Distance calculations use UTM 10N. Region: Howe Sound/Squamish training envelope [-123.20,49.68,-123.04,49.82]. The example is NOT the Brucejack alignment and does not propose a real corridor.

## Refresh analysis
Install Python dependencies: `python -m pip install -r requirements.txt`.
Run `python scripts/acquire.py`, then `python scripts/validate.py`.
Acquisition refreshes source data and replaces the bundled synthetic routes/inspection baseline. Copy your exported personal records somewhere safe first. Raster/source retrieval may change results over time. Keep the source register dates and checksums current when refreshing.

See docs/METHODS.md, docs/HANDOVER.md, and docs/ATTRIBUTION.md before using the output in a portfolio.
