# Routine to create 10,000 water points from the water detection algorithm so we can get the accuracy of the method
import sys, json, datetime, math, psycopg2, ee, earthEngine, random
from dbconnect import dbconnect
from ee import EEException

def getpoints(image):
  random_points = ee.FeatureCollection.randomPoints(image.geometry(), 500)
  waterpoints = image.reduceRegions(random_points, ee.Reducer.first()).filter(ee.Filter.neq('first', None))
  return waterpoints

collectionid = 'LANDSAT/LC8_L1T_TOA'
sunElevationThreshold = 42  # Landsat scenes with a solar elevation angle lower than this angle will not be considered
earthEngine.authenticate() 
conn = dbconnect("species_especies_schema")
print "Creating random water validation sites\n"
for path in range(1, 234):  # 1, 234
    waterDetections = []
    try:
        for row in range(1, 123):  # 1,123
            sql = "SELECT st_x(st_centroid(landsat_wrs2.geom)),  st_y(st_centroid(landsat_wrs2.geom)) FROM especies.landsat_wrs2 WHERE path=" + str(path) + " and row=" + str(row)
            conn.cur.execute(sql)
            pathRow = conn.cur.fetchall()
            print "path: " + str(path) + " row: " + str(row) + "\n========================================================================================================="
            lng = pathRow[0][0]
            lat = pathRow[0][1]
            scenes = earthEngine.getScenesForPoint(collectionid, lng, lat, 'EPSG:4326')
            mincloud = 100
            mincloudid = ''
            if len(scenes['features']) > 0:
                for scene in scenes['features']:
                    if scene['properties']['WRS_ROW'] == row and scene['properties']['WRS_PATH'] == path:
                        sceneSunElevation = scene['properties']['SUN_ELEVATION']
                        if sceneSunElevation > sunElevationThreshold:
                            sceneid = scene['properties']["system:index"] 
                            cloud = scene['properties']['CLOUD_COVER']
                            if cloud < mincloud:
                                mincloud = cloud
                                mincloudid = sceneid
                sceneid = mincloudid
                if sceneid:
                    fullsceneid = collectionid + "/" + sceneid 
                    print "Using scene " + fullsceneid 
                    scene = ee.Image(fullsceneid)
                    print "Water detection\n"
                    detection = earthEngine.detectWater(scene)
                    water = detection.expression("b('class')==3")
                    water = water.mask(water)
                    waterDetections.append(water)
                else:
                    print "No scenes found with sun elevation > " + str(sunElevationThreshold) + " degrees\n"
            else:
                print "No scenes found for path: " + str(path) + " row: " + str(row) + "\n"
        waterDetectionsCollection = ee.ImageCollection(waterDetections)
        waterpoints = waterDetectionsCollection.map(getpoints).flatten()
        try:
            print str(len(waterpoints.getInfo()['features'])) + " water points detected in path " + str(path)
            longLats = [(c['geometry']['coordinates'][0], c['geometry']['coordinates'][1]) for c in waterpoints.getInfo()['features']]
            count = 1
            if len(longLats):
                for lon, lat in longLats:
                    sql2 = "INSERT INTO gee_validated_sites(objectid, gee_lat, gee_lng, predicted_class, sceneid, cloud_cover, sun_elevation,geom) VALUES (" + str(random.randrange(0, 100000000)) + "," + str(lat) + "," + str(lon) + ",'3','" + fullsceneid + "'," + str(mincloud) + "," + str(sceneSunElevation) + ", ST_SetSRID(ST_Point(" + str(lon) + "," + str(lat) + "),4326));"
                    conn.cur.execute(sql2)
                    count = count + 1
                print '\tTotal points: ' + str(count - 1) 
        except (EEException) as e:
            print e
    except (EEException) as e:
        print e
