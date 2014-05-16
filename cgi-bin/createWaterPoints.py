# Routine to create 10,000 water points from the water detection algorithm so we can get the accuracy of the method
import sys, json, datetime, math, psycopg2, ee, earthEngine, random
from dbconnect import dbconnect
from ee.ee_exception import EEException
collectionid = 'LANDSAT/LC8_L1T_TOA'
earthEngine.authenticate() 
# iterate through the validation sites
conn = dbconnect("species_especies_schema")
conn.cur.execute("delete from gee_validated_sites;")
sql = "SELECT DISTINCT landsat_wrs2.path,  landsat_wrs2.row,  st_x(st_centroid(landsat_wrs2.geom)),  st_y(st_centroid(landsat_wrs2.geom)), l8_toa_scene_count, l8_toa_cloud_stats FROM especies.landsat_wrs2 WHERE l8_toa_scene_count>0 ORDER BY 1,2;"
# sql = "SELECT DISTINCT landsat_wrs2.path,  landsat_wrs2.row,  st_x(st_centroid(landsat_wrs2.geom)),  st_y(st_centroid(landsat_wrs2.geom)), l8_toa_scene_count, l8_toa_cloud_stats FROM especies.landsat_wrs2 WHERE l8_toa_scene_count>0 AND path=197 and row=50 ORDER BY 1,2;"
conn.cur.execute(sql)
print "Creating random water validation sites..\n"
pathRows = conn.cur.fetchall()
for pathRow in pathRows:
    path = pathRow[0]
    row = pathRow[1]
    print "path: " + str(path) + " row: " + str(row) + "\n========================================================================================================="
    lng = pathRow[2]
    lat = pathRow[3]
    sceneCount = pathRow[4]
    cloudStats = pathRow[5]
    print "Getting scenes for " + "long: " + str(lng) + " lat: " + str(lat) + ".."
    scenes = earthEngine.getScenesForPoint(collectionid, lng, lat, 'EPSG:4326')
    mincloud = 100
    mincloudid = ''
    for scene in scenes['features']:
        if scene['properties']['WRS_ROW'] == row and scene['properties']['WRS_PATH'] == path:
            sceneid = scene['properties']["system:index"] 
            cloud = scene['properties']['CLOUD_COVER']
            if cloud < mincloud:
                mincloud = cloud
                mincloudid = sceneid
                sceneSunElevation = scene['properties']['SUN_ELEVATION']
    sceneid = mincloudid
    if sceneid:
        fullsceneid = collectionid + "/" + sceneid 
        print "Using scene " + fullsceneid 
        scene = ee.Image(fullsceneid)
        print "Water detection.."
        water = earthEngine.detectWater(scene)
        bbox = scene.geometry().getInfo()['coordinates']
        thumbnail = water.getThumbUrl({'size': '1000', 'region': bbox, 'min':0, 'max':3, 'palette': '444444,000000,ffffff,0000ff'})
        print "Water image: " + thumbnail
        try: 
            print "Getting random points in bbox " + str(bbox) + ".."
            random_points = ee.FeatureCollection.randomPoints(scene.geometry(), 1000)
            print "Getting random points which have been classified as water.."
            random_points_quantised = water.reduceRegions(random_points, ee.Reducer.first()).filter(ee.Filter.neq('first', None))
            if len(random_points_quantised.getInfo()['features']) > 0:
                for feature in random_points_quantised.getInfo()['features']:
                    coordinate = feature['geometry']['coordinates']
                    print 'long: ' + str(coordinate[0]) + ' lat: ' + str(coordinate[1]) 
                    sql2 = "INSERT INTO gee_validated_sites(objectid, gee_lat, gee_lng, predicted_class, sceneid, cloud_cover, sun_elevation,geom) VALUES (" + str(random.randrange(0, 100000000)) + "," + str(coordinate[1]) + "," + str(coordinate[0]) + ",'3','" + fullsceneid + "'," + str(mincloud) + "," + str(sceneSunElevation) + ", ST_SetSRID(ST_Point(" + str(coordinate[1]) + "," + str(coordinate[0]) + "),4326));"
                    conn.cur.execute(sql2)
            else:
                print "No points classified as water"
        except (EEException) as e:
            print e.message
            pass
        print "\n"
    else:
        print "No scenes found\n"
