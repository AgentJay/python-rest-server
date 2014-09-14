import ee, datetime, math, json,urllib
from ee import EEException
MY_SERVICE_ACCOUNT = '382559870932@developer.gserviceaccount.com'
MY_PRIVATE_KEY_FILE = '/Users/andrewcottam/Documents/Aptana Studio 3 Workspaces/GitHub Repositories/python-rest-server/cgi-bin/Google Earth Engine Python API Private Key.p12'

sensor = {"name":"Landsat 8", "collectionid":"LANDSAT/LC8_L1T_TOA", "startDate":'8/13/2013', "endDate":'10/15/2013', "Blue":"B2", "Green":"B3", "Red":"B4", "NIR":"B5", "SWIR1":"B6", "SWIR2":"B7", "TIR":"B10"}
cloudLowerTemperatureThreshold = 262.15  # Pixels with a temperature lower than this threshold may be clouds
cloudNDVIThreshold = 0.11  # Pixels with an NDVI lower than this threshold may be clouds
snowNorthThreshold = 31  # Pixels with a latitude further north than this will be tested for snow
snowAltitudinalThreshold = 3000  # Pixels with a height greater than this will be tested for snow
snowValueThreshold = 0.2  # Pixels with a value greater than this will be tested for snow 
snowTemperatureThreshold = 282.15  # Pixels with a temperature less than this will be tested for snow 
slopeMaskThreshold = 0.17  # Pixels with a slope greater than this threshold in radians will be excluded
ndviMaskThreshold = 0.1  # Pixels with an NDVI greater than this threshold will be excluded
lowerSceneTempThreshold = 272.15  # lower temperature threshold for the scene
upperSceneTempThreshold = 310  # upper temperature threshold for the scene
annualMaxTempThreshold = 310  # Threshold for the max annual temperature above which bare rock could be present
annualMaxNDVIThreshold = 0.14  # Threshold for the max annual NDVI below which bare rock will be present
temperatureDifferenceThreshold = 9  # Pixels with a day/night temperature difference greater than this threshold will be excluded
sunElevationThreshold = 23  # Landsat scenes with a solar elevation angle greater than this angle will be included
waterDetectExpressions = [
  {"bands":"SWIR2,NIR,Red", "expression":"((b('h')<(3.038667895460303*b('v'))+236.62216730574633)&&(b('h')<(10796.714793390856*b('v'))+204.85937891753062)&&(b('h')>(52.75476688685699*b('v'))+209.3760200216838))||((b('h')>(3.038667895460303*b('v'))+236.62216730574633)&&(b('h')<(2.0464628168010686*b('v'))+237.16593011613543)&&(b('h')<(9.076683306759795*b('v'))+236.60439910485127))||((b('h')<(-0.24666028009321075*b('v'))+238.42264113944557)&&(b('h')<(9.88710145914933*b('v'))+236.539667859889)&&(b('h')>(2.0464628168010686*b('v'))+237.1659301161354))||((b('h')>(-43.65372607478519*b('v'))+209.41654907810485)&&(b('h')<(-11433.100423818365*b('v'))+6504.023197860868)&&(b('h')<(52.75476688685699*b('v'))+209.3760200216838))||((b('h')>(26.243531044391943*b('v'))+170.78642497548128)&&(b('h')<(-43.65372607478519*b('v'))+209.41654907810485)&&(b('h')>(-1107.3553634247025*b('v'))+209.86371739648635))||((b('h')>(295.7226981444027*b('v'))+21.853346666047287)&&(b('h')<(26.243531044391943*b('v'))+170.78642497548128)&&(b('h')>(8.433335884642577*b('v'))+171.4003760014821))||((b('h')<(8.433335884642577*b('v'))+171.4003760014821)&&(b('h')>(-31.37019423910757*b('v'))+172.77247877400865)&&(b('h')>(82.71930111287884*b('v'))+132.73119126796098))||((b('h')<(-31.37019423910757*b('v'))+172.77247877400865)&&(b('h')>(-115.8110462176276*b('v'))+175.68331423895395)&&(b('h')>(4.932732579069547*b('v'))+160.0314641384984))||((b('h')<(-115.8110462176276*b('v'))+175.68331423895395)&&(b('h')>(-212.72738738403356*b('v'))+179.02420335115374)&&(b('h')>(7.045573926497733*b('v'))+159.75757941842787))"},
  {"bands":"SWIR2,Green,Blue", "expression":"((b('s')>(0.3402310087582287*b('v'))+0.6878785247108777)&&(b('s')<(-0.22139589479141922*b('v'))+1.0009733932691036)&&(b('s')<(114.04465599671092*b('v'))+0.38090113543454673))||((b('s')>(11.178032732580114*b('v'))-5.353961858528813)&&(b('s')<(0*b('v'))+0.9997719738616231)&&(b('s')>(-0.22139589479141922*b('v'))+1.0009733932691036))||((b('s')>(-6.555760168973008*b('v'))+0.706496211475811)&&(b('s')>(0.9781716036464391*b('v'))+0.33224042147527677)&&(b('s')<(0.3402310087582287*b('v'))+0.6878785247108777))||((b('s')>(0.19217317709040418*b('v'))+0.37128569968432384)&&(b('s')>(1.539711633483847*b('v'))+0.019193983135302795)&&(b('s')<(0.9781716036464391*b('v'))+0.33224042147527677))||((b('s')<(0.19217317709040418*b('v'))+0.37128569968432384)&&(b('s')>(-0.21980966748266745*b('v'))+0.3917513701490769)&&(b('s')>(0.4354503844174411*b('v'))+0.307720990923226))"},
]

