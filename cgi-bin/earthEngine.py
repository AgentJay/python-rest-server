# Python module that wraps all of the Google Earth Engine functionality. This class returns all results as dictionaries either for internal Python use or for returning in other formats to the web
import sys, ee, cPickle, utilities, math, datetime, time
from dbconnect import google_earth_engine
from orderedDict import OrderedDict
from ee import EEException
# Constants
applyCloudMask = True  # Set to 1 to apply a cloud mask
applySlopeMask = True  # Set to 1 to apply a slope mask
applyNDVIMask = True  # Set to 1 to apply an ndvi mask
applyTemperatureMask = True  # Set to 1 to apply a temperature mask
applyBareRockMask = False  # Set to 1 to apply a barerock mask
cloudNDVIThreshold = 0.11  # Pixels with an NDVI lower than this threshold may be clouds
slopeMaskThreshold = 0.17  # Pixels with a slope greater than this threshold in radians will be excluded
ndviMaskThreshold = 0.1  # Pixels with an NDVI greater than this threshold will be excluded
annualMaxTempThreshold = 310  # Threshold for the max annual temperature above which bare rock could be present
annualMaxNDVIThreshold = 0.14  # Threshold for the max annual NDVI below which bare rock will be present
lowerSceneTempThreshold = 272.15  # lower temperature threshold for the scene
upperSceneTempThreshold = 308  # upper temperature threshold for the scene
temperatureDifferenceThreshold = 9  # Pixels with a day/night temperature difference greater than this threshold will be excluded
sunElevationThreshold = 42  # Landsat scenes with a solar elevation angle greater than this angle will be included
waterDetectExpressions = [
  {"bands":"SWIR2,NIR,Red", "expression":"((b('h')<(3.038667895460303*b('v'))+236.62216730574633)&&(b('h')<(10796.714793390856*b('v'))+204.85937891753062)&&(b('h')>(52.75476688685699*b('v'))+209.3760200216838))||((b('h')>(3.038667895460303*b('v'))+236.62216730574633)&&(b('h')<(2.0464628168010686*b('v'))+237.16593011613543)&&(b('h')<(9.076683306759795*b('v'))+236.60439910485127))||((b('h')<(-0.24666028009321075*b('v'))+238.42264113944557)&&(b('h')<(9.88710145914933*b('v'))+236.539667859889)&&(b('h')>(2.0464628168010686*b('v'))+237.1659301161354))||((b('h')>(-43.65372607478519*b('v'))+209.41654907810485)&&(b('h')<(-11433.100423818365*b('v'))+6504.023197860868)&&(b('h')<(52.75476688685699*b('v'))+209.3760200216838))||((b('h')>(26.243531044391943*b('v'))+170.78642497548128)&&(b('h')<(-43.65372607478519*b('v'))+209.41654907810485)&&(b('h')>(-1107.3553634247025*b('v'))+209.86371739648635))||((b('h')>(295.7226981444027*b('v'))+21.853346666047287)&&(b('h')<(26.243531044391943*b('v'))+170.78642497548128)&&(b('h')>(8.433335884642577*b('v'))+171.4003760014821))||((b('h')<(8.433335884642577*b('v'))+171.4003760014821)&&(b('h')>(-31.37019423910757*b('v'))+172.77247877400865)&&(b('h')>(82.71930111287884*b('v'))+132.73119126796098))||((b('h')<(-31.37019423910757*b('v'))+172.77247877400865)&&(b('h')>(-115.8110462176276*b('v'))+175.68331423895395)&&(b('h')>(4.932732579069547*b('v'))+160.0314641384984))||((b('h')<(-115.8110462176276*b('v'))+175.68331423895395)&&(b('h')>(-212.72738738403356*b('v'))+179.02420335115374)&&(b('h')>(7.045573926497733*b('v'))+159.75757941842787))"},
  {"bands":"SWIR2,Green,Blue", "expression":"((b('s')>(0.3402310087582287*b('v'))+0.6878785247108777)&&(b('s')<(-0.22139589479141922*b('v'))+1.0009733932691036)&&(b('s')<(114.04465599671092*b('v'))+0.38090113543454673))||((b('s')>(11.178032732580114*b('v'))-5.353961858528813)&&(b('s')<(0*b('v'))+0.9997719738616231)&&(b('s')>(-0.22139589479141922*b('v'))+1.0009733932691036))||((b('s')>(-6.555760168973008*b('v'))+0.706496211475811)&&(b('s')>(0.9781716036464391*b('v'))+0.33224042147527677)&&(b('s')<(0.3402310087582287*b('v'))+0.6878785247108777))||((b('s')>(0.19217317709040418*b('v'))+0.37128569968432384)&&(b('s')>(1.539711633483847*b('v'))+0.019193983135302795)&&(b('s')<(0.9781716036464391*b('v'))+0.33224042147527677))||((b('s')<(0.19217317709040418*b('v'))+0.37128569968432384)&&(b('s')>(-0.21980966748266745*b('v'))+0.3917513701490769)&&(b('s')>(0.4354503844174411*b('v'))+0.307720990923226))"},
]
sensors = [
  {"name":"Landsat 5", "collectionid":"LANDSAT/L5_L1T_TOA", "startDate":"8/13/1983", "endDate":"10/15/1984", "Blue":"10", "Green":"20", "Red":"30", "NIR":"40", "SWIR1":"50", "SWIR2":"70", "TIR":"60"},
  {"name":"Landsat 7", "collectionid":"LANDSAT/LE7_L1T_TOA", "startDate":"8/13/2013", "endDate":"10/15/2013", "Blue":"B1", "Green":"B2", "Red":"B3", "NIR":"B4", "SWIR1":"B5", "SWIR2":"B7", "TIR":"B6_VCID_2"},
  {"name":"Landsat 8", "collectionid":"LANDSAT/LC8_L1T_TOA", "startDate":'8/13/2013', "endDate":'10/15/2013', "Blue":"B2", "Green":"B3", "Red":"B4", "NIR":"B5", "SWIR1":"B6", "SWIR2":"B7", "TIR":"B10"}
]
class GoogleEarthEngineError(Exception):
    """Exception Class that allows the DOPA Services REST Server to raise custom exceptions"""
    pass  
 
