# updates database generated random lat/long values to google landsat pixel centroid values that will be returned with a call to google earth engines getRegion method
import ee, oauth2client.client, earthEngine
from dbconnect import dbconnect
from pyproj import Proj
from pyproj import transform
collectionid = 'LANDSAT/LC8_L1T_TOA'

def getPointLL(point_x, point_y, crs):
        p1, p2 = getProjections(crs)
        ll_long, ll_lat = transform(p1, p2, point_x, point_y)  # transform the data to lat/long so that we can use it in Google Earth Engine
        return ll_long, ll_lat

def getProjections(crs):
        if crs.upper() == "EPSG:102100":
            p1 = Proj(init='epsg:3857')
        else:
            p1 = Proj(init=crs)
        p2 = Proj(init='epsg:4326')
        return p1, p2    

def getScenesForPoint(collection, x, y, crs):  
    lng, lat = getPointLL(x, y, crs)
    small_query_polygon = [[[lng - 0.0001, lat + 0.0001], [lng - 0.0001, lat - 0.0001], [lng + 0.0001, lat - 0.0001], [lng + 0.0001, lat + 0.0001], [lng - 0.0001, lat + 0.0001]]]
    scenes = ee.ImageCollection(collection).filterBounds(ee.Feature.Polygon(small_query_polygon)).getInfo()  # LANDSAT/LC8_L1T is USGS Landsat 8 Raw Scenes (Orthorectified)
    return scenes
  
earthEngine.authenticate() 
collection = ee.ImageCollection([ee.Image('srtm90_v4')])
conn = dbconnect("species_especies_schema")
sql = "SELECT DISTINCT gee_random_validation_sites_subset.path,  gee_random_validation_sites_subset.row,  st_x(st_centroid(landsat_wrs2.geom)),  st_y(st_centroid(landsat_wrs2.geom)) FROM  especies.landsat_wrs2,  especies.gee_random_validation_sites_subset WHERE gee_random_validation_sites_subset.path = landsat_wrs2.path AND gee_random_validation_sites_subset.row = landsat_wrs2.row and landsat_wrs2.path > 160 order by 1,2;"
conn.cur.execute(sql)
pathRows = conn.cur.fetchall()
for pathRow in pathRows:
    path = pathRow[0]
    row = pathRow[1]
    lng = pathRow[2]
    lat = pathRow[3]
    scenes = getScenesForPoint(collectionid, lng, lat, 'EPSG:4326')
    if len(scenes['features']) > 0:
        sceneid=''
        for feature in scenes['features']:
            if feature['properties']['WRS_ROW'] == row and feature['properties']['WRS_PATH'] == path:
                sceneid = feature['properties']["system:index"]
                fullsceneid = collectionid + "/" + sceneid 
                break
        if sceneid!='':
            print "path: " + str(path) + " row: " + str(row) + " fullsceneid: " + fullsceneid
            scene = ee.Image(fullsceneid)
            collection = ee.ImageCollection(scene)
            sql2 = "SELECT * FROM gee_random_validation_sites_subset WHERE path = " + str(path) + " AND row = " + str(row)
            conn.cur.execute(sql2)
            coords = conn.cur.fetchall()
            for coord in coords:
                objectid = coord[0]
                lng = coord[2]
                lat = coord[3]
                point = ee.Geometry.Point([lng, lat])
                data = collection.getRegion(point, 30).getInfo()
                print data
                if len(data) > 1:
                    sql3 = "UPDATE gee_random_validation_sites_subset SET lng = " + str(data[1][1]) + ", lat = " + str(data[1][2]) + " WHERE objectid = " + str(objectid) + ";"
                    conn.cur.execute(sql3)
        else:
            print "path: " + str(path) + " row: " + str(row) + " no matching scenes "
