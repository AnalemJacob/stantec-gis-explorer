import sys,os,json,urllib.request,urllib.parse,concurrent.futures,math,io,time
from pathlib import Path
import numpy as np
from PIL import Image
import rasterio
from rasterio.transform import from_bounds
from shapely.geometry import shape,LineString,mapping,Point
from shapely.ops import transform,unary_union
from pyproj import Transformer
ROOT=Path(__file__).resolve().parents[1]; D=ROOT/'data'; D.mkdir(exist_ok=True)
B=[-123.20,49.68,-123.04,49.82]
def fetch(u):
 for attempt in range(3):
  try:return urllib.request.urlopen(u,timeout=80).read()
  except Exception:
   if attempt==2:raise

def dump(n,j): (D/n).write_text(json.dumps(j,separators=(',',':')))
def query(layer,name):
 base=f'https://delivery.maps.gov.bc.ca/arcgis/rest/services/mpcm/bcgwpub/MapServer/{layer}/query'
 p=dict(f='geojson',where='1=1',geometry=','.join(map(str,B)),geometryType='esriGeometryEnvelope',inSR=4326,spatialRel='esriSpatialRelIntersects',outSR=4326,outFields='*',resultRecordCount=1000,geometryPrecision=6)
 allfeatures=[]
 for offset in range(0,20000,1000):
  p['resultOffset']=offset
  page=json.loads(fetch(base+'?'+urllib.parse.urlencode(p)))
  assert 'features'in page,page
  allfeatures.extend(page['features'])
  if not page.get('exceededTransferLimit'):break
 else:raise RuntimeError('More than 20,000 features; reduce area')
 j={'type':'FeatureCollection','features':allfeatures}
 for f in j['features']:
  pr=f['properties'];f['properties']={k:v for k,v in pr.items() if k in ['GNIS_NAME','BLUE_LINE_KEY','EDGE_TYPE','ROAD_NAME_ALIAS1','FEATURE_TYPE','SEGMENT_LENGTH_2D','OBJECTID','LENGTH_METRE']}
 dump(name+'.geojson',j);print(name,len(j['features']),flush=True)
