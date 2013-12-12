import sys, ee, cPickle
from ee import EEException

class GoogleEarthEngineError(Exception):
    """Exception Class that allows the DOPA Services REST Server to raise custom exceptions"""
    pass  

def getValuesForPoint(sceneid, lat, lng):
    try:
        authenticate()
        scene = ee.Image(sceneid)
        collection = ee.ImageCollection(scene)
        data = collection.getRegion(ee.Geometry.Point(lng, lat), 30).getInfo()
        return dict([(data[0][i], data[1][i]) for i in range (len(data[0]))])
    
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
