import sys, json, datetime, math, psycopg2, ee, earthEngine
from pyproj import Proj
from pyproj import transform
from dbconnect import dbconnect
earthEngine.authenticate() 
startDate = datetime.datetime(2013, 10, 25)
endDate = datetime.datetime(2013, 11, 11)
applyCloudMask = True  # Set to 1 to apply a cloud mask
applySlopeMask = False  # Set to 1 to apply a slope mask
applyNDVIMask = True  # Set to 1 to apply an ndvi mask
applyBareRockMask = True  # Set to 1 to apply a bare rock mask
applyTemperatureMask = True  # Set to 1 to apply a temperature mask
slopeMaskThreshold = 0.17  # Pixels with a slope greater than this threshold in radians will be excluded
ndviMaskThreshold = 0.1  # Pixels with an NDVI greater than this threshold will be excluded
annualMaxTempThreshold = 310  # Threshold for the max annual temperature above which bare rock could be present
annualMaxNDVIThreshold = 0.14  # Threshold for the max annual NDVI below which bare rock will be present
lowerSceneTempThreshold = 272.15  # lower temperature threshold for the scene
upperSceneTempThreshold = 308  # upper temperature threshold for the scene
temperatureDifferenceThreshold = 9  # Pixels with a day/night temperature difference greater than this threshold will be excluded
sunElevationThreshold = 42  # Landsat scenes with a solar elevation angle greater than this angle will be included
collectionid = 'LANDSAT/LC8_L1T_TOA'
detectionExpressions = [
  {"bands":"754", "expression":"((b('h')<(3.038667895460303*b('v'))+236.62216730574633)&&(b('h')<(10796.714793390856*b('v'))+204.85937891753062)&&(b('h')>(52.75476688685699*b('v'))+209.3760200216838))||((b('h')>(3.038667895460303*b('v'))+236.62216730574633)&&(b('h')<(2.0464628168010686*b('v'))+237.16593011613543)&&(b('h')<(9.076683306759795*b('v'))+236.60439910485127))||((b('h')<(-0.24666028009321075*b('v'))+238.42264113944557)&&(b('h')<(9.88710145914933*b('v'))+236.539667859889)&&(b('h')>(2.0464628168010686*b('v'))+237.1659301161354))||((b('h')>(-43.65372607478519*b('v'))+209.41654907810485)&&(b('h')<(-11433.100423818365*b('v'))+6504.023197860868)&&(b('h')<(52.75476688685699*b('v'))+209.3760200216838))||((b('h')>(26.243531044391943*b('v'))+170.78642497548128)&&(b('h')<(-43.65372607478519*b('v'))+209.41654907810485)&&(b('h')>(-1107.3553634247025*b('v'))+209.86371739648635))||((b('h')>(295.7226981444027*b('v'))+21.853346666047287)&&(b('h')<(26.243531044391943*b('v'))+170.78642497548128)&&(b('h')>(8.433335884642577*b('v'))+171.4003760014821))||((b('h')<(8.433335884642577*b('v'))+171.4003760014821)&&(b('h')>(-31.37019423910757*b('v'))+172.77247877400865)&&(b('h')>(82.71930111287884*b('v'))+132.73119126796098))||((b('h')<(-31.37019423910757*b('v'))+172.77247877400865)&&(b('h')>(-115.8110462176276*b('v'))+175.68331423895395)&&(b('h')>(4.932732579069547*b('v'))+160.0314641384984))||((b('h')<(-115.8110462176276*b('v'))+175.68331423895395)&&(b('h')>(-212.72738738403356*b('v'))+179.02420335115374)&&(b('h')>(7.045573926497733*b('v'))+159.75757941842787))"},
  {"bands":"732 S and V", "expression":"((b('s')>(0.3402310087582287*b('v'))+0.6878785247108777)&&(b('s')<(-0.22139589479141922*b('v'))+1.0009733932691036)&&(b('s')<(114.04465599671092*b('v'))+0.38090113543454673))||((b('s')>(11.178032732580114*b('v'))-5.353961858528813)&&(b('s')<(0*b('v'))+0.9997719738616231)&&(b('s')>(-0.22139589479141922*b('v'))+1.0009733932691036))||((b('s')>(-6.555760168973008*b('v'))+0.706496211475811)&&(b('s')>(0.9781716036464391*b('v'))+0.33224042147527677)&&(b('s')<(0.3402310087582287*b('v'))+0.6878785247108777))||((b('s')>(0.19217317709040418*b('v'))+0.37128569968432384)&&(b('s')>(1.539711633483847*b('v'))+0.019193983135302795)&&(b('s')<(0.9781716036464391*b('v'))+0.33224042147527677))||((b('s')<(0.19217317709040418*b('v'))+0.37128569968432384)&&(b('s')>(-0.21980966748266745*b('v'))+0.3917513701490769)&&(b('s')>(0.4354503844174411*b('v'))+0.307720990923226))"},
  ]
