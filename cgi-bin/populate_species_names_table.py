# Python module to populate the species names table for species common names for DOPA
# TODO This module should be moved to another machine for running and not run on the REST Services machine
import logging, psycopg2, gbif
from dbconnect import dbconnect
from gbif import GBIFServiceError

# logging.basicConfig(filename='../../htdocs/mstmp/populate_species_names_table.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s',)
count = 1
conn = dbconnect("species_especies_schema")
conn.cur.execute("delete from species_names;")
conn.cur.execute("select distinct id_no,friendly_n from species_distribution.speciestaxonomy where friendly_n is not null;")
rows = conn.cur.fetchall()
for row in rows:
    IDspecies = row[0]
    binomial = row[1]
    try:
        nubkey = gbif.getNubKey(binomial)
        commonnames = gbif.getVernacularNames(nubkey)            
        if len(commonnames) > 0:
            for commonname in commonnames:
                language = commonname[0]
                name = commonname[1]
                conn.cur.execute("INSERT INTO species_names(iucn_species_id, name, language) VALUES (" + IDspecies + ",'" + name + "','" + language + "');")
    except (GBIFServiceError):
#         logging.error("GBIFServiceError: " + str(sys.exc_info()) + " (record " + str(count) + ")")
        continue
    count = count + 1
conn.cur.execute('CREATE INDEX sn2 ON species_names USING btree (language COLLATE pg_catalog."default")')
conn.close()
