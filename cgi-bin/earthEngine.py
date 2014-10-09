# Python module that wraps all of the Google Earth Engine functionality. This class returns all results as dictionaries either for internal Python use or for returning in other formats to the web
import sys, ee, cPickle, utilities, math, datetime, time
from dbconnect import google_earth_engine
from orderedDict import OrderedDict
from ee import EEException
# Constants
cloudNDVIThreshold = 0.1  # Pixels with an NDVI lower than this threshold may be clouds
snowNorthThreshold = 31  # Pixels with a latitude further north than this will be tested for snow
snowAltitudinalThreshold = 3000  # Pixels with a height greater than this will be tested for snow
snowValueThreshold = 0.18  # Pixels with a value greater than this will be tested for snow 
snowSatThreshold = 0.58 #Pixels with a Sat lower than this will be considered as snow && (default value:0.58) 
snowTemperatureThreshold = 281  # Pixels with a temperature less than this will be tested for snow 
slopeMaskThreshold = 0.17  # Pixels with a slope greater than this threshold in radians will be excluded
ndviMaskThreshold = 0.12  # Pixels with an NDVI greater than this threshold will be excluded
annualMaxTempThreshold = 310  # Threshold for the max annual temperature above which bare rock could be present
annualMaxNDVIThreshold = 0.14  # Threshold for the max annual NDVI below which bare rock will be present
lowerSceneTempThreshold = 264  # lower temperature threshold for the scene
upperSceneTempThreshold = 310  # upper temperature threshold for the scene
sunElevationThreshold = 23  # Landsat scenes with a solar elevation angle greater than this angle will be included
waterDetectExpressions = [
  {"bands":"SWIR2,NIR,Red", "expression":"((b('h')<(-16.481702483844295*b('v'))+237.39299348280895)&&(b('h')<(84688.07188433492*b('v'))-563.0010063926386)&&(b('h')>(1367.4216031588037*b('v'))+190.57398940093609))||((b('h')>(13.55095876285446*b('v'))+202.81876979706576)&&(b('h')<(-53.2340279866469*b('v'))+238.63636595740172)&&(b('h')<(1367.4216031588037*b('v'))+190.57398940093609))||((b('h')>(1599.6635800374377*b('v'))-647.8326130760333)&&(b('h')<(4.6138461972494085*b('v'))+236.679307363423)&&(b('h')>(-53.2340279866469*b('v'))+238.63636595740172))||((b('h')>(4.6138461972494085*b('v'))+236.679307363423)&&(b('h')<(4.062613097521557*b('v'))+236.9849857615982)&&(b('h')<(14.217951737090626*b('v'))+236.35438967976754))||((b('h')<(-13.951882699724406*b('v'))+246.9746656664425)&&(b('h')<(483.90327387870934*b('v'))+207.18926438479662)&&(b('h')>(4.062613097521557*b('v'))+236.9849857615982))||((b('h')<(-20.469908836263855*b('v'))+250.5891434430224)&&(b('h')<(4.658797190131653*b('v'))+245.48741910936977)&&(b('h')>(-13.951882699724406*b('v'))+246.9746656664425))||((b('h')>(210.80364213633263*b('v'))+97.02976992627356)&&(b('h')<(13.55095876285446*b('v'))+202.81876979706576)&&(b('h')>(1.1522186650929778*b('v'))+202.93090743023936))||((b('h')<(1.1522186650929778*b('v'))+202.93090743023936)&&(b('h')>(-71.79923381426251*b('v'))+203.59070053446678)&&(b('h')>(141.4836523127315*b('v'))+132.0453479392211))||((b('h')<(-71.79923381426251*b('v'))+203.5907005344668)&&(b('h')>(-79.04981968510809*b('v'))+203.65627683756435)&&(b('h')>(10.857445113377223*b('v'))+175.86366933371292))||((b('h')<(-79.04981968510809*b('v'))+203.65627683756435)&&(b('h')>(-91.44418331006706*b('v'))+203.768374888708)&&(b('h')>(16.605504291045854*b('v'))+174.08679898856425))||((b('h')>(-1020.1010656054937*b('v'))+212.16740446670389)&&(b('h')>(99.74988069193253*b('v'))+151.24678738275915)&&(b('h')<(-91.44418331006706*b('v'))+203.768374888708))||((b('h')>(2149.754329876662*b('v'))-411.89563352584287)&&(b('h')<(99.74988069193253*b('v'))+151.24678738275912)&&(b('h')>(41.62121011013503*b('v'))+154.4090247267743))||((b('h')>(177.29444892391095*b('v'))+117.96332477544951)&&(b('h')<(41.62121011013503*b('v'))+154.4090247267743)&&(b('h')>(22.61526070734314*b('v'))+155.44296068915622))||((b('h')<(22.61526070734314*b('v'))+155.44296068915622)&&(b('h')>(-3.5222556628157378*b('v'))+156.86485851544862)&&(b('h')>(183.05939965647218*b('v'))+116.56644483957649))||((b('h')<(-3.5222556628157378*b('v'))+156.86485851544862)&&(b('h')>(-45.58838956872646*b('v'))+159.15328345660438)&&(b('h')>(120.59366417838626*b('v'))+130.0579643812797))||((b('h')>(-79.27784668768453*b('v'))+160.98601175289758)&&(b('h')>(18.192621481728114*b('v'))+147.98644067414764)&&(b('h')<(-45.58838956872646*b('v'))+159.15328345660438))||((b('h')>(-249.8453350157328*b('v'))+170.26499363683433)&&(b('h')>(27.32683351734562*b('v'))+146.76821693073646)&&(b('h')<(-79.27784668768453*b('v'))+160.9860117528976))||((b('h')<(-1020.1010656054937*b('v'))+212.16740446670389)&&(b('h')>(-3999.1589500935984*b('v'))+239.1108275580515)&&(b('h')>(224.31551905409455*b('v'))+144.47033594378084))||((b('h')<(-3894.4662440381876*b('v'))+368.5347326130829)&&(b('h')<(224.31551905409455*b('v'))+144.47033594378084)&&(b('h')>(-66.42201716418424*b('v'))+150.98524293787293))||((b('h')<(141.4836523127315*b('v'))+132.0453479392211)&&(b('h')>(-37.942684535992605*b('v'))+192.23358323472317)&&(b('h')>(192.66969319288907*b('v'))+106.18976411449788))||((b('h')>(2692.244260520529*b('v'))-1156.41931133637)&&(b('h')<(192.66969319288907*b('v'))+106.18976411449788)&&(b('h')>(-33.044398171145254*b('v'))+190.40598286857332))||((b('h')>(-18.095741855627164*b('v'))+183.0184247191252)&&(b('h')<(-33.044398171145254*b('v'))+190.40598286857332)&&(b('h')>(-190.0052894840852*b('v'))+248.96968475693268))||((b('h')<(-18.095741855627164*b('v'))+183.0184247191252)&&(b('h')>(-20.357709587580604*b('v'))+183.88620445646478)&&(b('h')>(-10.857445113376142*b('v'))+179.44129129939233))||((b('h')<(-20.357709587580604*b('v'))+183.88620445646478)&&(b('h')>(-271.436127834409*b('v'))+280.2097553011579)&&(b('h')>(15.51063587625202*b('v'))+167.10438947568133))||((b('h')>(26.93640963242224*b('v'))+161.75858334192242)&&(b('h')<(15.51063587625202*b('v'))+167.10438947568133)&&(b('h')>(-13.837920242538257*b('v'))+178.67266483567965))"},
  {"bands":"SWIR2,NIR,Red", "expression":"((b('h')>(15.009416604134271*b('s'))+202.36255490978616)&&(b('h')<(-36.29216171095232*b('s'))+253.66413322487273)&&(b('h')<(1293.2135298349533*b('s'))-123.40004846221527))||((b('h')<(4.766693079016967*b('s'))+242.01933653025537)&&(b('h')>(-36.29216171095232*b('s'))+253.66413322487273)&&(b('h')>(10000000*b('s'))-9999782.628028486))||((b('h')>(1770.2933626478894*b('s'))-1552.9213911339689)&&(b('h')<(15.009416604134271*b('s'))+202.36255490978616)&&(b('h')>(4.4527608324114265*b('s'))+205.053020095668))||((b('h')<(4.4527608324114265*b('s'))+205.053020095668)&&(b('h')>(-11.642292182700958*b('s'))+209.1549990498435)&&(b('h')>(29426.209672458182*b('s'))-29085.64044956417))||((b('h')<(-11.642292182700958*b('s'))+209.1549990498435)&&(b('h')>(-42.610608506107866*b('s'))+217.04757210850875)&&(b('h')>(18827.416804554992*b('s'))-18538.35359451796))||((b('h')<(-42.610608506107866*b('s'))+217.04757210850875)&&(b('h')>(-2948.5423727959624*b('s'))+957.65221181953)&&(b('h')>(12.555041960589588*b('s'))+162.21702616003503))||((b('h')<(12.555041960589588*b('s'))+162.21702616003503)&&(b('h')>(-5.800507114530911*b('s'))+167.1478499531627)&&(b('h')>(340.2498970280048*b('s'))-163.48724190980542))||((b('h')<(-5.800507114530911*b('s'))+167.1478499531627)&&(b('h')>(-17.238360348487014*b('s'))+170.22038342178752)&&(b('h')>(114.72489873171403*b('s'))+51.991421419182984))||((b('h')<(-17.238360348487014*b('s'))+170.22038342178752)&&(b('h')>(-23.671165603568785*b('s'))+171.94841831077412)&&(b('h')>(7.274223651467424*b('s'))+148.2589876324115))||((b('h')<(-23.671165603568785*b('s'))+171.94841831077412)&&(b('h')>(-32.91623240087615*b('s'))+174.43190682678946)&&(b('h')>(13.384571518699898*b('s'))+143.58137116979333))||((b('h')<(-32.91623240087615*b('s'))+174.43190682678946)&&(b('h')>(-947.3302286013217*b('s'))+420.0695758925139)&&(b('h')>(10.999060906509083*b('s'))+145.17085286279737))||((b('h')<(10.999060906509083*b('s'))+145.17085286279737)&&(b('h')>(-8.45159799505535*b('s'))+150.75031427827042)&&(b('h')>(24.745610366995415*b('s'))+136.0114349177433))||((b('h')<(-8.45159799505535*b('s'))+150.75031427827042)&&(b('h')>(-221.45381967303496*b('s'))+211.8504386121941)&&(b('h')>(26.728949128935337*b('s'))+135.13087320229778))"},
  {"bands":"SWIR2,Green,Blue", "expression":"((b('h')<(12.26593689219973*b('s'))+213.56319793892735)&&(b('h')<(161.55657816363095*b('s'))+166.50682005437122)&&(b('h')>(62.88747617389189*b('s'))+192.89228050816078))||((b('h')>(-9715.48675311279*b('s'))+2807.7626028916543)&&(b('h')>(119.40987056283161*b('s'))+169.81179413848707)&&(b('h')<(62.88747617389189*b('s'))+192.89228050816078))||((b('h')>(-317.05551175659076*b('s'))+286.882084995492)&&(b('h')>(244.34605806690413*b('s'))+118.79505990525014)&&(b('h')<(119.40987056283161*b('s'))+169.81179413848707))||((b('h')<(244.34605806690413*b('s'))+118.79505990525013)&&(b('h')>(38.657063321438876*b('s'))+180.37958883957006)&&(b('h')<(0.7855098741218717*b('s'))+218.25114228688705))||((b('h')>(59.99027169469099*b('s'))+159.04638046631794)&&(b('h')<(38.657063321438876*b('s'))+180.37958883957006)&&(b('h')>(-70.42121412059574*b('s'))+213.03828475836497))||((b('h')<(59.99027169469099*b('s'))+159.04638046631794)&&(b('h')>(-63.190713604259756*b('s'))+210.04477165312707)&&(b('h')>(71.3322190203302*b('s'))+147.70443314067873))||((b('h')<(71.3322190203302*b('s'))+147.70443314067873)&&(b('h')>(-132.8395919398703*b('s'))+242.32131043905457)&&(b('h')>(97.78926528286257*b('s'))+121.24738687814636))||((b('h')>(-55.64206460129677*b('s'))+201.7946927528083)&&(b('h')>(10000000*b('s'))-9999853.847371848)&&(b('h')<(97.78926528286257*b('s'))+121.24738687814636))||((b('h')<(-55.64206460129677*b('s'))+201.7946927528083)&&(b('h')>(-70.89697101755921*b('s'))+209.8031067718208)&&(b('h')>(-26.931356210984664*b('s'))+173.08398436249618))||((b('h')>(-26.262128232850145*b('s'))+172.5250597538679)&&(b('h')<(-70.89697101755921*b('s'))+209.8031067718208)&&(b('h')>(-361.4610456160576*b('s'))+362.3414013335865))||((b('h')<(-26.262128232850145*b('s'))+172.5250597538679)&&(b('h')>(-49.10093639625872*b('s'))+185.4582131347398)&&(b('h')>(-1.561849811608879*b('s'))+151.8959260346158))||((b('h')<(-26.931356210984664*b('s'))+173.08398436249618)&&(b('h')>(-38.71382455329052*b('s'))+182.92444489622275)&&(b('h')>(4.488559368497584*b('s'))+141.66406878301393))||((b('h')>(-38.65578283731854*b('s'))+199.88701886395202)&&(b('h')<(-70.42121412059574*b('s'))+213.03828475836497)&&(b('h')>(-214.9227838798176*b('s'))+256.30292861985987))||((b('h')<(-317.05551175659076*b('s'))+286.882084995492)&&(b('h')>(-717.4513294606268*b('s'))+394.2776694687533)&&(b('h')>(-124.55752247580413*b('s'))+229.2470228701161))"}
]
sensors = [
  {"name":"Landsat 5", "collectionid":"LANDSAT/L5_L1T_TOA", "startDate":"8/13/1983", "endDate":"10/15/1984", "Blue":"10", "Green":"20", "Red":"30", "NIR":"40", "SWIR1":"50", "SWIR2":"70", "TIR":"60"},
  {"name":"Landsat 7", "collectionid":"LANDSAT/LE7_L1T_TOA", "startDate":"8/13/2012", "endDate":"10/15/2012", "Blue":"B1", "Green":"B2", "Red":"B3", "NIR":"B4", "SWIR1":"B5", "SWIR2":"B7", "TIR":"B6_VCID_2"},
  {"name":"Landsat 8", "collectionid":"LANDSAT/LC8_L1T_TOA", "startDate":'8/22/2014', "endDate":'9/12/2014', "Blue":"B2", "Green":"B3", "Red":"B4", "NIR":"B5", "SWIR1":"B6", "SWIR2":"B7", "TIR":"B10"}
]
class GoogleEarthEngineError(Exception):
    """Exception Class that allows the DOPA Services REST Server to raise custom exceptions"""
    pass  
 