def convertToHsv(image, bands):
  # Get the relevant bands for the hsv conversion
  r = 'B' + bands[0:1]
  g = 'B' + bands[1:2]
  b = 'B' + bands[2:3]
  image = ee.Image.cat([image.select([r], ['r']), image.select([g], ['g']), image.select([b], ['b'])])
  # Value computation
  maxRGB = image.reduce(ee.Reducer.max())
  minRGB = image.reduce(ee.Reducer.min())
  value = maxRGB
  # Saturation computation
  saturation = value.subtract(minRGB).divide(value)
  # Hue computation
  g_b = image.select(['g'], ['g_b']).subtract(image.select('b'))
  b_r = image.select(['b'], ['b_r']).subtract(image.select('r'))
  r_g = image.select(['r'], ['r_g']).subtract(image.select('g'))
  hue_input = ee.Image([minRGB, image, value.select(['max'], ['value']), g_b, b_r, r_g])
  hueRed = hue_input.expression("(b('value')==b('r'))*(((60*(b('g_b')/(b('value')-b('min'))))+360)%360)")
  hueGreen = hue_input.expression("(b('value')==b('g'))*((60*(b('b_r')/(b('value')-b('min'))))+120)")
  hueBlue = hue_input.expression("(b('value')==b('b'))*((60*(b('r_g')/(b('value')-b('min'))))+240)")
  hue = ee.Image([hueRed, hueGreen, hueBlue]).reduce(ee.Reducer.max())
  # return the hsv image
  return ee.Image([hue.select(['max'], ['h']), saturation.select(['max'], ['s']), value.select(['max'], ['v'])])

