# ----------------- IMPORTING -----------------
import requests
import csv
import json
import logging
import time
import datetime
import os.path
import sys
import graphQL_API
# ---------------------------------------------



############## INPUT VARIABLES ################
# Optional input for partial processing
start_at = 0

# Directory Input
api_tokens = 'code/tokens/github_tokens.csv'

# Optional working with batches
batch = TRUE    # If TRUE, batch number has to be specified according to file names
batch_nr = 1

if batch:
    log_dir = 'LOG/batch%s_LOG_Github_API.log' % batch_nr
    import_data = 'data/processed_data/batch%s_usernames.csv' % batch_nr
    export = 'data/raw_data/batch%s_github_export.json' % batch_nr
    export_missing = 'data/raw_data/batch%s_github_api_not_found.csv' % batch_nr
else:
    log_dir = 'LOG/LOG_Github_API.log'
    import_data = 'data/processed_data/usernames.csv'
    export = 'data/raw_data/github_export.json'
    export_missing = 'data/raw_data/github_api_not_found.csv'
###############################################



# ------------- GLOBAL VARIABLES --------------
url = 'https://api.github.com/users/'

# Progress counting
count = 0
processed = 0
completed = 0

# Error Capturing
er_500 = 0
er_422 = 0
er_404 = 0
er_403 = 0
er_400 = 0
er_query = 0
fatal_er = 0

usernames = []
users_not_found = []
data_extracted = {}
sponsor_list = []

