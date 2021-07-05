import logging
import time
import datetime
import json
import os
from nuts_finder import NutsFinder
import sys
sys.path.append('Resources')
import caching



############## INPUT VARIABLES ################
# Version of NUTS
year = 2016

# Optional input for partial processing
start_at = 0

# Optional working with batches
batch = TRUE    # If TRUE, batch number has to be specified according to file names
batch_nr = 1

if batch:
    log_dir = 'LOGS/batch%s_LOG_Nuts_Geocode.log' % batch_nr
    import_dir = 'data/raw_data/batch%s_twitter_geoloc_export.json' % batch_nr
    export_dir = 'data/raw_data/batch%s_nuts_geoloc_export.json' % batch_nr
else:
    log_dir = 'LOGS/LOG_Nuts_Geocode.log'
    import_dir = 'data/raw_data/twitter_geoloc_export.json'
    export_dir = 'data/raw_data/nuts_geoloc_export.json'
###############################################



# ------------- GLOBAL VARIABLES --------------
count = 0

export_geoloc = {}

logging.basicConfig(filename=log_dir, filemode='a', 
                    format='%(asctime)s [%(levelname)s] - %(message)s', 
                    datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
# ---------------------------------------------



with open(import_dir, "r") as f:
    data = json.load(f)
logging.info('Processing of useres initiated ...')
log_starttime = datetime.datetime.now()



try:


    nf = NutsFinder(year = year)
    for i in data:

        count += 1
        if count >= start_at:

            export_geoloc[str(i)] = data[i]

            #GitHub locations
            try:

                for ii in data[i]['location']:

                    try:
                        nuts = nf.find(float(data[i]['location'][ii]['coordinates']['longitude']),
                                        float(data[i]['location'][ii]['coordinates']['latitude']))
                        nuts3 = nuts[3]['NUTS_ID']
                        export_geoloc[i]['location'][ii]['nuts3'] = nuts3
                    except:
                        export_geoloc[i]['location'][ii]['nuts3'] = 'NaN'

            except:

                pass


            # Twitter location
            try:

                for ii in data[i]['twitter_username']['twitter_location']:

                    try:
                        nuts = nf.find(float(data[i]['twitter_username']['twitter_location'][ii]['coordinates']['longitude']),
                                        float(data[i]['twitter_username']['twitter_location'][ii]['coordinates']['latitude']))
                        nuts3 = nuts[3]['NUTS_ID']
                        export_geoloc[i]['twitter_username']['twitter_location'][ii]['nuts3'] = nuts3
                    except:
                        export_geoloc[i]['twitter_username']['twitter_location'][ii]['nuts3'] = 'NaN'

            except:

                pass


            if count % 100 == 0:
                # Saving new gained info every 100 users
                caching.cache(export_geoloc, export_dir, csv)
                export_geoloc = {}



    caching.cache(export_geoloc, export_dir, csv)
    export_geoloc = {}



except Exception as e:
    logging.warning(e)
    logging.warning(str(e))




log_endtime = datetime.datetime.now()
log_runtime = (log_endtime - log_starttime)
logging.info("Total runtime: " + str(log_runtime))
