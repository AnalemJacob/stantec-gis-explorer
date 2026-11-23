# Native Esri setup
The web application works without these steps. They are required to claim a native Esri workflow in your application.

1. Sign into the ArcGIS Online organization available through your institution or employer. Confirm entitlement to create hosted layers and Survey123 surveys; storage may consume credits.
2. In Survey123 Connect, create a survey from `esri/inspection_survey.xlsx`. Validate and preview it, publish to your organization, and test a submission. Record its actual survey item ID. This supplied XLSForm was structurally checked but has not been published/tested in your organization.
3. Publish `data/inspections.geojson` as a hosted point feature layer. Configure fields per `fieldmaps-schema.json`, enable attachments, editor tracking, GlobalIDs and synchronization as supported. Include a record-type flag so training data remains clearly identified.
4. Create a web map with the hosted inspection layer, route layer and appropriate basemap. Configure Field Maps forms, domains and required values. If offline work is needed, configure a downloadable basemap and offline area and test download/edit/sync on a phone.
5. Use organization/group sharing for editing. If a public portfolio view is needed, publish a separate read-only feature layer view; do not expose edits or private records.
6. In the app's Field collection tab, save the published survey item ID and web map ID. Buttons open the native Esri apps. The custom local inspection records and the native hosted records remain separate; automatic two-way synchronization is not implemented.
7. Create an ArcGIS Dashboard or Experience Builder app from the hosted layers if you need to demonstrate those products. The source package does not impersonate them.

Official documentation:
- https://doc.arcgis.com/en/survey123/desktop/create-surveys/xlsformessentials.htm
- https://doc.arcgis.com/en/field-maps/latest/prepare-maps/prepare-maps-for-download.htm
- https://doc.arcgis.com/en/arcgis-online/manage-data/publish-features.htm

No credentials or API tokens belong in GitHub. Public item IDs are identifiers, not secret credentials.
