# Python module that refetches the image dates for all of the validation sites in the gee_training_data from the Google Earth Engine Python API. 
# TODO This module should be moved to another machine for running and not run on the REST Services machine
import earthEngine
from dbconnect import dbconnect
conn = dbconnect("species_especies_schema")
conn.cur.execute("SELECT DISTINCT sceneid FROM gee_training_data;")
scenes = conn.cur.fetchall()
count = 1
for scene in scenes:
    datetime = earthEngine.getDateTimeForScene(scene[0])
    print scene[0] + " " + datetime
    conn.cur.execute("UPDATE gee_training_data SET image_date='" + datetime + "' WHERE sceneid='" + scene[0] + "';")