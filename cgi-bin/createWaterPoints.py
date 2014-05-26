# Routine to create 10,000 water points from the water detection algorithm so we can get the accuracy of the method
import sys, json, datetime, math, psycopg2, ee, earthEngine, random
from dbconnect import dbconnect
collectionid = 'LANDSAT/LC8_L1T_TOA'
sunElevationThreshold = 42  # Landsat scenes with a solar elevation angle lower than this angle will not be considered
earthEngine.authenticate() 
# iterate through the validation sites
conn = dbconnect("species_especies_schema")
# conn.cur.execute("delete from gee_validated_sites;")
# sql = "SELECT DISTINCT landsat_wrs2.path,  landsat_wrs2.row,  st_x(st_centroid(landsat_wrs2.geom)),  st_y(st_centroid(landsat_wrs2.geom)), l8_toa_scene_count, l8_toa_cloud_stats FROM especies.landsat_wrs2 WHERE l8_toa_scene_count>0 ORDER BY 1,2;"
sql = "SELECT DISTINCT landsat_wrs2.path,  landsat_wrs2.row,  st_x(st_centroid(landsat_wrs2.geom)),  st_y(st_centroid(landsat_wrs2.geom)), l8_toa_scene_count, l8_toa_cloud_stats FROM especies.landsat_wrs2 WHERE l8_toa_scene_count>0 AND path>88 ORDER BY 1,2;"
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
            print "Water detection"
            detection = earthEngine.detectWater(scene)
            bbox = scene.geometry().getInfo()['coordinates']
            thumbnail = detection.getThumbUrl({'size': '1000', 'region': bbox, 'min':0, 'max':3, 'palette': '444444,000000,ffffff,0000ff'})
            print "Water image: " + thumbnail
            water = detection.expression("b('class')==3")
            water = water.mask(water)
            try: 
                print "Getting random points in bbox " + str(bbox)[:106] + ".."
                random_points = ee.FeatureCollection.randomPoints(scene.geometry(), 500)
                print "Getting random points classified as water.."
                random_points_quantised = water.reduceRegions(random_points, ee.Reducer.first()).filter(ee.Filter.neq('first', None))
                print "Getting lat/long data.."
                features = random_points_quantised.getInfo()['features']
                longLats = [(c['geometry']['coordinates'][0], c['geometry']['coordinates'][1]) for c in features]
                count = 1
                if len(longLats):
                    print "Getting random points classified as water.."
                    for lon, lat in longLats:
                        sql2 = "INSERT INTO gee_validated_sites(objectid, gee_lat, gee_lng, predicted_class, sceneid, cloud_cover, sun_elevation,geom) VALUES (" + str(random.randrange(0, 100000000)) + "," + str(lat) + "," + str(lon) + ",'3','" + fullsceneid + "'," + str(mincloud) + "," + str(sceneSunElevation) + ", ST_SetSRID(ST_Point(" + str(lon) + "," + str(lat) + "),4326));"
                        conn.cur.execute(sql2)
                        count = count + 1
                    print '\tTotal points: ' + str(count - 1) 
                else:
                    print "No points classified as water"
            except (Exception) as e:
                print e
                pass
            print "\n"
        else:
            print "No scenes found with sun elevation > " + str(sunElevationThreshold) + " degrees\n"
    else:
        print "No scenes found for path: " + str(path) + " row: " + str(row) + "\n"