def getSensorInformation(scene):  # returns the sensor information based on the passed scene
#     logging.info(scene.getInfo().keys())
    if "SENSOR_ID" not in scene.getInfo()['properties'].keys():
        return None
    else:
        sensorname = scene.getInfo()['properties']['SENSOR_ID']
        if sensorname == "OLI_TIRS":  # landsat 8
            return sensors[2]
        elif (sensorname == "ETM+") | (sensorname == "ETM"):  # landsat 7
            return sensors[1]
        elif sensorname == "TM":  # landsat 5
            return sensors[0]
    
def getRadiometricCorrection(scene):
    sceneid = landsat_scene.getInfo()['id']
    if "L5_L1T/" in sceneid:
        return 0.02
    if "L7_L1T/" in sceneid:
        return 10000
    if "LC8_L1T/" in sceneid:
        return 1

def getGEEBandNames(bands, sensor):  # gets the corresponding gee band names from their descriptions, e.g. SWIR2,NIR,Red -> B7,B5,B4 for Landsat 8 object
    geebandnames = []
    bandnames = bands.split(",")
    for band in bandnames:
        geebandnames.append(sensor[band])
    return ",".join([b for b in geebandnames])
        
def getImage(ll_x, ll_y, ur_x, ur_y, crs, width, height, layerParameters):  # main method to retrieve a url for an image generated from google earth engine 
#     logging.basicConfig(filename='../../htdocs/mstmp/earthEngine.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',)
    authenticate()
    region = getBoundingBoxLL(ll_x, ll_y, ur_x, ur_y, crs)
    if layerParameters['sceneid'] == 'collection':
        # GET A COLLECTION TO CREATE AN IMAGE FOR
        layerParameters.setdefault("collectionid", "LANDSAT/LC8_L1T_TOA")
        layerParameters.setdefault("startDate", "2013-09-13")
        layerParameters.setdefault("endDate", "2013-10-15")
        sd = datetime.datetime(int(layerParameters['startDate'][:4]), int(layerParameters['startDate'][5:7]), int(layerParameters['startDate'][8:10]))
        ed = datetime.datetime(int(layerParameters['endDate'][:4]), int(layerParameters['endDate'][5:7]), int(layerParameters['endDate'][8:10]))
        try:
            landsat_collection = ee.ImageCollection(layerParameters['collectionid']).filterBounds(ee.Feature.Polygon(region)).filterDate(sd, ed)
            if len(landsat_collection.getInfo()['features']) != 0:
                scene = landsat_collection.median()
                sensorinfo = getSensorInformation(ee.Image(landsat_collection.getInfo()['features'][0]['id']))  # get the scene metadata from the first scene in the collection
            else:
