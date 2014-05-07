# populates the landsat path/row table with statistics on the number of scenes for each path row in the L8 collection
import psycopg2, ee, earthEngine
from pyproj import Proj
from pyproj import transform
from dbconnect import dbconnect

def getProjections(crs):
        if crs.upper() == "EPSG:102100":
            p1 = Proj(init='epsg:3857')
        else:
            p1 = Proj(init=crs)
        p2 = Proj(init='epsg:4326')
        return p1, p2    

def getPointLL(point_x, point_y, crs):
        p1, p2 = getProjections(crs)
        ll_long, ll_lat = transform(p1, p2, point_x, point_y)  # transform the data to lat/long so that we can use it in Google Earth Engine
        return ll_long, ll_lat

def getScenesForPoint(collection, x, y, crs):  
    lng, lat = getPointLL(x, y, crs)
    small_query_polygon = [[[lng - 0.0001, lat + 0.0001], [lng - 0.0001, lat - 0.0001], [lng + 0.0001, lat - 0.0001], [lng + 0.0001, lat + 0.0001], [lng - 0.0001, lat + 0.0001]]]
    collection = ee.ImageCollection(collection).filterBounds(ee.Feature.Polygon(small_query_polygon))
    cloudStats = collection.aggregate_array("CLOUD_COVER").getInfo()
    scenes = collection.getInfo()['features']  # LANDSAT/LC8_L1T is USGS Landsat 8 Raw Scenes (Orthorectified)
    return len(scenes), cloudStats

earthEngine.authenticate() 
conn = dbconnect("species_especies_schema")
sql = "SELECT DISTINCT landsat_wrs2.path,landsat_wrs2.row,st_x(st_centroid(landsat_wrs2.geom)),st_y(st_centroid(landsat_wrs2.geom)) FROM especies.landsat_wrs2 where path>214 ORDER BY 1,2;"
conn.cur.execute(sql)
pathRows = conn.cur.fetchall()
for pathRow in pathRows:
    path = pathRow[0]
    row = pathRow[1]
    lng = pathRow[2]
    lat = pathRow[3]
    scenes, cloudstats = getScenesForPoint('LANDSAT/LC8_L1T_TOA', lng, lat, 'EPSG:4326')
    if len(cloudstats)>0:
        cloudstatsstr = ",".join([str(stat) for stat in cloudstats])
        sql2 = "UPDATE landsat_wrs2 SET l8_toa_scene_count=" + str(scenes) + ",l8_toa_cloud_stats=ARRAY[" + cloudstatsstr + "] WHERE path = " + str(path) + " AND row = " + str(row)
        conn.cur.execute(sql2)
        print "Processed path " + str(path) + " and row = " + str(row) + " at lng/lat " + str(lng) + "/" + str(lat) + " with " + str(scenes) + " scenes"
    else:
        print "Processed path " + str(path) + " and row = " + str(row) + " at lng/lat " + str(lng) + "/" + str(lat) + " with 0 scenes"
        sql2 = "UPDATE landsat_wrs2 SET l8_toa_scene_count=0 WHERE path = " + str(path) + " AND row = " + str(row)
        conn.cur.execute(sql2)