def getCompositeData():
    if not applyCloudMask:
        return landsat_collection.mean()
    images = []
    for feature in landsat_collection.getInfo()['features']:
        image = ee.Image(feature['id'])
        tempMask = image.expression('b("B10")<' + str(lowerSceneTempThreshold))
        ndvi = image.normalizedDifference(["B5", "B4"])
        ndviMask = ndvi.expression('b("nd")<0.11')
        hsv654 = convertToHsv(image, "654")
        hsv654expr = hsv654.expression("((b('h')>(-60.557047339197744*b('v'))+122.47821613782476)&&(b('h')<(-111.53021054455162*b('v'))+189.34453256158332)&&(b('h')<(1010.7289326933218*b('v'))-135.00694405113367))||((b('h')>(25944.551568789888*b('v'))-33990.88089314458)&&(b('h')<(32.31251221202874*b('v'))+147.77160369999916)&&(b('h')>(-111.53021054455162*b('v'))+189.34453256158332))||((b('h')<(7.476554845098572*b('v'))+180.4922850785867)&&(b('h')<(104.37499774130613*b('v'))+126.94435205260542)&&(b('h')>(32.31251221202874*b('v'))+147.77160369999916))||((b('h')<(71.5303106986243*b('v'))+145.09495436831793)&&(b('h')<(145.14771269084218*b('v'))+115.16036225036032)&&(b('h')>(104.37499774130613*b('v'))+126.94435205260542))||((b('h')>(71.5303106986243*b('v'))+145.09495436831793)&&(b('h')<(63.98778874077445*b('v'))+149.26309627621794)&&(b('h')<(78.90706294311482*b('v'))+142.09539090073736))||((b('h')<(54.022891996163814*b('v'))+154.76988882666987)&&(b('h')>(7.476554845098572*b('v'))+180.4922850785867)&&(b('h')<(1.329979711104365*b('v'))+188.59022644471142))||((b('h')<(-0.9063208002806431*b('v'))+191.53649001807514)&&(b('h')<(12.120520640164884*b('v'))+181.66444228368684)&&(b('h')>(1.329979711104365*b('v'))+188.59022644471142))||((b('h')>(-554.544380704817*b('v'))+241.20879791870624)&&(b('h')>(-14.34796731410254*b('v'))+61.86139794741938)&&(b('h')<(-60.557047339197744*b('v'))+122.47821613782476))||((b('h')<(-14.34796731410254*b('v'))+61.86139794741938)&&(b('h')>(-114.63190817087207*b('v'))+95.15607300578044)&&(b('h')>(1.1835799314009672*b('v'))+41.48719930323337))")
        hsv432 = convertToHsv(image, "432")
        hsv432expr = hsv432.expression("((b('h')<(-290.3647541295557*b('v'))+365.9204839911988)&&(b('h')<(335.1949426777476*b('v'))+136.9220846732972)&&(b('h')>(-23.505492887658985*b('v'))+223.42719816416374))||((b('h')<(131.3034109469229*b('v'))+211.56057983072515)&&(b('h')>(-290.3647541295557*b('v'))+365.9204839911988)&&(b('h')>(412.868927627023*b('v'))-9.581110187711033))||((b('h')<(-110.96188694961242*b('v'))+401.8358594223264)&&(b('h')<(31201.82786617771*b('v'))-11162.414442104384)&&(b('h')>(131.3034109469229*b('v'))+211.56057983072515))||((b('h')<(4.324914848340889*b('v'))+359.25883441225426)&&(b('h')>(-110.96188694961242*b('v'))+401.8358594223264)&&(b('h')>(423.77264053876735*b('v'))-18.144891467499406))||((b('h')<(-23.505492887658985*b('v'))+223.42719816416374)&&(b('h')>(-716.983867682122*b('v'))+390.66821480942525)&&(b('h')>(272.52480149100506*b('v'))+65.35762563348138))||((b('h')<(-3550.663071023035*b('v'))+2106.8029918288794)&&(b('h')<(272.52480149100506*b('v'))+65.35762563348138)&&(b('h')>(-326.4412985361954*b('v'))+262.2735506441135))||((b('h')>(-61.03523580992668*b('v'))+110.43867974751751)&&(b('h')<(-326.4412985361954*b('v'))+262.2735506441135)&&(b('h')>(-1622.2473694938608*b('v'))+688.2823866791312))||((b('h')<(-61.03523580992668*b('v'))+110.43867974751751)&&(b('h')<(1636.2739567673634*b('v'))-517.7779568562837)&&(b('h')>(188.91098090522192*b('v'))-32.551842609834154))||((b('h')<(-77.56198786778931*b('v'))+119.89338940738565)&&(b('h')<(188.91098090522192*b('v'))-32.551842609834154)&&(b('h')>(43.44906482539776*b('v'))+16.214031249978476))||((b('h')<(-33.16714717184527*b('v'))+81.85695813588943)&&(b('h')<(43.44906482539776*b('v'))+16.214031249978476)&&(b('h')>(8.724200034130297*b('v'))+27.855486428395956))||((b('h')>(29699.19026356131*b('v'))-38245.65372368247)&&(b('h')<(8.724200034130297*b('v'))+27.855486428395956)&&(b('h')>(-16.544281722059484*b('v'))+36.32670437437103))||((b('h')>(15.820483019684168*b('v'))-5.367950304752587)&&(b('h')<(-16.544281722059484*b('v'))+36.32670437437103)&&(b('h')>(-7589.899231290106*b('v'))+2575.281793922023))||((b('h')>(46.74233619452139*b('v'))-45.203740876729434)&&(b('h')<(15.820483019684168*b('v'))-5.367950304752586)&&(b('h')>(0*b('v'))+0))")
        img1 = ee.call('Image.and', ndviMask, hsv654expr)
        img2 = ee.call('Image.and', img1, hsv432expr)
        maskImage = ee.call('Image.or', img2, tempMask)
        cloud_masked_filtered = maskImage.convolve(ee.Kernel.fixed(5, 5, [[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]]))
        img3 = ee.call('Image.not', cloud_masked_filtered)
        images.append(image.mask(img3))
    dest_collection = ee.ImageCollection(images)
    return dest_collection.median()

