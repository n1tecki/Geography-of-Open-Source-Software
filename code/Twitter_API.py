# ----------------- IMPORTING -----------------
import tweepy
import json
import os.path
import time
import logging
import datetime
import csv
import sys
sys.path.insert(1, 'Resources')
import caching
# ---------------------------------------------



############## INPUT VARIABLES ################
# Optional input for partial processing
start_at = 0

# Directory Input
api_tokens = '/home/codeuser/code/tokens/twitter_tokens.csv'

# Optional working with batches
batch = True    # If TRUE, batch number has to be specified according to file names
batch_nr = 1

if batch:
    log_dir = 'LOGS/batch%s_LOG_Twitter_API.log' % batch_nr
    import_dir = 'data/raw_data/batch%s_github_export.json' % batch_nr
    export_dir = 'data/raw_data/batch%s_twitter_export.json' % batch_nr
    export_missing_dir = 'data/raw_data/batch%s_twitter_api_not_found.csv' % batch_nr
else:
    log_dir = 'LOGS/LOG_Twitter_API.log'
    import_dir = 'data/raw_data/github_export.json'
    export_dir = 'data/raw_data/twitter_export.json'
    export_missing_dir = 'data/raw_data/twitter_api_not_found.csv'
###############################################



# ------------- GLOBAL VARIABLES --------------
count = 0
start_at = 0

export_twitter = {}
not_found = [] 
processed = 0
completed = 0
er_500 = 0
er_422 = 0
er_404 = 0
er_403 = 0
er_400 = 0
er_twitter = 0

logging.basicConfig(filename=log_dir, filemode='a', 
                    format='%(asctime)s [%(levelname)s] - %(message)s', 
                    datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
# ---------------------------------------------



# ----------- AUTHENTIFIKATION INFO -----------
# Stack with not limited tokens reached
with open(api_tokens, 'r', encoding='utf-8-sig') as tokens:
    reader = csv.reader(tokens, delimiter = ',')
    # Stack with tokens that have not reached limit
    token_ready = list(reader)
    
# Stack with limited tokens 
token_wait = []

# Initial authenticate to Twitter
auth_token = token_ready.pop(0)
auth = tweepy.OAuthHandler(auth_token[0],auth_token[1])
auth.set_access_token(auth_token[2],auth_token[3])
api = tweepy.API(auth, wait_on_rate_limit=False, wait_on_rate_limit_notify=False)
# ---------------------------------------------



# ------------- SWITCHING TOKENS --------------
def switch(auth_token):
    token_wait.append(auth_token)
    if len(token_ready) != 0:
        auth_token = token_ready.pop(0)
        
    else:
        auth_token = token_wait.pop(0)
        auth = tweepy.OAuthHandler(auth_token[0],auth_token[1])
        auth.set_access_token(auth_token[2],auth_token[3])
        api = tweepy.API(auth, wait_on_rate_limit=False, wait_on_rate_limit_notify=False)
        if api.rate_limit_status()['resources']['users']['/users/:id']['remaining'] == 0:
            wait(api)         
        
    logging.info("Switched to token: " + str(auth_token))
    return(auth_token)
# ---------------------------------------------



# ------------------ WAITING ------------------
# Function: Waits until the pull limits are renewed
def wait(api):
    logging.info("waiting for API counter to reset ...")
    
    while api.rate_limit_status()['resources']['users']['/users/:id']['remaining'] == 0:
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


try:


    logging.info('Loading of external file ...')
    logging.info('File successfully loaded ...')
    logging.info('Processing of useres initiated ...')
    log_starttime = datetime.datetime.now()

    
    import_data = json_load(import_dir)
    for user in import_data:
        

        count += 1
        if count >= start_at:

            
            try:


                twitter_username = import_data[user]["twitter_username"]
                if twitter_username:
                    
                    repeat = True
                    found = False
                    fatal = 0
                    while repeat == True:
                        try:
                            user_data = api.get_user(twitter_username)
                            twitter_data = {
                            "twitter_user": user_data.screen_name,
                            "twitter_name": user_data.name,
                            "twitter_location": user_data.location
                            }
                            
                            # Counting successfully of processed users
                            completed += 1
                            
                            repeat = False
                            found = True
                        
                        except tweepy.TweepError as e:
                            #Checks if the error is a rate limit error 
                            try:
                                if e.args[0][0]['code'] in (88,32,326):
                                    logging.warning('Token pull limit reached ...')
                                    auth_token = switch(auth_token)
                                    auth = tweepy.OAuthHandler(auth_token[0],auth_token[1])
                                    auth.set_access_token(auth_token[2],auth_token[3])
                                    api = tweepy.API(auth, wait_on_rate_limit=False, wait_on_rate_limit_notify=False)
                
                                else:
                                    logging.warning('ERROR ' + str(e.args[0][0]['code']))
                                    logging.warning(e.args[0][0]['message'])
                                    er_twitter += 1
                                    logging.info("Last processed user: " + str(user))
                                    not_found.append([user,twitter_username]) 
                                    twitter_data = user
                                    repeat = False
                            except:
                                fatal += 1 
                                if fatal >= 3: 
                                    logging.warning('Fatal ERROR') 
                                    er_twitter += 1 
                                    logging.info("Last processed user: " + str(twitter_username)) 
                                    not_found.append([user,twitter_username]) 
                                    repeat = False 
                                else: 
                                    repeat = True 
                                    
                            found = False 
                            
                    fatal = 0

                
                    # Checking for unsuccessfully checked username
                    if twitter_data == twitter_username:
                        er_twitter += 1
                        
                else:
                    twitter_data = None


                export_twitter[str(user)] = import_data[user]
                export_twitter[user]["twitter_username"] = twitter_data


                # Exporting user data as json
                processed += 1
                if processed % 100 == 0:
                    # Saving new gained info every 100 users
                    caching.cache(export_twitter, export_dir, json)
                    caching.cache(not_found, export_missing_dir, csv)
                    not_found = [] 
                    export_twitter = {}
                

            except Exception as e:
                logging.warning(e)
                logging.warning(str(e))
                logging.info("Last processed user: " + str(processed))
                not_found.append([user,twitter_username]) 


    # Exporting remaining user data
    caching.cache(export_twitter, export_dir, csv)
    caching.cache(not_found, export_missing_dir, json)
    not_found = [] 
    export_twitter = {}

    logging.info(str(completed) + " of " + str(len(import_data)) + " users succesfully processed")
    logging.info(str(er_twitter) + " users could not be found")
    log_endtime = datetime.datetime.now()
    log_runtime = (log_endtime - log_starttime)
    logging.info("Total runtime: " + str(log_runtime))


except Exception as e:
    logging.warning(e)
    logging.warning(str(e))
