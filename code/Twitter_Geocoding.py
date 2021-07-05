# ----------------- IMPORTING -----------------
import urllib.request
import json
import requests
import sys
import logging
import time
import datetime
import os.path
import csv
# ---------------------------------------------



# ----------- AUTHENTIFIKATION INFO -----------
# Stack with not limited tokens reached
with open('/home/codeuser/code/tokens/bing_tokens.csv', 'r', encoding='utf-8-sig') as tokens:
    reader = csv.reader(tokens, delimiter = ',')
    # Stack with tokens that have not reached limit
    token_ready = list(reader)
    
# Stack with limited tokens 
token_wait = []

bingMapsKey = token_ready.pop(0)[0]
# ---------------------------------------------



# ------------- GLOBAL VARIABLES --------------
batch_nr = 0
count = 0
start_at = 0

export_geoloc = {}
not_found = []   # List of locations not found
maxResults = 5
url = 'http://dev.virtualearth.net/REST/v1/Locations/%s?&maxResults=%s&key=%s'
processed = 0
completed = 0
empty = 0
er_500 = 0
er_404 = 0
er_400 = 0

locations = {}

logging.basicConfig(filename='/home/codeuser/code/LOGS/batch%s_LOG_Twitter_Geocode.log' % batch_nr, filemode='a', 
                    format='%(asctime)s [%(levelname)s] - %(message)s', 
                    datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)

export_directory = '/home/codeuser/code/data/raw_data/batch%s_twitter_geoloc_export.json' % batch_nr
export_directory_2 = '/home/codeuser/code/data/raw_data/batch%s_twitter_geloc_not_found.csv' % batch_nr
# ---------------------------------------------



# ------------- SWITCHING TOKENS --------------
def switch(bingMapsKey):
    token_wait.append(bingMapsKey)
    if len(token_ready) != 0:
        bingMapsKey = token_ready.pop(0)[0]
    else:
        bingMapsKey = token_wait.pop(0)
        response = requests.get(url % (loc_http, maxResults, bingMapsKey))
        if (response.headers['X-MS-BM-WS-INFO']) == 1:
            check_wait(response)         
        
    logging.info("Switching token to: " + str(bingMapsKey))
    return(bingMapsKey)
# ---------------------------------------------



# ----------- CACHING AND EXPORTING -----------
def cache(export_geoloc, directory):
    logging.info('... ' + str(processed) + '/' + str(len(export)) + ' users processed ...' + '(' + str(count) + ')')
    
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


