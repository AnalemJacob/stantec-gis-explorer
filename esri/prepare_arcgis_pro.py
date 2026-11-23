"""Run with the ArcGIS Pro Python interpreter. Creates a geodatabase and a map layer file.
Use: python prepare_arcgis_pro.py
No ArcGIS Online publishing or credentials are included.
"""
from pathlib import Path
import arcpy
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'arcgis-output';OUT.mkdir(exist_ok=True)
gdb=OUT/'Portfolio.gdb'
if not arcpy.Exists(str(gdb)):arcpy.management.CreateFileGDB(str(OUT),gdb.name)
arcpy.env.overwriteOutput=True
for name in ['routes','inspections','streams','roads','company-projects']:
 target=str(gdb/name.replace('-','_'))
 source=json.loads((ROOT/'data'/f'{name}.geojson').read_text())
 for feature in source['features']:
  feature['properties']={k:v for k,v in feature['properties'].items() if isinstance(v,(str,int,float,bool)) or v is None}
 clean=OUT/f'{name}.geojson';clean.write_text(json.dumps(source))
 arcpy.conversion.JSONToFeatures(str(clean),target,'POINT' if name in ['inspections','company-projects']else 'POLYLINE')
 if name=='routes':
  projected=str(gdb/'routes_utm10')
  arcpy.management.Project(target,projected,arcpy.SpatialReference(32610))
  arcpy.management.AddField(projected,'check_km','DOUBLE')
  arcpy.management.CalculateGeometryAttributes(projected,[['check_km','LENGTH']],length_unit='KILOMETERS')
for name in ['elevation','slope','landuse']:
 arcpy.management.CopyRaster(str(ROOT/'data'/f'{name}.tif'),str(gdb/name))
print('Created',gdb)
print('Add these layers to an ArcGIS Pro map. Check routes_utm10.check_km against the browser metrics. Configure symbology and publish layers using your own organizational account.')
