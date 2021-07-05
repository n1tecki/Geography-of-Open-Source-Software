import logging
import time
import datetime
import sys
import json
import os
from nuts_finder import NutsFinder



# ------------- GLOBAL VARIABLES --------------
batch_nr = 0
count = 0
start_at = 0

export_geoloc = {}

logging.basicConfig(filename='/home/codeuser/code/LOGS/batch%s_LOG_Nuts_Geocode.log' % batch_nr, filemode='a', 
                    format='%(asctime)s [%(levelname)s] - %(message)s', 
                    datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
# ---------------------------------------------



# ----------- CACHING AND EXPORTING -----------
def cache(export_geoloc, directory):
    logging.info('... ' + str(count) + '/' + str(len(data)) + ' users processed ...')
    
    # Updating exported file with newly cached data
    if os.path.exists(directory) == True:
        with open(directory, 'r+') as outfile:
            cache = json.load(outfile)
            cache.update(export_geoloc) # append new data to existing file
            outfile.seek(0) 
            json.dump(cache, outfile)
        logging.info("%s file updated ..." % directory)
        
    # Creating export file if one doesn't exist yet
    else:
        with open(directory, 'w') as outfile:
            json.dump(export_geoloc, outfile)
        logging.info("retrieved data exported to %s..." % directory)
# ---------------------------------------------



with open('/home/codeuser/code/data/raw_data/batch%s_twitter_geoloc_export.json' % batch_nr, "r") as f:
    data = json.load(f)
logging.info('Processing of useres initiated ...')
log_starttime = datetime.datetime.now()



try:


    nf = NutsFinder(year = 2016)
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
                cache(export_geoloc, '/home/codeuser/code/data/raw_data/batch%s_nuts_geoloc_export.json' % batch_nr)
                export_geoloc = {}



    cache(export_geoloc, '/home/codeuser/code/data/raw_data/batch%s_nuts_geoloc_export.json' % batch_nr)
    export_geoloc = {}



except Exception as e:
    logging.warning(e)
    logging.warning(str(e))




log_endtime = datetime.datetime.now()
log_runtime = (log_endtime - log_starttime)
logging.info("Total runtime: " + str(log_runtime))