def getNoDataAreas():
  thermalNoData = landsat_collection.mean().expression('b("B10")>0')  # some B10 is missing from the scene
  img = thermalNoData.mask(1)
  returnImage = ee.call('Image.not', img)
  return returnImage

# SLOPE MASK ALGORITHM
def slopeMask(image):
  if not applySlopeMask:
      return image.mask().select(["B1"], ["mask"])
  terrain = ee.call('Terrain', ee.Image('srtm90_v4'))
  slope_radians = terrain.select(['slope']).expression("(b('slope')*" + str(math.pi) + ")/180")
  returnImage = slope_radians.expression("(b('slope')<" + str(slopeMaskThreshold) + ")").select(["slope"], ["mask"])
  return returnImage

# NDVI MASK ALGORITHM
def ndviMask(image):
  if not applyNDVIMask:
      return image.mask().select(["B1"], ["mask"])
  ndvi_areas = ndvi.expression("(b('nd')<" + str(ndviMaskThreshold) + ")")
  img = ee.call('Image.and', image.select(["B1"]), ndvi_areas)
  returnImage = img.select(["B1"], ["mask"])
  return returnImage

# BARE ROCK MASK ALGORITHM
def bareRockMask(image):
  # not implemented in Python yet
  return image.mask().select(["B1"], ["mask"])

# TEMPERATURE THRESHOLD MASK
def temperatureMask(image):
  if not applyTemperatureMask:
      return image.mask().select(["B1"], ["mask"])
  returnImage = image.expression('b("B10")<' + str(upperSceneTempThreshold) + '&&b("B10")>' + str(lowerSceneTempThreshold)).select(["B10"], ["mask"])  # max water B10 is 309.886027827
  return returnImage
  
# APPLICATION OF MASKS
def getMasks(image):
  slopeMaskBool = slopeMask(image)
  ndviMaskBool = ndviMask(image)
  bareRockMaskBool = bareRockMask(image)
  temperatureMaskBool = temperatureMask(image)
  masksCollection = ee.ImageCollection([slopeMaskBool, ndviMaskBool, bareRockMaskBool, temperatureMaskBool])
  returnImage = ee.call('reduce.and', masksCollection)
  returnImage = returnImage.mask(returnImage)
  return returnImage

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

# DETECT WATER BODIES ALGORITHM
def detectWaterBodies():
    detections = []
    for detectionExpression in detectionExpressions:
        hsv = convertToHsv(landsat, detectionExpression['bands'])
        detection = hsv.expression(detectionExpression['expression'])
        detections.append(detection.select([detection.getInfo()['bands'][0]['id']], ['h']))
    overallDetection = ee.call('reduce.and', detections)
    overallDetection = overallDetection.mask(overallDetection)
    waterBool = overallDetection.mask(1)
    overallDetection = ee.call('Image.and', landsat_mask, overallDetection)
    return overallDetection

def getScenesForPoint(collection, x, y, crs):  
    lng, lat = getPointLL(x, y, crs)
    small_query_polygon = [[[lng - 0.0001, lat + 0.0001], [lng - 0.0001, lat - 0.0001], [lng + 0.0001, lat - 0.0001], [lng + 0.0001, lat + 0.0001], [lng - 0.0001, lat + 0.0001]]]
    scenes = ee.ImageCollection(collection).filterBounds(ee.Feature.Polygon(small_query_polygon)).getInfo()  # LANDSAT/LC8_L1T is USGS Landsat 8 Raw Scenes (Orthorectified)
    return scenes
  
