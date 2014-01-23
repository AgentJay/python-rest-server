import sys, ee, cPickle, utilities, math, datetime
from dbconnect import google_earth_engine
from orderedDict import OrderedDict
from ee import EEException

# Internal Google Earth Engine Class that returns all results as dictionaries either for internal Python use or for returning in other formats to the web

class GoogleEarthEngineError(Exception):
    """Exception Class that allows the DOPA Services REST Server to raise custom exceptions"""
    pass  

def getSceneImage(sceneid, ll_x, ll_y, ur_x, ur_y, crs, width, height, layerParameters):
    try:
        authenticate()
        region = getBoundingBoxLL(ll_x, ll_y, ur_x, ur_y, crs)  # get the bounding box as lat/long suitable for sending to GEE API
        # PROCESS THE INPUT SCENE
        scene = ee.Image(sceneid)
        sensor = scene.getInfo()['properties']['SENSOR_ID']
        # SET THE BANDS 
        if sensor == "OLI_TIRS":  # landsat 8
            layerParameters.setdefault("redBand", "B4")
            layerParameters.setdefault("greenBand", "B3")
            layerParameters.setdefault("blueBand", "B2")
        elif (sensor == "ETM+") | (sensor == "ETM"):  # landsat 7
            layerParameters.setdefault("redBand", "30")
            layerParameters.setdefault("greenBand", "20")
            layerParameters.setdefault("blueBand", "10")
        elif sensor == "TM":  # landsat 5
            layerParameters.setdefault("redBand", "30")
            layerParameters.setdefault("greenBand", "20")
            layerParameters.setdefault("blueBand", "10")
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
        if layerParameters['hsv']:
            scene = convertToHsv(scene, sensor)  # will only return bands 7,5,4 in Landsat 8
            output_thumbnail = scene.getThumbUrl({'bands': 'h,s,v', 'size': width + 'x' + height , 'region': region, 'gain':'0.8,300,0.01', })
            return output_thumbnail
        # FINAL STEP IS THE DETECTION PROCESS
        if 'detectWater' in layerParameters.keys():
            if layerParameters['detectWater']:
                hsv_output = convertToHsv(scene, sensor)  # convert to hsv
                layerParameters.setdefault("classMembershipExpression", "((b('h')>(0.12*b('v'))-600)&&(b('h')<=120)&&(b('h')>=0))||((b('h')>(0.02*b('v'))+0)&&(b('h')<=180)&&(b('h')>=120))||((b('h')>(0.00625*b('v'))+123.75)&&(b('h')<=230)&&(b('h')>=180))||((b('h')>(0.13*b('v'))-1980)&&(b('h')<=360)&&(b('h')>=230))")
                water = detectWaterBodies(hsv_output, layerParameters['classMembershipExpression'])  # detect the water
                water_mask = scene.mask(water.select('area_ac'))  # create the mask
                output_thumbnail = water_mask.getThumbUrl({'bands': bands, 'size': width + 'x' + height , 'min': layerParameters['min'], 'max': layerParameters['max'], 'region': region})
                return output_thumbnail
        else:
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

def convertToHsv(image, sensor):
    try:
        if sensor == "OLI_TIRS":  # landsat 8
            hsvIn1 = 'B7'  
            hsvIn2 = 'B5'  
            hsvIn3 = 'B4'  
            hsvIn1Correction = 1  
            hsvIn2Correction = 1
            hsvIn3Correction = 1  
        elif (sensor == "ETM+") | (sensor == "ETM"):  # landsat 7
            hsvIn1 = '70' 
            hsvIn2 = '40' 
            hsvIn3 = '30' 
            hsvIn1Correction = 10000  
            hsvIn2Correction = 10000  
            hsvIn3Correction = 10000
        elif sensor == "TM":  # landsat 5
            hsvIn1 = '70'  
            hsvIn2 = '40'  
            hsvIn3 = '30'  
            hsvIn1Correction = 0.02
            hsvIn2Correction = 0.02
            hsvIn3Correction = 0.02
        image = ee.Image.cat(image.select([hsvIn1, hsvIn2, hsvIn3], ['r', 'g', 'b']))  # get the red, green, blue bands as input to the hsv
        image = image.expression("band/coeff", {'band': image.select('r', 'g', 'b'), 'coeff': [hsvIn1Correction, hsvIn2Correction, hsvIn3Correction]});  # radiometric correction for landsat
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

    except (EEException):
        return "Google Earth Engine Error: " + str(sys.exc_info())        

def detectWaterBodies(hsv_output, classMembershipExpression):
    region_ac = hsv_output.expression(classMembershipExpression)
    region_c = hsv_output.expression("(b('h')>(-0.3593*b('v')+360))&&(b('h')<(0.0338*b('v')+195))&&(b('h')<(-0.0445*b('v')+270))&&(b('h')>(0.0366*b('v')+75.853))")
    region_a = region_ac.subtract(region_c)
#         region_b = region_ac.not()
    return ee.Image([region_a.select(['h'], ['area_a']), region_ac.select(['h'], ['area_ac']), region_c.select(['h'], ['area_c'])])

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
        return OrderedDict([(data[0][i], data[1][i]) for i in range (len(data[0]))])
    
    except ():
        return "DOPA Services Error: " + str(sys.exc_info())        

def getValuesForPoints(sceneid, pointsArray):  # points are as a [[117.49949,5.50077],[117.50005,5.50074]]
    try:
        authenticate()
        multipoint = ee.Geometry.MultiPoint(pointsArray)
        scene = ee.Image(sceneid)
        collection = ee.ImageCollection(scene)
        data = collection.getRegion(multipoint, 30).getInfo()
        return data
    
    except (EEException):
        return "Google Earth Engine Error: " + str(sys.exc_info())        

def getBoundingBoxLL(ll_x, ll_y, ur_x, ur_y, crs):  # gets a lat/long bounding box suitable for sending to the Google Earth Engine API
        ll_long, ll_lat = utilities.getPointLL(ll_x, ll_y, crs)  # transform the data to lat/long so that we can use it in Google Earth Engine
        ur_long, ur_lat = utilities.getPointLL(ur_x, ur_y, crs)
        return [[ll_long, ur_lat], [ll_long, ll_lat], [ur_long, ll_lat], [ur_long, ur_lat]]  # get the area of interest

def dateToDateTime(_date):  # converts a Google date into a Python datetime, e.g. 2013-06-14 to datetime.datetime(2013, 5, 2, 0, 0))
    d = _date.split("-")
    return datetime.datetime(int(d[0]), int(d[1]), int(d[2]))

def authenticate():
    # initialisation
    f_credentials = open(r'google earth engine/_credentials.pickle', 'rb')
    ee.data.initialize(cPickle.load(f_credentials))
    f_credentials.close()
    
    # initialise the API
    f_api = open(r'google earth engine/_api.pickle', 'rb')  # pickle of the gee api functions in json format
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
