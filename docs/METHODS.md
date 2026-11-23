# Analysis methods and limits

## Provenance
All records are dated as retrieved/reviewed on 23 November 2026. This is not their field acquisition date. See data/SOURCE_REGISTER.csv.
Company facts are short original paraphrases of public Stantec project pages. Coordinates are approximate map references independently assigned, not authoritative footprints. The demonstration area is separate from company projects.

## Spatial processing
- Envelope: west -123.20, south 49.68, east -123.04, north 49.82 (WGS84).
- ArcGIS REST queries use pagination until exceededTransferLimit is false, at 1,000 features/page. They return features intersecting the envelope (some full features extend outside it), not clipped geometries.
- Hypothetical route line lengths measured in EPSG:32610, metres.
- Mapped stream intersection geometries counted against a union of stream linework. These are not verified bridge counts; contacts, generalized geometry and channel representation affect counts.
- Distance to roads: straight-line minimum distance at roughly 100m route samples, averaged. Not driving distance or access permission.
- Terrain: Terrarium RGB heights decoded as R*256+G+B/256−32768. z12 tiles mosaicked and sampled onto a 160x140 regional grid. Gradients use latitude-adjusted local metre spacing; slope in degrees. This coarse method is unsuitable for foundation design, slope stability or avalanche classification.
- Sampling elevations are nearest-neighbour. The analysis grid samples its geographic endpoints, while GeoTIFF pixels occupy a bounding envelope; resulting half-cell display alignment uncertainty is about 50m. Do not use for surveying.
- AAFC 2020 land use exported with the source's simplified raster function and nearest-neighbour interpolation at 160x140. Land-use class codes and colours are supplied with the package; this is a reference overlay, not a current vegetation classification or ranking input.
- Corridor footprint approximately length × 40m; it includes water and all land classes, does not dissolve bends or represent actual clearing.

## Decision support
For each metric normalize as (value-min)/(max-min) across these three alternatives; constant metrics contribute zero. Sum the normalized terrain (fraction of samples above 30°), environmental (stream intersections), and access (mean road distance) values with slider weights normalized to sum to 1. All-zero weights use thirds. Lower is preferred within this deliberately limited screen. No protected-area exclusion, permitting rule, property right or engineering design validation is inferred. Explicitly review all routes and missing information.

## Inspections
20 synthetic training records. There were no site visits. Editing does not change the synthetic flag. Local storage is not a shared database and may be cleared by the browser. QA checks required fields and bounds only, not field accuracy. Photographs attached by users remain local and are included in JSON exports.

## Licensing
Public visibility is not a blanket reuse licence. We bundle independent factual summaries and source links, not Stantec photographs, logos or internal datasets. Government data and open libraries retain their licences; see ATTRIBUTION.md.
