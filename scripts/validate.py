import json,math,hashlib
from pathlib import Path
from shapely.geometry import shape
from shapely.ops import transform,unary_union
from pyproj import Transformer
P=Path(__file__).resolve().parents[1];D=P/'data'
def read(n):return json.loads((D/n).read_text())
streams=read('streams.geojson');roads=read('roads.geojson');routes=read('routes.geojson');sites=read('inspections.geojson');t=read('terrain.json');to=Transformer.from_crs(4326,32610,always_xy=True).transform
checks=[]
def check(name,condition):
 assert condition,name
 checks.append({'check':name,'pass':True})
for name,j in [('streams',streams),('roads',roads),('routes',routes),('inspections',sites)]:
 check(name+' valid nonempty geometry',len(j['features'])>0 and all(shape(f['geometry']).is_valid and not shape(f['geometry']).is_empty for f in j['features']))
 check(name+' no duplicate geometries',len({shape(f['geometry']).wkb for f in j['features']})==len(j['features']))
check('20 unique inspection IDs',len(sites['features'])==len({f['properties']['id']for f in sites['features']})==20)
check('3 routes',len(routes['features'])==3)
s=unary_union([transform(to,shape(f['geometry']))for f in streams['features']])
for f in routes['features']:
 p=f['properties'];l=transform(to,shape(f['geometry']));ints=l.intersection(s);count=len(ints.geoms)if hasattr(ints,'geoms')else (0 if ints.is_empty else 1)
 check(p['id']+' length recomputed',abs(p['length_km']-l.length/1000)<.006)
 check(p['id']+' crossings recomputed',count==p['crossings'])
 check(p['id']+' finite profile',all(all(math.isfinite(v)for v in row) for row in p['profile']))
for f in sites['features']:
 x,y=f['geometry']['coordinates'];b=t['bbox'];check(f['properties']['id']+' within study area',b[0]<=x<=b[2] and b[1]<=y<=b[3])
check('finite terrain grid',all(math.isfinite(v)for row in t['elevation']for v in row))
check('raster grid consistent',len(t['elevation'])==t['height'] and all(len(r)==t['width']for r in t['elevation']))
# local linked assets referenced by the HTML and app.
for f in ['index.html','app.js','style.css','vendor/leaflet.js','vendor/leaflet.css','data/sources.json','esri/inspection_survey.xlsx','data/company-projects.geojson','data/news.json']:
 check('file exists '+f,(P/f).is_file())
report={'validated':'2026-11-23','checks':checks,'counts':{k:len(v['features'])for k,v in [('streams',streams),('roads',roads),('routes',routes),('inspections',sites)]},'route_metrics':[{k:v for k,v in f['properties'].items()if k!='profile'}for f in routes['features']],'browser_validation':'Not completed: preview browser could not reach local server. Check deployed GitHub Pages.'}
(D/'analysis.json').write_text(json.dumps(report,indent=2));(D/'SHA256SUMS.json').write_text(json.dumps({str(f.relative_to(P)):hashlib.sha256(f.read_bytes()).hexdigest()for f in D.glob('*')if f.is_file()and f.name!='SHA256SUMS.json'},indent=2));print('PASS',len(checks),'checks');print(json.dumps(report['route_metrics'],indent=2))
