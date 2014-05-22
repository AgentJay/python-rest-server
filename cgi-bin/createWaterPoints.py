# Routine to create 10,000 water points from the water detection algorithm so we can get the accuracy of the method
import psycopg2, subprocess
from dbconnect import dbconnect
PYTHON_PATH = '/usr/bin/python'
WORKER_SCRIPT = '/srv/www/dopa-services/cgi-bin/createWaterPointsSub.py'
conn = dbconnect("species_especies_schema")
# conn.cur.execute("delete from gee_validated_sites;")
# sql = "SELECT DISTINCT landsat_wrs2.path,  landsat_wrs2.row,  st_x(st_centroid(landsat_wrs2.geom)),  st_y(st_centroid(landsat_wrs2.geom)), l8_toa_scene_count, l8_toa_cloud_stats FROM especies.landsat_wrs2 WHERE l8_toa_scene_count>0 ORDER BY 1,2;"
sql = "SELECT DISTINCT landsat_wrs2.path,  landsat_wrs2.row,  st_x(st_centroid(landsat_wrs2.geom)),  st_y(st_centroid(landsat_wrs2.geom)), l8_toa_scene_count, l8_toa_cloud_stats FROM especies.landsat_wrs2 WHERE l8_toa_scene_count>0 AND path>24 ORDER BY 1,2;"
conn.cur.execute(sql)
print "Creating random water validation sites..\n" 
pathRows = conn.cur.fetchall()
try:
    for pathRow in pathRows:
        path = str(pathRow[0])
        row = str(pathRow[1])
        print "\npath: " + path + " row: " + row + "\n========================================================================================================="
        p = subprocess.Popen([PYTHON_PATH, WORKER_SCRIPT , path, row ])
        p.wait()
        print p
#         p.kill()
except (Exception) as e:
    print e
finally:
    conn.conn.close()