#                 logging.error("getImage: No matching scenes")
                raise GoogleEarthEngineError("getImage: No matching scenes")
        except (GoogleEarthEngineError):
#             logging.error("Google Earth Engine Services Error: " + str(sys.exc_info()))
            return "Google Earth Engine Services Error: " + str(sys.exc_info())
    else:
        try:
            # GET THE SINGLE SCENE TO CREATE AN IMAGE FOR
            scene = ee.Image(layerParameters['sceneid'])
            sensorinfo = getSensorInformation(scene)
        except (EEException):
#             logging.error("Google Earth Engine Services Error: " + str(sys.exc_info()))
            return "Google Earth Engine Services Error: " + str(sys.exc_info())
    return getSceneImage(scene, sensorinfo, region, width, height, layerParameters)

def getSceneImage(scene, sensorinfo, region, width, height, layerParameters):
    try:
        # SET THE DEFAULT PARAMETER VALUES
        layerParameters.setdefault("min", 0)
        layerParameters.setdefault("max", 0.7)
        layerParameters.setdefault("redBand", sensorinfo['Red'])
        layerParameters.setdefault("greenBand", sensorinfo['Green'])
        layerParameters.setdefault("blueBand", sensorinfo['Blue'])
        # SET THE BANDS FOR IMAGE RENDERING
        bands = layerParameters['redBand'] + "," + layerParameters['greenBand'] + "," + layerParameters['blueBand'] 
        # APPLY CORRECTIONS IF SPECIFIED
        # 1. ILLUMINATION CORRECTION
        layerParameters.setdefault("illuminationCorrection", False)
        if layerParameters['illuminationCorrection']:
            scene = illuminationCorrection(scene)  # will only return bands 4,3,2
        # 2. CLOUD REMOVAL 
        layerParameters.setdefault("cloudCorrection", False)
        # APPLY HSV IF SPECIFIED
        layerParameters.setdefault("hsv", False)
        defaulthsvbands = getGEEBandNames("SWIR2,NIR,Red", sensorinfo)
        layerParameters.setdefault("hsvbands", defaulthsvbands)
        if layerParameters['hsv']:
            scene = convertToHsv(scene, layerParameters["hsvbands"])  # will only return bands 7,5,4 in Landsat 8
            output_thumbnail = scene.getThumbUrl({'bands': 'h,s,v', 'size': width + 'x' + height , 'region': region, 'gain':'0.8,300,0.01', })
            return output_thumbnail
        # FINAL STEP IS THE DETECTION PROCESS IF ANY
        if 'detectExpression' in layerParameters.keys():
            if "b('h')" in layerParameters['detectExpression']:
                detectionInput = convertToHsv(scene, layerParameters["hsvbands"])  # convert to hsv
            else:
                detectionInput = scene
            booleanClass = detectionInput.expression(layerParameters['detectExpression'])  # detect the class
            mask = scene.mask(booleanClass)  # create the mask
            output_thumbnail = mask.getThumbUrl({'bands': bands, 'size': width + 'x' + height , 'min': layerParameters['min'], 'max': layerParameters['max'], 'region': region})
            return output_thumbnail
        if 'detectWater' in layerParameters.keys():
            if layerParameters['detectWater']:
                detection = detectWater(scene, sensorinfo)
                output_thumbnail = detection.getThumbUrl({'palette': '444444,000000,ffffff,0000ff', 'size': width + 'x' + height , 'min': 0, 'max': 3, 'region': region})
                return output_thumbnail
        output_thumbnail = scene.getThumbUrl({'bands': bands, 'size': width + 'x' + height , 'min': layerParameters['min'], 'max': layerParameters['max'], 'region': region})
        return output_thumbnail
    
    except (EEException):
        return "Google Earth Engine Error: " + str(sys.exc_info())        