def getGEEBandNames(bands, sensor):  # gets the corresponding gee band names from their descriptions, e.g. SWIR2,NIR,Red -> B7,B5,B4 for Landsat 8 object
    geebandnames = []
    bandnames = bands.split(",")
    for band in bandnames:
        geebandnames.append(sensor[band])
    return ",".join([b for b in geebandnames])

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

def detectWater(image):
    applyCloudMask = True
    applySnowMask = True
    applySlopeMask = False
    applyNDVIMask = False
    applyTemperatureMask = False
    applyBareRockMask = False
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
      image = image.addBands(terrain.expression("b('elevation')>" + str(snowAltitudinalThreshold)).mask().select(["elevation"], ["snow_alt_ok"]))
      # add a band for areas where the hsv 432 is ok for snow
      image = image.addBands(convertToHsv(image, sensor['Red'] + "," + sensor['Green'] + "," + sensor['Blue']), None, True)
      image = image.addBands(image.expression("b('v')>" + str(snowValueThreshold)).select(["v"], ["snow_v_ok"]))
      # add a band for areas where the temperature is low enough for snow
      image = image.addBands(image.expression("b('" + sensor['TIR'] + "')<" + str(snowTemperatureThreshold)).select([sensor['TIR']], ["snow_temp_ok"]))
      image = image.addBands(image.expression("b('snow_v_ok')==1&&b('snow_temp_ok')==1&&(b('snow_lat_ok')==1||b('snow_alt_ok')==1)").select(["snow_v_ok"], ["isSnow"]))
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
    # add a band for the total mask - this adds all bands with the prefix 'is' 
#     maskbands = ["isCloud", "isSnow", "isSteep", "isGreen", "isTooHotOrCold"]
    maskbands = ["isCloud", "isSnow" ]
    image = image.addBands(ee.call('Image.not', image.select(maskbands).reduce(ee.Reducer.anyNonZero())).select(["any"], ["detectArea"]))
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
    detectbands = ["detectExpression1", "detectExpression2"]
    image = image.addBands(image.select(detectbands).reduce(ee.Reducer.allNonZero()).select(["all"], ["water"]))
    water = image.select(["water"]).mask(image.select(["water"]))
    waterArea = water.multiply(ee.Image.pixelArea())
    totalArea = waterArea.reduceRegion(ee.Reducer.sum(), poly, 30, None, None, True);
    water = water.set({'totalArea':totalArea})
    return water

ee.Initialize(ee.ServiceAccountCredentials(MY_SERVICE_ACCOUNT, MY_PRIVATE_KEY_FILE))
poly = ee.Geometry.Polygon([[-46.5, -23.1], [-46.3, -23.1], [-46.3, -22.9], [-46.5, -22.9], [-46.5, -23.1]])
landsat_collection = ee.ImageCollection("LANDSAT/LC8_L1T_TOA").filterDate(datetime.datetime(2013, 7, 1), datetime.datetime(2014, 8, 18)).filterBounds(poly)  # .filterMetadata('CLOUD_COVER', "less_than", 10)
detections = landsat_collection.map(detectWater)
keys = ['totalArea', 'date', 'sceneid', 'cloudCover']
data = [(str(f['properties']['totalArea']['water']), str(f['properties']['DATE_ACQUIRED']), str(f['id']), str(f['properties']['CLOUD_COVER'])) for f in detections.getInfo()['features']]
dataDict = [dict([(keys[col], data[row][col]) for col in range(len(keys))]) for row in range(len(data))]
print json.dumps(dict([('results', dataDict)]), indent=1)
geojson = '{"type":"Polygon","coordinates":[[[100.0, 0.0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]}'
for row in data:
    values = {"q":"INSERT INTO water_stats (the_geom, cloudcover,date,sceneid,totalarea) VALUES (ST_SetSRID(ST_GeomFromGeoJSON('" + geojson + "'),4326),10,'1999','landsat','22')", "api_key":"f9e4705e00d2478eb9780388d293544eb5a7a330"}       
    data = urllib.urlencode(values) 
    response = urllib.urlopen("http://andrewcottam.cartodb.com/api/v2/sql", data)
    response.read()