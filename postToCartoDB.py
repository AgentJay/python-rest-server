import urllib
geojson = '{"type":"Polygon","coordinates":[[[100.0, 0.0],[101.0,0.0],[101.0,1.0],[100.0,1.0],[100.0,0.0]]]}'
date = 1999
values = {"q":"INSERT INTO water_stats (the_geom, date) VALUES ( ST_SetSRID(ST_GeomFromGeoJSON('" + geojson + "'), 4326), " + str(date) + ")", "api_key":"f9e4705e00d2478eb9780388d293544eb5a7a330"}       
data = urllib.urlencode(values) 
response = urllib.urlopen("http://andrewcottam.cartodb.com/api/v2/sql", data)
print response.read()