def illuminationCorrection(image):
    # accepts either a single scene which will have the sun elevation and azimuth already populated, or a collection image which will need to have the sun elevation and azimuth manually populated and accessed via the properties
    try:
        terrain = ee.call('Terrain', ee.Image('srtm90_v4'))
        solar_zenith = (90 - image.getInfo()['properties']['SUN_ELEVATION'])
#             solar_zenith = 31.627850000000002
        solar_azimuth = image.getInfo()['properties']['SUN_AZIMUTH']
#             solar_azimuth = 50.377735
        solar_zenith_radians = (solar_zenith * math.pi) / 180
        slope_radians = terrain.select(['slope']).expression("(b('slope')*" + str(math.pi) + ")/180")
        aspect = terrain.select(['aspect'])
        cosZ = math.cos(solar_zenith_radians)
        cosS = slope_radians.cos()
        slope_illumination = cosS.expression("b('slope')*(" + str(cosZ) + ")").select(['slope'], ['b1'])
        sinZ = math.sin(solar_zenith_radians)
        sinS = slope_radians.sin()
        azimuth_diff_radians = aspect.expression("((b('aspect')-" + str(solar_azimuth) + ")*" + str(math.pi) + ")/180")
        cosPhi = azimuth_diff_radians.cos()
        aspect_illumination = cosPhi.multiply(sinS).expression("b('aspect')*" + str(sinZ)).select(['aspect'], ['b1'])
        ic = slope_illumination.add(aspect_illumination)
        return image.expression("((image * (cosZ + coeff)) / (ic + coeff)) + offsets", {'image': image.select('B4', 'B3', 'B2'), 'ic': ic, 'cosZ': cosZ, 'coeff': [12, 9, 25], 'offsets': [0, 0, 0]})

    except (EEException):
        return "Google Earth Engine Error: " + str(sys.exc_info())        

def rgbToHsv(image):
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
    return ee.Image([hue.select(['max'], ['h']), saturation.select(['max'], ['s']), value.select(['max'], ['v'])])

def convertToHsv(image, bands):
    try:
        bandsArray = bands.split(",")
        r = bandsArray[0]
        g = bandsArray[1]
        b = bandsArray[2]
        img = ee.Image.cat([image.select([r], ['r']), image.select([g], ['g']), image.select([b], ['b'])])
        return rgbToHsv(img)

    except (EEException):
        return "Google Earth Engine Error: " + str(sys.exc_info())        

def getDatesForBB(ll_x, ll_y, ur_x, ur_y, crs):
    try:
        authenticate()
        bbox_latlong = getBoundingBoxLL(ll_x, ll_y, ur_x, ur_y, crs)  # [[114, 6], [114, 5], [115, 5], [115, 6]]
        clip_polygon = ee.Feature.Polygon([bbox_latlong])
        return ee.ImageCollection("LANDSAT/LC8_L1T").filterBounds(clip_polygon).aggregate_array("DATE_ACQUIRED").getInfo()

    except (EEException):
        return "Google Earth Engine Error: " + str(sys.exc_info())        

def getDatesForPoint(x, y, crs):
    try:
        authenticate()
        lng, lat = utilities.getPointLL(x, y, crs)
        # points dont work with GEE, so we have to create a small polygon
        small_query_polygon = [[[lng - 0.00001, lat + 0.00001], [lng - 0.00001, lat - 0.00001], [lng + 0.00001, lat - 0.00001], [lng + 0.00001, lat + 0.00001], [lng - 0.00001, lat + 0.00001]]]
        stringDates = ee.ImageCollection("LANDSAT/LC8_L1T").filterBounds(ee.Feature.Polygon(small_query_polygon)).aggregate_array("DATE_ACQUIRED").getInfo()  # get the dates as strings
        dates = [dateToDateTime(s) for s in stringDates]
        return [s.isoformat() for s in sorted(set(dates))]  # convert them to properly formatted strings 

    except (EEException):
        return "Google Earth Engine Error: " + str(sys.exc_info())        
        