logging.basicConfig(filename=log_dir, filemode='a', 
                    format='%(asctime)s [%(levelname)s] - %(message)s', 
                    datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
# ---------------------------------------------



# ----------- AUTHENTIFIKATION INFO -----------
# Reading externaly saved API tokens
with open(api_tokens, 'r', encoding='utf-8-sig') as tokens:
    reader = csv.reader(tokens, delimiter = ',')
    # Stack with tokens that have not reached limit
    token_ready = list(reader)

# Stack with limited tokens 
token_wait = []

auth = tuple(token_ready.pop(0))
# ---------------------------------------------



# ------------------ WAITING ------------------
# Function: Waits until the pull limits are renewed
def wait(auth, object1, url):
    logging.info("waiting for API counter to reset ...")
    
    while int(requests.get(url + object1, auth=auth).headers["X-RateLimit-Remaining"]) == 0:
        time.sleep(300)
    
    logging.info("API rate limit reset!")
    logging.info("Continuing pull requests ...")
# ---------------------------------------------



# ----------- CACHING AND EXPORTING -----------
def cache(cache_data, directory, type):

    if type == 'json':
        # Updating exported file with newly cached data
        if os.path.exists(directory) == True:
            with open(directory, 'r+') as outfile:
                cache = json.load(outfile)
                cache.update(cache_data) # append new data to existing file
                outfile.seek(0) 
                json.dump(cache, outfile)
            logging.info("%s file updated ..." % directory)
            
        # Creating export file if one doesn't exist yet
        else:
            with open(directory, 'w') as outfile:
                json.dump(cache_data, outfile)
            logging.info("retrieved data exported to %s..." % directory)

    if type == 'csv':
        # Updating exported file with newly cached data
        if os.path.exists(directory) == True:
            with open(directory, 'a') as outfile:
                for i in cache_data:
                    outfile.write(i + '\n')
            logging.info("%s file updated ..." % directory)
            
        # Creating export file if one doesn't exist yet
        else:
            with open(directory, 'w') as outfile:
                for i in cache_data:
                    outfile.write(i + '\n')
            logging.info("retrieved data exported to %s..." % directory)
# ---------------------------------------------



# ------------- SWITCHING TOKENS --------------
def switch(auth, object1, url):
    token_wait.append(auth)
    if len(token_ready) != 0:
        auth = tuple(token_ready.pop(0))
    else:
        auth = token_wait.pop(0)
        req_info = requests.get(url + object1, auth=auth)
        if int(req_info.headers["X-RateLimit-Remaining"]) == 0:
            wait(auth, object1, url)      
        
    logging.info("Switched to token: " + str(auth[0]))
    return(auth)
# ---------------------------------------------



# ------------ LOADING USER NAMES -------------
# Reading usernames into a list
with open(import_data, 'r', encoding='utf-8-sig') as csv_file:
    logging.info('Loading of external file ...')
    reader = csv.reader(csv_file, delimiter = ',')
    usernames = list(reader)
    logging.info('File successfully loaded ...')
# ---------------------------------------------


try:

    
    # Iterate through the csv list to check every username
    logging.info('Processing of useres initiated ...')
    log_starttime = datetime.datetime.now()
    for user in usernames:


        count += 1
        if count >= start_at:


            try:


                # Requesting info
                req_info = requests.get(url + user[0], auth=auth)

                # Pull limit is checked and pulling paused until limit is renewed
                if int(req_info.headers["X-RateLimit-Remaining"]) == 0:
                    logging.warning("Pull rate limit for " + str(auth[0]) + " reached")
                    auth = switch(auth, user[0], url)
                    req_info = requests.get(url + user[0], auth=auth)


                # User info
                user_data = req_info.json()
                # API token and pull info
                token_info = req_info.headers

                # Error capture -----------------------------------------------------------
                if req_info.status_code != 200:

                    # Checking https status codes for errors 
                    if req_info.status_code == 404:
                        logging.warning(str(user) + " not found... skipping")
                        users_not_found.append(str(user[0]))
                        er_404 += 1
                        pass
                    elif req_info.status_code == 403:
                        logging.warning("403 Forbidden")
                        logging.info(req_info.headers)
                        logging.info(req_info.text)
                        logging.info("Last processed user: " + str(user))
                        users_not_found.append(str(user[0]))
                        er_403 += 1
                    elif req_info.status_code == 400:
                        logging.warning("400 Bad Request")
                        logging.info(req_info.headers)
                        logging.info(req_info.text)
                        logging.info("Last processed user: " + str(user))
                        users_not_found.append(str(user[0]))
                        er_400 += 1
                    elif req_info.status_code == 422:
                        logging.warning("422 Unprocessable Entity")
                        logging.info(req_info.headers)
                        logging.info(req_info.text)
                        logging.info("Last processed user: " + str(user))
                        users_not_found.append(str(user[0]))
                        er_422 += 1
                    elif req_info.status_code >= 500:
                        logging.warning("Fatal Error 500 - Server sided Error")
                        fatal_er += 1
                        er_500 += 1
                        users_not_found.append(str(user[0]))
                        logging.warning("Error code " + str(req_info.status_code))
                        logging.info(req_info.headers)
                        logging.info(req_info.text)
                        if fatal_er > 5:
                            logging.warning("Exit Sys ...")
                            logging.info("Last processed user: " + str(user))
                            sys.exit()
                    pass 
                # -------------------------------------------------------------------------

                else:
                # Scraping infos about user -----------------------------------------------
                    completed += 1
                    data_extracted[str(user[0])] = user_data
                    
                    #Map email to user
                    #data_extracted[str(user[0])]['email_address'] = []
                    #data_extracted[str(user[0])]['email_address'].append(user[1])
                    
                    data_extracted[str(user[0])]['crawled_at'] = str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
                    
                    # Querying data from graphQL API
                    query_data = graphQL_API.query(user[0],auth[1])
                    if query_data != "Query Error":
                        data_extracted[str(user[0])]['sponsor_count'] = int(query_data['data']['user']['sponsorshipsAsMaintainer']['totalCount'])
                        
                        for i in query_data['data']['user']['sponsorshipsAsMaintainer']['nodes']:
                            if i['privacyLevel'] == "PUBLIC":
                                
                                # Due to an error on gql some public sponsors are missing login names, hence the try command 
                                try:
                                    sponsor_list.append(str(i['sponsor']['login']))
                                except:
                                    sponsor_list = []
                                    
                        data_extracted[str(user[0])]['sponsors'] = sponsor_list
                        sponsor_list = []
                    else:
                        data_extracted[str(user[0])]['sponsor_count'] = "NaN"
                        data_extracted[str(user[0])]['sponsors'] = "NaN"
                        er_query += 1
                            
                # -------------------------------------------------------------------------


                # Exporting user data as json
                processed += 1
                if processed % 100 == 0:
                    #print(data_extracted)
                    logging.info('... ' + str(processed+start_at) + '/' + str(len(usernames)) + ' users processed ...' '(' + str(count) + ')')
                    # Saving new gained info every 100 users
                    cache(data_extracted, export, 'json')
                    cache(users_not_found, export_missing, 'csv')
                    data_extracted = {}
                    users_not_found = []

                    fatal_er = 0


            except Exception as e:
                logging.warning(e)
                logging.warning(str(e))
                logging.info("Last processed user: " + str(processed))
                users_not_found.append(str(user[0]))


    logging.info('... ' + str(processed+start_at) + '/' + str(len(usernames)) + ' users processed ...'  + '(' + str(count) + ')')
    # Exporting remaining user data
    cache(data_extracted, '/home/codeuser/code/data/raw_data/batch%s_github_export.json' % batch_nr, 'json')
    cache(users_not_found, '/home/codeuser/code/data/raw_data/batch%s_github_api_not_found.csv' % batch_nr, 'csv')
    data_extracted = {}
    users_not_found = []

    logging.info(str(completed) + " of " + str(len(usernames)) + " users succesfully processed")
    logging.info(str(er_404) + " users could not be found")
    logging.info(str(er_query) + " graphQL query errors occured")
    logging.info(str(er_500 + er_422 + er_403 + er_400) + " other errors occured")
    log_endtime = datetime.datetime.now()
    log_runtime = (log_endtime - log_starttime)
    logging.info("Total runtime: " + str(log_runtime))


except Exception as e:
    logging.warning(e)
    logging.warning(str(e))
