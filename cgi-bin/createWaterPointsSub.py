import sys, json, datetime, math, psycopg2, ee, earthEngine, random, urllib
from dbconnect import dbconnect
COLLECTIONID = 'LANDSAT/LC8_L1T_TOA'
RANDOM_POINT_COUNT = 500
SUN_ELEVATION_THRESHOLD = 42  # Landsat scenes with a solar elevation angle lower than this angle will not be considered
WATER_CLASS_ID = 3

def createPoints(path, row):
    earthEngine.authenticate() 
    scenes = earthEngine.getScenesForPoint(COLLECTIONID, path, row, 'EPSG:4326')
    mincloud = 100
    mincloudid = ''
    if len(scenes['features']) > 0:
        for scene in scenes['features']:
            if scene['properties']['WRS_ROW'] == row and scene['properties']['WRS_PATH'] == path:
                sceneSunElevation = scene['properties']['SUN_ELEVATION']
                if sceneSunElevation > SUN_ELEVATION_THRESHOLD:
                    sceneid = scene['properties']["system:index"] 
                    cloud = scene['properties']['CLOUD_COVER']
                    if cloud < mincloud:
                        mincloud = cloud
                        mincloudid = sceneid
        sceneid = mincloudid
        if sceneid:
            fullsceneid = COLLECTIONID + "/" + sceneid 
            print "Using scene " + fullsceneid 
            try: 
                scene = ee.Image(fullsceneid)
                print "Water detection.."
                detection = earthEngine.detectWater(scene)
                bbox = scene.geometry().getInfo()['coordinates']
    #                 thumbnail = detection.getThumbUrl({'size': '1000', 'region': bbox, 'min':0, 'max':3, 'palette': '444444,000000,ffffff,0000ff'})
    #                 print "Water image: " + thumbnail
    #                 urllib.urlretrieve (thumbnail, r'../../htdocs/mstmp/' + sceneid + ".jpg") #if you want to retrieve the image
                print "Getting random points in bbox " + str(bbox)[:106] + ".."
                random_points = ee.FeatureCollection.randomPoints(scene.geometry(), RANDOM_POINT_COUNT)
                random_points_quantised = detection.reduceRegions(random_points, ee.Reducer.first()).filter(ee.Filter.eq('first', WATER_CLASS_ID))  # class 3 is water
                print "Getting random points classified as water.."
                features = random_points_quantised.getInfo()['features']
                print "Getting the long/lat values.."
                longLats = [(c['geometry']['coordinates'][0], c['geometry']['coordinates'][1]) for c in features]
                count = 1
                if len(longLats):
                    for lon, lat in longLats:
                        sql2 = "INSERT INTO gee_validated_sites(objectid, gee_lat, gee_lng, predicted_class, sceneid, cloud_cover, sun_elevation,geom) VALUES (" + str(random.randrange(0, 100000000)) + "," + str(lat) + "," + str(lon) + ",'3','" + fullsceneid + "'," + str(mincloud) + "," + str(sceneSunElevation) + ", ST_SetSRID(ST_Point(" + str(lon) + "," + str(lat) + "),4326));"
                        conn.cur.execute(sql2)
                        count = count + 1
                    print '\tTotal points: ' + str(count - 1) 
                else:
                    print "\tNo points"
            except (Exception) as e:
                print e
                pass
        else:
            print "No scenes found with sun elevation > " + str(SUN_ELEVATION_THRESHOLD) + " degrees"
    else:
        print "No scenes found for path: " + str(path) + " row: " + str(row)      

if __name__ == "__main__":
    args = sys.argv
    createPoints(args[1],args[2])