def getScenesForPoint(collection, x, y, crs):  
    try:
        authenticate()
        lng, lat = utilities.getPointLL(x, y, crs)
        # points dont work with GEE, so we have to create a small polygon
        small_query_polygon = [[[lng - 0.00001, lat + 0.00001], [lng - 0.00001, lat - 0.00001], [lng + 0.00001, lat - 0.00001], [lng + 0.00001, lat + 0.00001], [lng - 0.00001, lat + 0.00001]]]
        scenes = ee.ImageCollection(collection).filterBounds(ee.Feature.Polygon(small_query_polygon)).getInfo()  # LANDSAT/LC8_L1T is USGS Landsat 8 Raw Scenes (Orthorectified)
        # Landsat image ids are LANDSAT/LC8_L1T/LC81970502014029LGN00 whereas Landsat TOA are LC8_L1T_TOA/LC81970502014029LGN00 without the Landsat - so add this in
        if collection[-3:] == "TOA":
            for scene in scenes['features']:
                scene['id'] = "LANDSAT/" + scene['id']
        return scenes

    except (EEException):
        return "Google Earth Engine Error: " + str(sys.exc_info())        

def getValuesForPoint(sceneid, x, y, crs):
    try:
        authenticate()
        lng, lat = utilities.getPointLL(x, y, crs)
        scene = ee.Image(sceneid)
        collection = ee.ImageCollection(scene)
        data = collection.getRegion(ee.Geometry.Point(lng, lat), 30).getInfo()
        if len(data) == 1:
            raise GoogleEarthEngineError("No values for point x:" + str(x) + " y: " + str(y) + " for sceneid: " + sceneid)
        return OrderedDict([(data[0][i], data[1][i]) for i in range (len(data[0]))])
    
    except (EEException, GoogleEarthEngineError):
        return "Google Earth Engine Error: " + str(sys.exc_info())        

def getValuesForPoints(sceneid, pointsArray):  # points are as a [[117.49949,5.50077],[117.50005,5.50074]]
    try:
        authenticate()
        multipoint = ee.Geometry.MultiPoint(pointsArray)
        scene = ee.Image(sceneid)
        collection = ee.ImageCollection(scene)
        data = collection.getRegion(multipoint, 30).getInfo()
        return data
    
    except (EEException, GoogleEarthEngineError):
        return "Google Earth Engine Error: " + str(sys.exc_info())        

def getBoundingBoxLL(ll_x, ll_y, ur_x, ur_y, crs):  # gets a lat/long bounding box suitable for sending to the Google Earth Engine API
        ll_long, ll_lat = utilities.getPointLL(ll_x, ll_y, crs)  # transform the data to lat/long so that we can use it in Google Earth Engine
        ur_long, ur_lat = utilities.getPointLL(ur_x, ur_y, crs)
        return [[ll_long, ur_lat], [ll_long, ll_lat], [ur_long, ll_lat], [ur_long, ur_lat]]  # get the area of interest

def getDateTimeForScene(sceneid):
    try:
        authenticate()
        scene = ee.Image(sceneid)
        return scene.getInfo()['properties']['DATE_ACQUIRED'] + ' ' + scene.getInfo()['properties']['SCENE_CENTER_TIME'][:8]
    
    except (EEException, GoogleEarthEngineError):
        return "Google Earth Engine Error: " + str(sys.exc_info())        

def dateToDateTime(_date):  # converts a Google date into a Python datetime, e.g. 2013-06-14 to datetime.datetime(2013, 5, 2, 0, 0))
    d = _date.split("-")
    return datetime.datetime(int(d[0]), int(d[1]), int(d[2]))