# ------------- CSV CACHING -------------------
def csv_cache(data,directory):
    
    # Updating exported file with newly cached data
    if os.path.exists(directory) == True:
        with open(directory, 'a') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(data)
        logging.info("%s file updated ..." % directory)
        
    # Creating export file if one doesn't exist yet
    else:
        with open(directory, 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(data)
        logging.info("retrieved data exported to %s..." % directory)
# ---------------------------------------------



# ------------------ WAITING ------------------
# Function: Waits until the pull limits are renewed
def check_wait(response):
    logging.info("waiting for API counter reset ... ")
    
    # Checks every minute if limit is renewed
    while response.headers['X-MS-BM-WS-INFO'] == 1:
        time.sleep(60)
        
    logging.info("API rate limit reset!")
    logging.info("Continuing pull requests ...")
# ---------------------------------------------



# --------------- LOADING FILE ----------------
def json_load(file):
    if os.path.exists(file) == True:
        with open(file, 'r+') as outfile:
            return(json.load(outfile))
# ---------------------------------------------



logging.info('Loading of external file ...')

# Loading data
export = json_load('/home/codeuser/code/data/raw_data/batch%s_github_geoloc_export.json' % batch_nr)

logging.info('File successfully loaded ...')
logging.info('Processing of useres initiated ...')
log_starttime = datetime.datetime.now()


try:


    for user in export:
        

        count += 1
        if count >= start_at:


            try:


                try:
                    loc_str = export[user]['twitter_username']['twitter_location']
                except: 
                    loc_str = ''

                
                if loc_str:
                    loc_str = loc_str.lower()
                    
                    # Checks if user input is already associated with a location
                    if loc_str in locations:
                        geo_info = locations[loc_str]
                    # If input is not associated with location, input is crawled
                    else:
                        
                        # Query string tranformed into http readable string
                        loc_http = urllib.parse.quote(loc_str, safe='')
                        
                        # Creating API Query
                        response = requests.get(url % (loc_http, maxResults, bingMapsKey))
                
                        
                        # Checking if token limit reached
                        try:
                            if response.headers['Cache-Control'] == 'no-cache' and response.headers['X-MS-BM-WS-INFO'] == 1:
                                logging.warning("Pull rate limit for reached")
                                bingMapsKey = switch(bingMapsKey)
                                response = requests.get(url % (loc_http, maxResults, bingMapsKey))
                        except:
                            print(response.headers)
                            not_found.append([str(user),loc_str])
                                
                                
                        # crwaling of info
                        if response.status_code == 200:
                            address_index = 0
                            
                            geo_info = {}
                            try:
                                for geo_loc in response.json()['resourceSets'][0]['resources']:
                                    address_index += 1
                                    geo_loc['address']['confidence'] = geo_loc['confidence']
                                    geo_loc['address']['userTyped'] = loc_str
                                    
                                    geo_info[str(address_index)] = geo_loc['address']
                                    # Adding longitude and latitude coordinates
                                    geo_info[str(address_index)]['coordinates'] = {'latitude': geo_loc['point']['coordinates'][0], 
                                                                                'longitude': geo_loc['point']['coordinates'][1]}
                                    
                                    locations[loc_str] = geo_info          # Adds associated location to user input
                                    
                            except:
                                not_found.append([str(user),loc_str])
                                er_404 += 1
                                
                            
                            # Counting successfully of processed users
                            completed += 1
                                
                            
                        # Error handeling
                        elif response.status_code == 404:
                            not_found.append([str(user),loc_str])
                            er_404 += 1
                            geo_info = {}
                        elif response.status_code == 400:
                            not_found.append([str(user),loc_str])
                            er_400 += 1
                            geo_info = {}
                        elif response.status_code >= 500:
                            not_found.append([str(user),loc_str])
                            er_500 += 1
                            logging.warning("Fatal Error 500 - Server sided Error")
                            if er_500 >= 5:
                                logging.warning("Exiting Sys.")
                                logging.info('Last processed User: '+ str(user))
                                sys.exit()
                        else:
                            not_found.append([str(user),loc_str])
                            logging.warning("Unknown Error: " + str(response.status_code))
                            geo_info = {}
                        
                        
                else:
                    geo_info = None
                    empty += 1
                        
                    
                # Adding geo_loc information
                export_geoloc[str(user)] = export[user]
                if loc_str:
                    export_geoloc[user]['twitter_username']['twitter_location'] = geo_info
                        
                
                # Exporting user data as json
                processed += 1
                if processed % 100 == 0:
                    # Saving new gained info every 100 users
                    cache(export_geoloc, export_directory)
                    csv_cache(not_found, export_directory_2)
                    not_found = [] 
                    export_geoloc = {}


            except Exception as e:
                logging.warning(e)
                logging.warning(str(e))
                logging.info("Last processed user: " + str(processed))

            
    cache(export_geoloc, export_directory)
    csv_cache(not_found, export_directory_2)
    not_found = [] 
    export_geoloc = {}


    logging.info(str(completed) + " of " + str(len(export)) + " users succesfully processed")
    logging.info(str(empty) + " location spaces are empty")
    logging.info(str(er_404) + " locations could not be found")
    logging.info(str(er_500 + er_400) + " other errors occured")
    log_endtime = datetime.datetime.now()
    log_runtime = (log_endtime - log_starttime)
    logging.info("Total runtime: " + str(log_runtime))
            
            
except Exception as e:
    logging.warning(e)
    logging.warning(str(e))
        
        