with concurrent.futures.ThreadPoolExecutor() as ex:list(ex.map(lambda x:query(*x),[(56,'streams'),(464,'roads')]))
# Terrain RGB tiles: real elevation mosaic, resampled to approximately 100m.
z=12
lonx=lambda lon:(lon+180)/360*2**z
laty=lambda lat:(1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*2**z
x0,x1=math.floor(lonx(B[0])),math.floor(lonx(B[2]));y0,y1=math.floor(laty(B[3])),math.floor(laty(B[1]))
mos=Image.new('RGB',((x1-x0+1)*256,(y1-y0+1)*256))
def tile(xy):
 x,y=xy;u=f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png';return x,y,Image.open(io.BytesIO(fetch(u))).convert('RGB')
with concurrent.futures.ThreadPoolExecutor() as ex:
 for x,y,im in ex.map(tile,[(x,y)for x in range(x0,x1+1)for y in range(y0,y1+1)]):mos.paste(im,((x-x0)*256,(y-y0)*256))
a=np.asarray(mos).astype(float);h=a[:,:,0]*256+a[:,:,1]+a[:,:,2]/256-32768
# sample regularly in WGS84 and derive gradients using local metre spacing
W,H=160,140
lons=np.linspace(B[0],B[2],W);lats=np.linspace(B[3],B[1],H)
ix=np.clip(np.array([(lonx(l)-x0)*256 for l in lons],int),0,h.shape[1]-1);iy=np.clip(np.array([(laty(l)-y0)*256 for l in lats],int),0,h.shape[0]-1)
elev=h[np.ix_(iy,ix)]
dx=(B[2]-B[0])*111320*math.cos(math.radians(49.75))/(W-1);dy=(B[3]-B[1])*111320/(H-1)
gy,gx=np.gradient(elev,dy,dx);slope=np.degrees(np.arctan(np.hypot(gx,gy)))
with rasterio.open(D/'elevation.tif','w',driver='GTiff',height=H,width=W,count=1,dtype='float32',crs='EPSG:4326',transform=from_bounds(*B,W,H),compress='deflate') as ds:ds.write(elev.astype('float32'),1)
with rasterio.open(D/'slope.tif','w',driver='GTiff',height=H,width=W,count=1,dtype='float32',crs='EPSG:4326',transform=from_bounds(*B,W,H),compress='deflate') as ds:ds.write(slope.astype('float32'),1)
# visualization image
rgba=np.zeros((H,W,4),dtype=np.uint8);rgba[:,:,:3]=[211,99,44];rgba[:,:,3]=np.where(slope>30,160,np.where(slope>15,75,0));Image.fromarray(rgba).save(D/'slope.png')
# AAFC classified land use TIFF clip, nearest neighbour, real source values.
base='https://agriculture.canada.ca/imagery-images/rest/services/landuse_30m/2020/ImageServer'
p=dict(f='json',bbox=','.join(map(str,B)),bboxSR=4326,imageSR=4326,size=f'{W},{H}',format='tiff',pixelType='U8',interpolation='RSP_NearestNeighbor',renderingRule=json.dumps({'rasterFunction':'landuse_30m_simplified'}))
j=json.loads(fetch(base+'/exportImage?'+urllib.parse.urlencode(p)));assert 'href'in j,j
(D/'landuse.tif').write_bytes(fetch(j['href']))
with rasterio.open(D/'landuse.tif') as ds:
 land=ds.read(1); print('land classes',np.unique(land),flush=True)
 book=json.loads(fetch(base+'/rasterAttributeTable?f=json&'+urllib.parse.urlencode({'renderingRule':json.dumps({'rasterFunction':'landuse_30m_simplified'})})))
 dump('landuse-codebook.json',book)
 cm={f['attributes']['Value']:(f['attributes']['Red'],f['attributes']['Green'],f['attributes']['Blue'],175) for f in book['features']}
 lc=np.zeros((H,W,4),dtype=np.uint8)
 for val in np.unique(land):lc[land==val]=cm.get(int(val),(100,155,85,140))
 lc[:,:,3]=175;Image.fromarray(lc).save(D/'landuse.png')
# persist source metadata for all downloaded bytes
terrain=dict(bbox=B,width=W,height=H,elevation=np.round(elev,1).tolist(),slope=np.round(slope,1).tolist(),landuse=land.tolist(),landuseClasses=[int(x)for x in np.unique(land)],retrieved='2026-11-23')
dump('terrain.json',terrain)
# Hypothetical comparison lines in the real study area; NOT Stantec alignments.
coords=[ [[-123.185,49.70],[-123.16,49.728],[-123.125,49.75],[-123.09,49.775],[-123.055,49.80]], [[-123.185,49.70],[-123.147,49.716],[-123.113,49.735],[-123.075,49.766],[-123.055,49.80]], [[-123.185,49.70],[-123.177,49.744],[-123.151,49.775],[-123.102,49.794],[-123.055,49.80]] ]
to=Transformer.from_crs(4326,32610,always_xy=True).transform;back=Transformer.from_crs(32610,4326,always_xy=True).transform
streams=json.loads((D/'streams.geojson').read_text());roads=json.loads((D/'roads.geojson').read_text());ss=unary_union([transform(to,shape(f['geometry']))for f in streams['features'] if f['geometry']]);rr=unary_union([transform(to,shape(f['geometry']))for f in roads['features']if f['geometry']])
features=[];sites=[]
for i,c in enumerate(coords):
 line=LineString(c);pl=transform(to,line);n=round(pl.length/100)+1;profile=[]
 for k in range(n):
  pt=transform(back,pl.interpolate(pl.length*k/(n-1)));col=min(W-1,max(0,round((pt.x-B[0])/(B[2]-B[0])*(W-1))));row=min(H-1,max(0,round((B[3]-pt.y)/(B[3]-B[1])*(H-1))));profile.append([round(pl.length*k/(n-1)),float(elev[row,col]),float(slope[row,col]),int(land[row,col]),round(Point(*to(pt.x,pt.y)).distance(rr))])
 ints=pl.intersection(ss);count=len(ints.geoms)if hasattr(ints,'geoms') else (0 if ints.is_empty else 1)
 props=dict(id=chr(65+i),synthetic=True,length_km=round(pl.length/1000,2),crossings=count,steep_pct=round(100*sum(p[2]>30 for p in profile)/n,1),mean_access_m=round(sum(p[4]for p in profile)/n),corridor_ha=round(pl.length*40/10000,1),profile=profile)
 features.append(dict(type='Feature',geometry=mapping(line),properties=props))
 for k in range(7 if i<2 else 6):
  pt=transform(back,pl.interpolate(pl.length*(k+1)/(8 if i<2 else 7)));idx=len(sites)+1
  sites.append(dict(type='Feature',geometry=mapping(pt),properties=dict(id=f'INS-{idx:03}',route=chr(65+i),synthetic=True,status='Inspected'if idx<=12 else 'Awaiting inspection',issue='Erosion observed'if idx in [2,5,8,11,14,18]else 'Routine crossing check',priority='High'if idx in [5,14]else 'Normal',action='Open'if idx in [2,5,8,11,14,18]else 'None',verified=idx%5!=0,due='2026-11-25',notes='Synthetic training record; no field visit occurred.')))
dump('routes.geojson',dict(type='FeatureCollection',features=features));dump('inspections.geojson',dict(type='FeatureCollection',features=sites));print('analysis complete',[(f['properties']['id'],f['properties']['crossings'])for f in features],flush=True)
# vendored libraries, preserving licenses
for name,u in [('leaflet.js','https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'),('leaflet.css','https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'),('leaflet-LICENSE','https://unpkg.com/leaflet@1.9.4/LICENSE')]:
 (ROOT/'vendor'/name).write_bytes(fetch(u))