def getSensorInformation(scene):  # returns the sensor information based on the passed scene
#     logging.info(scene.getInfo().keys())
    try:
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
    except (EEException)as e:
        raise GoogleEarthEngineError("Unable to get sensor information. You may be calling this method from an imageCollection.map() function which does not support getInfo()")
    
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

def detectWater(image, sensor=None, applyCloudMask=True, applySnowMask=True, applySlopeMask=False, applyNDVIMask=False, applyTemperatureMask=False, applyBareRockMask=False):
    # get the sensor information from the scene if it isnt already known
    if not sensor:
        try:
            sensor = getSensorInformation(image)
        except (GoogleEarthEngineError) as e:
            sensor = sensors[2] #use landsat 8 as the default value if you cant get the sensor information
            print e
    # add a band for no data areas
    image = image.addBands(ee.call('Image.not', image.expression("b('" + sensor['TIR'] + "')>0").mask()).clip(image.geometry()).select([sensor['TIR']], ["isEmpty"]))
    # add a band for the ndvi
    image = image.addBands(image.normalizedDifference([sensor['NIR'], sensor['Red']]).select(["nd"], ["ndvi"]))
    # compute the terrain if required
    if applySnowMask or applySlopeMask:
      terrain = ee.call('Terrain', ee.Image('srtm90_v4')).clip(image.geometry())
    # MASKS SECTION
    # add a band for the cloud mask
    if applyCloudMask:
        # add a band for areas where the temperature is low enough for cloud
        image = image.addBands(image.expression("b('" + sensor['TIR'] + "')<" + str(lowerSceneTempThreshold)).select([sensor['TIR']], ["cloud_temp_ok"]))
        # add a band for areas where the ndvi is low enough for cloud
        image = image.addBands(image.expression("b('ndvi')<" + str(cloudNDVIThreshold)).select(["ndvi"], ["cloud_ndvi_ok"]))
        # add a band for areas where the hsv 654 is ok for cloud
        image = image.addBands(convertToHsv(image, sensor['SWIR1'] + "," + sensor['NIR'] + "," + sensor['Red']))
        image = image.addBands(image.expression("((b('h')>(-63.9767458759244*b('v'))+126.96415795606003)&&(b('h')<(-110.99212035041235*b('v'))+188.63866879085975)&&(b('h')<(603.2197202957016*b('v'))-37.718566327653065))||((b('h')>(25944.551568789888*b('v'))-33990.88089314458)&&(b('h')<(36.86094838605795*b('v'))+141.77916585585064)&&(b('h')>(-110.99212035041235*b('v'))+188.63866879085975))||((b('h')<(2.706669936469208*b('v'))+186.77647545634971)&&(b('h')<(106.69607879660673*b('v'))+119.64611493979173)&&(b('h')>(36.86094838605795*b('v'))+141.77916585585064))||((b('h')<(81.81592861333533*b('v'))+135.70749532282187)&&(b('h')<(176.29751158778367*b('v'))+97.58713048968069)&&(b('h')>(106.69607879660673*b('v'))+119.64611493979172))||((b('h')>(81.81592861333533*b('v'))+135.70749532282187)&&(b('h')<(63.82071478662236*b('v'))+147.32430519799433)&&(b('h')<(109.53269473723807*b('v'))+124.52464673608978))||((b('h')<(8.966684960846429*b('v'))+182.73532290022047)&&(b('h')>(2.706669936469208*b('v'))+186.77647545634971)&&(b('h')<(1.3539150425983255*b('v'))+188.55869231281008))||((b('h')>(-634.8621367931978*b('v'))+267.8746186626148)&&(b('h')>(-14.34796731410254*b('v'))+61.86139794741938)&&(b('h')<(-63.9767458759244*b('v'))+126.96415795606003))||((b('h')<(-14.34796731410254*b('v'))+61.86139794741938)&&(b('h')>(-114.63190817087207*b('v'))+95.15607300578044)&&(b('h')>(1.1835799314009672*b('v'))+41.48719930323337))").select(["h"], ["cloud_hsv_654_ok"]))
        # add a band for areas where the hsv 432 is ok for cloud
        image = image.addBands(convertToHsv(image, sensor['Red'] + "," + sensor['Green'] + "," + sensor['Blue']), None, True)
        image = image.addBands(image.expression("((b('h')<(490.8082696335494*b('v'))+79.95677350110236)&&(b('h')>(-91.39829801435039*b('v'))+235.14099783080272)&&(b('h')>(1426.1409800726237*b('v'))-262.4401146190752))||((b('h')<(-91.39829801435039*b('v'))+235.14099783080272)&&(b('h')>(-1462.3727682296092*b('v'))+600.5673285499772)&&(b('h')>(43.0109637714587*b('v'))+191.06997379295458))||((b('h')<(193.9753887166038*b('v'))+188.61827286211468)&&(b('h')<(1426.1409800726237*b('v'))-262.4401146190752)&&(b('h')>(276.2440822973692*b('v'))+114.59591064872176))||((b('h')>(193.9753887166038*b('v'))+188.61827286211468)&&(b('h')<(4.324914848340889*b('v'))+359.25883441225426)&&(b('h')<(31201.82786617771*b('v'))-11162.414442104384))||((b('h')>(-7586.058735191112*b('v'))+2692.54129818123)&&(b('h')>(336.94797401444475*b('v'))+59.976768604942734)&&(b('h')<(276.2440822973692*b('v'))+114.59591064872174))||((b('h')<(336.94797401444475*b('v'))+59.97676860494278)&&(b('h')>(-120.38370866692127*b('v'))+211.93362163645094)&&(b('h')<(-607.9749503868337*b('v'))+910.1838635444369))||((b('h')>(-17.228323217984126*b('v'))+64.21096650884475)&&(b('h')<(-120.38370866692127*b('v'))+211.93362163645097)&&(b('h')>(-1052.9083931253128*b('v'))+521.7820790922744))||((b('h')>(-4.838229766817528*b('v'))+46.46785504723803)&&(b('h')<(-17.228323217984126*b('v'))+64.21096650884475)&&(b('h')>(-113.58235093045452*b('v'))+106.78088838272488))||((b('h')<(-4.838229766817528*b('v'))+46.46785504723803)&&(b('h')>(-2611.3799432671185*b('v'))+1492.1408309694498)&&(b('h')>(18.14135712802163*b('v'))+13.560163654610307))||((b('h')<(-7243.576669583244*b('v'))+10412.632039788463)&&(b('h')<(18.14135712802163*b('v'))+13.560163654610307)&&(b('h')>(-27.301183714976023*b('v'))+39.11251888901155))||((b('h')<(-27.301183714976023*b('v'))+39.11251888901155)&&(b('h')<(50.865139764507866*b('v'))-4.840429776768538)&&(b('h')>(-17.46625242379369*b('v'))+24.974636828442005))||((b('h')<(-17.46625242379369*b('v'))+24.974636828442)&&(b('h')>(10000000*b('v'))-4363287.073623016)&&(b('h')>(-0.13337531632500316*b('v'))+0.058329326076244706))").select(["h"], ["cloud_hsv_432_ok"]))
        cloudMask = image.expression("(b('cloud_temp_ok'))||(b('cloud_ndvi_ok')==1&&b('cloud_hsv_654_ok')==1&&b('cloud_hsv_432_ok')==1)").select(["cloud_temp_ok"], ["isCloud"])
        image = image.addBands(cloudMask.convolve(ee.Kernel.fixed(5, 5, [[0, 0, 1, 0, 0], [0, 1, 1, 1, 0], [1, 1, 1, 1, 1], [0, 1, 1, 1, 0], [0, 0, 1, 0, 0]])).expression("b('isCloud')>0"))
    else:
        image = image.addBands(ee.Image(0).clip(image.geometry()).select([0], ["isCloud"]))
    # add a band for the snow mask
    if applySnowMask:
      # add a band for areas which are higher than the snowNorthThreshold degrees latitude
      image = image.addBands(ee.Image.pixelLonLat().expression("b('latitude')>" + str(snowNorthThreshold)).select(["latitude"], ["snow_lat_ok"]))
      # add a band for areas which are higher than the snowAltitudinalThreshold
      image = image.addBands(terrain.expression("b('elevation')>" + str(snowAltitudinalThreshold)).mask(1).select(["elevation"], ["snow_alt_ok"]))
      # add a band for areas where the hsv 432 is ok for snow
      image = image.addBands(convertToHsv(image, sensor['Red'] + "," + sensor['Green'] + "," + sensor['Blue']), None, True)
      image = image.addBands(image.expression("b('v')>" + str(snowValueThreshold)).select(["v"], ["snow_v_ok"]))
      image = image.addBands(image.expression("b('s')<" + str(snowSatThreshold)).select(["s"],["snow_s_ok"]))
      # add a band for areas where the temperature is low enough for snow
      image = image.addBands(image.expression("b('" + sensor['TIR'] + "')<" + str(snowTemperatureThreshold)).select([sensor['TIR']], ["snow_temp_ok"]))
      image = image.addBands(image.expression("b('snow_v_ok')==1&&b('snow_s_ok')==1&&b('snow_temp_ok')==1&&(b('snow_lat_ok')==1||b('snow_alt_ok')==1)").select(["snow_v_ok"], ["isSnow"]))
    # add a band for the slope mask
    if applySlopeMask:
        slope_radians = terrain.select(['slope']).expression("(b('slope')*" + str(math.pi) + ")/180")
        slope_areas = slope_radians.expression("(b('slope')>" + str(slopeMaskThreshold) + ")")
        image = image.addBands(slope_areas.select(["slope"], ["isSteep"]))
    # add a band for the ndvi mask
    if applyNDVIMask:
        image = image.addBands(image.expression("b('ndvi')>" + str(ndviMaskThreshold)).select(["ndvi"], ["isGreen"]))
    # add a band for the temperature mask
    if applyTemperatureMask:
        image = image.addBands(ee.call('Image.not', image.expression("b('" + sensor['TIR'] + "')<" + str(upperSceneTempThreshold) + "&&b('" + sensor['TIR'] + "')>" + str(lowerSceneTempThreshold))).select([sensor['TIR']], ["isTooHotOrCold"]))
    # add a band for the barerock mask
    if applyBareRockMask:
        landsat_collection = ee.ImageCollection("LANDSAT/LC8_L1T_TOA").filterDate(datetime.datetime(2013, 4, 1), datetime.datetime(2014, 4, 1)).filterBounds(image.geometry())
        image = image.addBands(image.expression("((b('B3')<(0.8255813953488379*b('B5'))+0.026636991279069665)&&(b('B3')>(-0.2499999999999994*b('B5'))+0.04058593750000021)&&(b('B3')>(1.6000000000000014*b('B5'))+0.006187499999999648))||((b('B3')<(-0.40000000000000063*b('B5'))+0.059000000000000295)&&(b('B3')<(1.6000000000000014*b('B5'))+0.006187499999999645)&&(b('B3')>(0.5523809523809521*b('B5'))+0.025666666666666657))||((b('B3')<(1*b('B5'))+0.022031249999999863)&&(b('B3')>(-0.40000000000000063*b('B5'))+0.059000000000000295)&&(b('B3')>(3.264705882352946*b('B5'))-0.06926470588235396))||((b('B3')>(0.4457478005865104*b('B5'))+0.02939882697947215)&&(b('B3')<(0.13355048859934848*b('B5'))+0.05695999592833889)&&(b('B3')<(3.264705882352946*b('B5'))-0.06926470588235398))||((b('B3')<(-0.09328358208955286*b('B5'))+0.07698519123134354)&&(b('B3')<(1.6923076923076947*b('B5'))-0.005877403846154289)&&(b('B3')>(0.13355048859934848*b('B5'))+0.05695999592833889))||((b('B3')<(-1.3106060606060648*b('B5'))+0.18445194128787978)&&(b('B3')<(1.088235294117649*b('B5'))+0.022155330882352706)&&(b('B3')>(-0.09328358208955286*b('B5'))+0.07698519123134354))||((b('B3')<(0.6903765690376558*b('B5'))+0.04907296025104613)&&(b('B3')>(-1.3106060606060648*b('B5'))+0.18445194128787978)&&(b('B3')>(3.1588785046728995*b('B5'))-0.2101197429906553))||((b('B3')<(-1.0582524271844669*b('B5'))+0.2326790048543696)&&(b('B3')<(3.1588785046728995*b('B5'))-0.21011974299065528)&&(b('B3')>(0.3833865814696488*b('B5'))+0.03490415335463261))||((b('B3')<(0.38314176245210746*b('B5'))+0.0813326149425288)&&(b('B3')>(-1.0582524271844669*b('B5'))+0.2326790048543696)&&(b('B3')>(5.78181818181818*b('B5'))-0.7056931818181835))||((b('B3')<(-0.8358778625954201*b('B5'))+0.2590428196564891)&&(b('B3')<(5.78181818181818*b('B5'))-0.7056931818181834)&&(b('B3')>(0.3123028391167197*b('B5'))+0.0446559542586751))||((b('B3')<(-1.4397905759162286*b('B5'))+0.3718046465968591)&&(b('B3')<(0.7887323943662009*b('B5'))+0.022205105633802222)&&(b('B3')>(-0.8358778625954201*b('B5'))+0.2590428196564891))||((b('B3')<(-3.0842105263157817*b('B5'))+0.6788486842105264)&&(b('B3')<(0.18749999999999953*b('B5'))+0.11652343750000027)&&(b('B3')>(-1.4397905759162286*b('B5'))+0.3718046465968591))||((b('B3')>(0.8272727272727277*b('B5'))-0.051498579545454726)&&(b('B3')<(-0.985365853658536*b('B5'))+0.3181097560975614)&&(b('B3')>(-3.0842105263157817*b('B5'))+0.6788486842105262))||((b('B3')<(-1.8872180451127856*b('B5'))+0.5020030545112799)&&(b('B3')<(0.6805555555555519*b('B5'))+0.03177951388888953)&&(b('B3')>(-0.985365853658536*b('B5'))+0.3181097560975614))||((b('B3')<(-0.6589147286821698*b('B5'))+0.27707000968992285)&&(b('B3')>(-1.8872180451127856*b('B5'))+0.5020030545112799)&&(b('B3')>(0.648*b('B5'))-0.014943750000000033))||((b('B3')<(-12.333333333333234*b('B5'))+2.88557291666665)&&(b('B3')<(0.5384615384615392*b('B5'))+0.05780048076923067)&&(b('B3')>(-0.6589147286821698*b('B5'))+0.27707000968992285))||((b('B3')<(-1.365384615384615*b('B5'))+0.4760516826923084)&&(b('B3')>(-12.333333333333234*b('B5'))+2.88557291666665)&&(b('B3')>(0.6287878787878773*b('B5'))-0.010651041666666361))||((b('B3')>(-1.365384615384615*b('B5'))+0.4760516826923084)&&(b('B3')>(1.2953020134228208*b('B5'))-0.1733221476510075)&&(b('B3')<(-0.06557377049180299*b('B5'))+0.19049948770491826))||((b('B3')>(8.062500000000188*b('B5'))-1.9824902343750537)&&(b('B3')<(1.2953020134228208*b('B5'))-0.1733221476510075)&&(b('B3')>(0.48120300751879613*b('B5'))+0.02536889097744384))||((b('B3')<(-2.323943661971829*b('B5'))+0.7942605633802824)&&(b('B3')<(0.6196581196581197*b('B5'))+0.03996260683760686)&&(b('B3')>(-0.06557377049180299*b('B5'))+0.19049948770491826))||((b('B3')<(-0.20600858369098746*b('B5'))+0.2515396995708159)&&(b('B3')>(-2.323943661971829*b('B5'))+0.7942605633802824)&&(b('B3')>(0.7222222222222233*b('B5'))-0.020112847222222535))||((b('B3')<(0.4918566775244293*b('B5'))+0.07271172638436507)&&(b('B3')>(-0.20600858369098746*b('B5'))+0.2515396995708159)&&(b('B3')>(2.689189189189159*b('B5'))-0.5957580236486406))||((b('B3')<(-3.0000000000000853*b('B5'))+1.135000000000028)&&(b('B3')<(2.689189189189159*b('B5'))-0.5957580236486406)&&(b('B3')>(1.252525252525252*b('B5'))-0.17530934343434348))||((b('B3')<(0.12631578947368488*b('B5'))+0.18391611842105268)&&(b('B3')>(-3.0000000000000853*b('B5'))+1.135000000000028)&&(b('B3')>(0.6000000000000006*b('B5'))+0.025749999999999856))").select(["B3"],["bareRockConfusionArea"]))
        image = image.addBands(landsat_collection.select([sensor['TIR']], ["rock_temp_ok"]).max().expression('b("rock_temp_ok")>' + str(annualMaxTempThreshold)))
        bandnames = getGEEBandNames("NIR,Red", sensor).split(",")
        ndvi_images = []
        for feature in landsat_collection.getInfo()['features']:
            ndvi_images.append(ee.Image(feature['id']).normalizedDifference([bandnames[0], bandnames[1]]))
        landsat_collection_ndvi = ee.ImageCollection(ndvi_images)
        isrock = landsat_collection_ndvi.max().clip(image.geometry())
        image = image.addBands(isrock.expression('b("nd")<' + str(annualMaxNDVIThreshold)).select(["nd"], ["rock_ndvi_ok"]))
        image = image.addBands(image.expression("b('bareRockConfusionArea')==1&&b('rock_temp_ok')==1&&b('rock_ndvi_ok')==1").select(['bareRockConfusionArea'], ['isRock']))
    # add a band for the total mask - this adds all bands with the prefix 'is*' 
    image = image.addBands(ee.call('Image.not', image.select(["is.*"]).reduce(ee.Reducer.anyNonZero())).select(["any"], ["detectArea"]))
    # detect water
    for i in range(len(waterDetectExpressions)):
        waterDetectExpression = waterDetectExpressions[i]
        # convert the band descriptions to actual band names according to the sensor, e.g. "SWIR2,NIR,Red" -> "B7,B5,B4" for landsat
        bands = getGEEBandNames(waterDetectExpression['bands'], sensor)
        # convert to hsv
        hsv = convertToHsv(image, bands)
        detection = hsv.expression(waterDetectExpression['expression'])
        image = image.addBands(detection.select([0], ["detectExpression" + str(i + 1)]))
    # add a band for the total detections - this combines all the bands with the prefix 'detect'
    image = image.addBands(image.select(["detect.*"]).reduce(ee.Reducer.allNonZero()).select(["all"], ["water"]))
    # create a final water detection layer with 0-not water (grey), 1=no data (black), 2=cloud(white), 3=water(blue)
    detection = image.expression("b('isEmpty')+((b('isCloud')||b('isSnow'))*2)+(b('water')*3)").select(["isEmpty"], ["class"])
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