# iterate through the validation sites
conn = dbconnect("species_especies_schema")
# conn.cur.execute("DELETE FROM gee_validated_sites;")
sql = "SELECT DISTINCT  landsat_wrs2.path,  landsat_wrs2.row,  st_x(st_centroid(landsat_wrs2.geom)),  st_y(st_centroid(landsat_wrs2.geom)), l8_toa_scene_count, l8_toa_cloud_stats FROM  especies.gee_random_validation_sites_subset,  especies.landsat_wrs2 WHERE  gee_random_validation_sites_subset.path = landsat_wrs2.path AND gee_random_validation_sites_subset.row = landsat_wrs2.row and l8_toa_scene_count>0 AND gee_random_validation_sites_subset.path >176 ORDER BY 1,2;"
conn.cur.execute(sql)
pathRows = conn.cur.fetchall()
for pathRow in pathRows:
    path = pathRow[0]
    row = pathRow[1]
    lng = pathRow[2]
    lat = pathRow[3]
    sceneCount = pathRow[4]
    cloudStats = pathRow[5]
    scenes = getScenesForPoint(collectionid, lng, lat, 'EPSG:4326')
    mincloud = 100
    mincloudid = ''
    for scene in scenes['features']:
        sceneid = scene['properties']["system:index"]
        cloud = scene['properties']['CLOUD_COVER']
        if cloud < mincloud:
            mincloud = cloud
            mincloudid = sceneid
            sceneSunElevation = scene['properties']['SUN_ELEVATION']
    sceneid = mincloudid
    fullsceneid = collectionid + "/" + sceneid 
    print "path: " + str(path) + " row: " + str(row) + " long: " + str(lng) + " lat: " + str(lat) + " sceneCount: " + str(sceneCount) + " cloudStats: " + str(cloudStats) + " mincloud: " + str(mincloud) + " sceneid: " + fullsceneid + " elevation: " + str(sceneSunElevation)
    scene = ee.Image(fullsceneid)
#     coords = scene.getInfo()['properties']['system:footprint']['coordinates']
#     minx = coords[1][0]
#     maxx = coords[3][0]
#     miny = coords[2][1] 
#     maxy = coords[0][1]
#     bbox = [[minx, miny], [maxx, miny], [maxx, maxy], [minx, maxy]]
    landsat_collection = ee.ImageCollection([scene])
    landsat = getCompositeData()
    ndvi = landsat.normalizedDifference(["B5", "B4"])
    # 2. GET NO-DATA AREAS - i.e. WHERE SCENES ARE MISSING
    noDataAreas = getNoDataAreas()
    # 3. GET THE OPTIONAL MASKS IF REQUIRED
    landsat_mask = getMasks(landsat)
    # 4. DETECT WATER BODIES
    water_landsat = detectWaterBodies()
    # 5. GET THE FINAL OUTPUT IMAGE
    nda = noDataAreas.expression("b('B10')==1")
    cloud = ee.call('Image.not', landsat.mask())
    cloud = cloud.multiply(ee.call('Image.not', noDataAreas))
    cloud = cloud.expression("b('B1')=1")
    waterNonWater = water_landsat.mask(1)
    final = nda.add(cloud.multiply(2)).add(waterNonWater.multiply(3))  # 0-not water (grey), 1=no data (black), 2=cloud(white), 3=water(blue)
    sql2 = "SELECT objectid, glc2000, lng, lat FROM gee_random_validation_sites_subset where path=" + str(path) + " and row=" + str(row)
    conn.cur.execute(sql2)
    coords = conn.cur.fetchall()
    pointsArray = []
    for coord in coords:
        objectid = coord[0]
        glc2000 = coord[1]
        lng = coord[2]
        lat = coord[3]
        point = ee.Geometry.Point([lng, lat])
        collection = ee.ImageCollection(final)
        data = collection.getRegion(point, 30).getInfo()
        sql3 = "INSERT INTO gee_validated_sites(objectid, original_lat, original_lng, gee_lat, gee_lng, gee_predicted_land_cover, sceneid, cloud_cover, sun_elevation,path,row) VALUES (" + str(objectid) + "," + str(lat) + "," + str(lng) + "," + str(data[1][2]) + "," + str(data[1][1]) + "," + str(data[1][4]) + ",'" + fullsceneid + "'," + str(mincloud) + "," + str(sceneSunElevation) + "," + str(path) + "," + str(row) + ");"
        conn.cur.execute(sql3)
        print "objectid: " + str(objectid) + " Longitude: " + str(lng) + " Latitude: " + str(lat) + " GLC2000: " + str(glc2000) + " values: " + str(data[1][1]), str(data[1][2])