def detectWater(image, sensor=None):
    # get the sensor information from the scene if it isnt already known
    if not sensor:
        sensor = getSensorInformation(image)
    # add a band for no data areas
    image = image.addBands(ee.call('Image.not', image.expression("b('" + sensor['TIR'] + "')>0").mask()).clip(image.geometry()).select([sensor['TIR']], ["isEmpty"]))
    # add a band for the ndvi
    image = image.addBands(image.normalizedDifference([sensor['NIR'], sensor['Red']]).select(["nd"], ["ndvi"]))
    # add a band for the cloud mask
    if applyCloudMask:
#         print "applyCloudMask=True"
        # add a band for areas where the temperature is low enough for cloud
        image = image.addBands(image.expression("b('" + sensor['TIR'] + "')<" + str(lowerSceneTempThreshold)).select([sensor['TIR']], ["cloud_temp_ok"]))
        # add a band for areas where the ndvi is low enough for cloud
        image = image.addBands(image.expression("b('ndvi')<" + str(cloudNDVIThreshold)).select(["ndvi"], ["cloud_ndvi_ok"]))
        # add a band for areas where the hsv 654 is ok for cloud
        image = image.addBands(convertToHsv(image, sensor['SWIR1'] + "," + sensor['NIR'] + "," + sensor['Red']))
        image = image.addBands(image.expression("((b('h')>(-60.557047339197744*b('v'))+122.47821613782476)&&(b('h')<(-111.53021054455162*b('v'))+189.34453256158332)&&(b('h')<(1010.7289326933218*b('v'))-135.00694405113367))||((b('h')>(25944.551568789888*b('v'))-33990.88089314458)&&(b('h')<(32.31251221202874*b('v'))+147.77160369999916)&&(b('h')>(-111.53021054455162*b('v'))+189.34453256158332))||((b('h')<(7.476554845098572*b('v'))+180.4922850785867)&&(b('h')<(104.37499774130613*b('v'))+126.94435205260542)&&(b('h')>(32.31251221202874*b('v'))+147.77160369999916))||((b('h')<(71.5303106986243*b('v'))+145.09495436831793)&&(b('h')<(145.14771269084218*b('v'))+115.16036225036032)&&(b('h')>(104.37499774130613*b('v'))+126.94435205260542))||((b('h')>(71.5303106986243*b('v'))+145.09495436831793)&&(b('h')<(63.98778874077445*b('v'))+149.26309627621794)&&(b('h')<(78.90706294311482*b('v'))+142.09539090073736))||((b('h')<(54.022891996163814*b('v'))+154.76988882666987)&&(b('h')>(7.476554845098572*b('v'))+180.4922850785867)&&(b('h')<(1.329979711104365*b('v'))+188.59022644471142))||((b('h')<(-0.9063208002806431*b('v'))+191.53649001807514)&&(b('h')<(12.120520640164884*b('v'))+181.66444228368684)&&(b('h')>(1.329979711104365*b('v'))+188.59022644471142))||((b('h')>(-554.544380704817*b('v'))+241.20879791870624)&&(b('h')>(-14.34796731410254*b('v'))+61.86139794741938)&&(b('h')<(-60.557047339197744*b('v'))+122.47821613782476))||((b('h')<(-14.34796731410254*b('v'))+61.86139794741938)&&(b('h')>(-114.63190817087207*b('v'))+95.15607300578044)&&(b('h')>(1.1835799314009672*b('v'))+41.48719930323337))").select(["h"], ["cloud_hsv_654_ok"]))
        # add a band for areas where the hsv 432 is ok for cloud
        image = image.addBands(convertToHsv(image, sensor['Red'] + "," + sensor['Green'] + "," + sensor['Blue']), None, True)
        image = image.addBands(image.expression("((b('h')<(-290.3647541295557*b('v'))+365.9204839911988)&&(b('h')<(335.1949426777476*b('v'))+136.9220846732972)&&(b('h')>(-23.505492887658985*b('v'))+223.42719816416374))||((b('h')<(131.3034109469229*b('v'))+211.56057983072515)&&(b('h')>(-290.3647541295557*b('v'))+365.9204839911988)&&(b('h')>(412.868927627023*b('v'))-9.581110187711033))||((b('h')<(-110.96188694961242*b('v'))+401.8358594223264)&&(b('h')<(31201.82786617771*b('v'))-11162.414442104384)&&(b('h')>(131.3034109469229*b('v'))+211.56057983072515))||((b('h')<(4.324914848340889*b('v'))+359.25883441225426)&&(b('h')>(-110.96188694961242*b('v'))+401.8358594223264)&&(b('h')>(423.77264053876735*b('v'))-18.144891467499406))||((b('h')<(-23.505492887658985*b('v'))+223.42719816416374)&&(b('h')>(-716.983867682122*b('v'))+390.66821480942525)&&(b('h')>(272.52480149100506*b('v'))+65.35762563348138))||((b('h')<(-3550.663071023035*b('v'))+2106.8029918288794)&&(b('h')<(272.52480149100506*b('v'))+65.35762563348138)&&(b('h')>(-326.4412985361954*b('v'))+262.2735506441135))||((b('h')>(-61.03523580992668*b('v'))+110.43867974751751)&&(b('h')<(-326.4412985361954*b('v'))+262.2735506441135)&&(b('h')>(-1622.2473694938608*b('v'))+688.2823866791312))||((b('h')<(-61.03523580992668*b('v'))+110.43867974751751)&&(b('h')<(1636.2739567673634*b('v'))-517.7779568562837)&&(b('h')>(188.91098090522192*b('v'))-32.551842609834154))||((b('h')<(-77.56198786778931*b('v'))+119.89338940738565)&&(b('h')<(188.91098090522192*b('v'))-32.551842609834154)&&(b('h')>(43.44906482539776*b('v'))+16.214031249978476))||((b('h')<(-33.16714717184527*b('v'))+81.85695813588943)&&(b('h')<(43.44906482539776*b('v'))+16.214031249978476)&&(b('h')>(8.724200034130297*b('v'))+27.855486428395956))||((b('h')>(29699.19026356131*b('v'))-38245.65372368247)&&(b('h')<(8.724200034130297*b('v'))+27.855486428395956)&&(b('h')>(-16.544281722059484*b('v'))+36.32670437437103))||((b('h')>(15.820483019684168*b('v'))-5.367950304752587)&&(b('h')<(-16.544281722059484*b('v'))+36.32670437437103)&&(b('h')>(-7589.899231290106*b('v'))+2575.281793922023))||((b('h')>(46.74233619452139*b('v'))-45.203740876729434)&&(b('h')<(15.820483019684168*b('v'))-5.367950304752586)&&(b('h')>(0*b('v'))+0))").select(["h"], ["cloud_hsv_432_ok"]))
        cloudMask = image.expression("(b('cloud_temp_ok'))||(1&&b('cloud_ndvi_ok')==1&&b('cloud_hsv_654_ok')==1&&b('cloud_hsv_432_ok')==1)").select(["cloud_temp_ok"], ["isCloud"])
        image = image.addBands(cloudMask.convolve(ee.Kernel.fixed(5, 5, [[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]])).expression("b('isCloud')>0"))
    # add a band for the slope mask
    if applySlopeMask:
#         print "applySlopeMask=True"
        terrain = ee.call('Terrain', ee.Image('srtm90_v4')).clip(image.geometry())
        slope_radians = terrain.select(['slope']).expression("(b('slope')*" + str(math.pi) + ")/180")
        slope_areas = slope_radians.expression("(b('slope')>" + str(slopeMaskThreshold) + ")")
        image = image.addBands(slope_areas.select(["slope"], ["isSteep"]))
    # add a band for the ndvi mask
    if applyNDVIMask:
#         print "applyNDVIMask=True"
        image = image.addBands(image.expression("b('ndvi')>" + str(ndviMaskThreshold)).select(["ndvi"], ["isGreen"]))
    # add a band for the temperature mask
    if applyTemperatureMask:
#         print "applyTemperatureMask=True"
        image = image.addBands(ee.call('Image.not', image.expression("b('" + sensor['TIR'] + "')<" + str(upperSceneTempThreshold) + "&&b('" + sensor['TIR'] + "')>" + str(lowerSceneTempThreshold))).select([sensor['TIR']], ["isTooHotOrCold"]))
    # add a band for the barerock mask
    if applyBareRockMask:
#         print "applyBareRockMask=True"
        landsat_collection = ee.ImageCollection("LANDSAT/LC8_L1T_TOA").filterDate(datetime.datetime(2013, 4, 1), datetime.datetime(2014, 4, 1)).filterBounds(image.geometry())
        image = image.addBands(landsat_collection.select([sensor['TIR']], ["rock_temp_ok"]).max().expression('b("rock_temp_ok")>' + str(annualMaxTempThreshold)))
        bandnames = getGEEBandNames("NIR,Red", sensor).split(",")
        ndvi_images = []
        for feature in landsat_collection.getInfo()['features']:
            ndvi_images.append(ee.Image(feature['id']).normalizedDifference([bandnames[0], bandnames[1]]))
        landsat_collection_ndvi = ee.ImageCollection(ndvi_images)
        isrock = landsat_collection_ndvi.max().clip(image.geometry())
        image = image.addBands(isrock.expression('b("nd")<' + str(annualMaxNDVIThreshold)).select(["nd"], ["rock_ndvi_ok"]))
        image = image.addBands(image.expression("b('rock_temp_ok')==1&&b('rock_ndvi_ok')==1").select(['rock_temp_ok'], ['isRock']))
    # add a band for the total mask - this adds all bands with the prefix 'is' 
    maskbands = [b for b in image.bandNames().getInfo() if b[:2] == "is"]
    image = image.addBands(ee.call('Image.not', image.select(maskbands).reduce(ee.Reducer.anyNonZero())).select(["any"], ["detectArea"]))
    # detect water
    for i in range(len(waterDetectExpressions)):
        waterDetectExpression = waterDetectExpressions[i]
        # convert the band descriptions to actual band names according to the sensor, e.g. "SWIR2,NIR,Red" -> "B7,B5,B4" for landsat
        bands = getGEEBandNames(waterDetectExpression['bands'], sensor)
        # convert to hsv
        hsv = convertToHsv(image, bands)
        detection = hsv.expression(waterDetectExpression['expression'])
        image = image.addBands(detection.select([detection.bandNames().getInfo()[0]], ["detectExpression" + str(i + 1)]))
    # add a band for the total detections - this combines all the bands with the prefix 'detect'
    detectbands = [b for b in image.bandNames().getInfo() if b[:6] == "detect"]
    image = image.addBands(image.select(detectbands).reduce(ee.Reducer.allNonZero()).select(["all"], ["water"]))
    # create a final water detection layer with 0-not water (grey), 1=no data (black), 2=cloud(white), 3=water(blue)
    detection = image.expression("b('isEmpty')+(b('isCloud')*2)+(b('water')*3)").select(["isEmpty"], ["class"])
    return detection  # 0-not water, 1=no data, 2=cloud, 3=water

def authenticate():
    # initialisation
    f_credentials = open('/srv/www/dopa-services/cgi-bin/google earth engine/_credentials.pickle', 'rb')
    ee.data.initialize(cPickle.load(f_credentials))
    f_credentials.close()
    
    # initialise the API
    f_api = open('/srv/www/dopa-services/cgi-bin/google earth engine/_api.pickle', 'rb')  # pickle of the gee api functions in json format
    ee.ApiFunction._api = cPickle.load(f_api)
    f_api.close()
    ee.Image.initialize()
    ee.Feature.initialize()
    ee.Collection.initialize()
    ee.ImageCollection.initialize()
    ee.FeatureCollection.initialize()
    ee.Filter.initialize()
    ee.Geometry.initialize()
    ee.String.initialize()
    ee._InitializeGeneratedClasses()
    ee._InitializeUnboundMethods()
    
def authenticate_live():
    # initialisation
    _google_earth_engine = google_earth_engine()
    ee.Initialize(ee.ServiceAccountCredentials(_google_earth_engine.MY_SERVICE_ACCOUNT, _google_earth_engine.MY_PRIVATE_KEY_FILE))
