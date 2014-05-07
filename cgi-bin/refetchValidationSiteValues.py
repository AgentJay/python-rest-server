# Python module that refetches the pixel values for all of the validation sites in the gee_training_data from the Google Earth Engine Python API. This module can be used to batch retrieve values if the Landsat archive has been reprocessed or you want to retrieve the values from another collection, e.g. Landsat8_L1T_TOA
# TODO This module should be moved to another machine for running and not run on the REST Services machine
import earthEngine
from dbconnect import dbconnect
def rgbTohsv(r, g, b):
#     print "r:" + str(r) + ",g:" + str(g) + ",b:" + str(b)
    maxVal = float(max(r, g, b))
    minVal = float(min(r, g, b))
    val = maxVal
#     print "maxVal:" + str(maxVal) + ",minVal:" + str(minVal)
    saturation = (val - minVal) / maxVal
    if val == minVal:
        hue = 0
    elif val == r:
        hue = ((((g - b) / (val - minVal)) * 60) + 360) % 360
    elif val == g:
        hue = (((b - r) / (val - minVal) * 60) + 120)
    elif val == b:
        hue = (((r - g) / (val - minVal) * 60) + 240)
    return (hue, saturation, val)

oldCollection = "LANDSAT/LC8_L1T/"
newCollection = "LANDSAT/LC8_L1T_TOA/"
conn = dbconnect("species_especies_schema")
conn.cur.execute("DROP TABLE IF EXISTS tmp;")
conn.cur.execute("CREATE TABLE especies.tmp (lat double precision,  lng double precision, sceneid text, band1 double precision,  band2 double precision,  band3 double precision,  band4 double precision,  band5 double precision,  band6 double precision,  band7 double precision,  band8 double precision,  band9 double precision,  band10 double precision,  band11 double precision,  bqa integer,hue double precision,  saturation double precision,  val double precision)")
conn.cur.execute("CREATE INDEX t1 ON tmp  USING btree  (lat); CREATE INDEX t2  ON tmp  USING btree  (lng);CREATE INDEX t3  ON tmp  USING btree  (sceneid COLLATE pg_catalog.""default"");")
conn.cur.execute("SELECT DISTINCT sceneid FROM gee_training_data;")
scenes = conn.cur.fetchall()
count = 1
for scene in scenes:
    conn.cur.execute("SELECT lng,lat FROM gee_training_data WHERE sceneid='" + scene[0] + "';")
    pointsTuple = conn.cur.fetchall()
    points = [[p[0], p[1]] for p in pointsTuple]
    newsceneid = scene[0].replace(oldCollection, newCollection)  
    data = earthEngine.getValuesForPoints(newsceneid, points)  # send these to GEE to get the pixel values from the new collection
    insertinto = "INSERT INTO tmp(lat, lng, sceneid, band1, band2, band3, band4, band5, band6, band7, band8, band9, band10, band11, bqa, hue, saturation,val) VALUES"
    values = ""
    for i in range(1, len(data)):  # create the VALUES (''),('') statement
        values = values + "(" + str(data[i][2]) + "," + str(data[i][1]) + ",'" + scene[0] + "'"
        for j in range(4, len(data[0])):  # iterate through the bands pixel values to write the string
            values = values + "," + str(data[i][j])
        h, s, v = rgbTohsv(data[i][10], data[i][8], data[i][7])  # bands B7, B5, B4 for Landsat 8
        values = values + "," + str(h) + "," + str(s) + "," + str(v) + "),"
    sql = insertinto + values[:-1]
    conn.cur.execute(sql)
    print "processing scene " + scene[0] + " " + str(count) + " of " + str(len(scenes))
    count = count + 1
sql = "UPDATE gee_training_data SET band1=tmp.band1, band2=tmp.band2, band3=tmp.band3, band4=tmp.band4, band5=tmp.band5, band6=tmp.band6, band7=tmp.band7, band8=tmp.band8, band9=tmp.band9, band10=tmp.band10, band11=tmp.band11, bqa=tmp.bqa, hue=tmp.hue, saturation=tmp.saturation, val=tmp.val FROM especies.tmp WHERE  gee_training_data.lat = tmp.lat AND gee_training_data.sceneid = tmp.sceneid AND tmp.lng = gee_training_data.lng;"
conn.cur.execute(sql)
sql = "UPDATE gee_training_data SET sceneid = '" + newCollection + "' || substr(sceneid,length('" + oldCollection + "')+1)"
conn.cur.execute(sql)
conn.cur.execute("DROP TABLE IF EXISTS tmp;")
