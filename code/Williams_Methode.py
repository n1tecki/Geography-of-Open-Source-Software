# ----------------- IMPORTING -----------------
import github
import pandas as pd
import logging
import time
import datetime
import os.path
import json
import csv
import sys
sys.path.append('Resources')
import caching
# ---------------------------------------------



############## INPUT VARIABLES ################
# Optional input for partial processing
start_at = 0

# Directory Input
api_tokens = 'tokens/github_tokens.csv'

# Optional working with batches
batch = TRUE    # If TRUE, batch number has to be specified according to file names
batch_nr = 1

if batch:
    log_dir = 'LOGS/batch%s_LOG_Williams_Methode.log' % batch_nr
    import_dir = 'data/raw_data/batch%s_hashed_emails_.json' % batch_nr
    export_dir = 'data/raw_data/batch%s_redundant_usernames.csv' % batch_nr
    export_dir_missing = 'data/raw_data/batch%s_williams_methode_not_found.csv' % batch_nr
else:
    log_dir = 'LOGS/LOG_Williams_Methode.log'
    import_dir = 'data/raw_data/hashed_emails.json'
    export_dir = 'data/raw_data/redundant_usernames.csv'
    export_dir_missing = 'data/raw_data/williams_methode_not_found.csv'
###############################################



# ----------- AUTHENTIFIKATION INFO -----------
# Reading externaly saved API tokens
with open(api_tokens, 'r', encoding='utf-8-sig') as tokens:
    reader = csv.reader(tokens, delimiter = ',')
    # Stack with tokens that have not reached limit
    token_ready = list(reader)
    
# Stack with limited tokens 
token_wait = []

auth = token_ready.pop(0)[1]
g = github.Github(auth)
# ---------------------------------------------



# ------------- GLOBAL VARIABLES --------------
count = 0

processed = 0
completed = 0

er_404_repo = 0
er_other_repo = 0
er_404_user = 0
er_other_user = 0
fatal_er = 0

user_names = []
users_not_found = []

api_calls = 0
# ---------------------------------------------



# ---------------- LOGGING --------------------
logging.basicConfig(filename=log_dir, filemode='a', 
                    format='%(asctime)s [%(levelname)s] - %(message)s', 
                    datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)
# ---------------------------------------------



# ---------- CHECHING TOKEN LIMITS ------------
def check_limit(g,auth):
    if g.get_rate_limit().core.remaining == 0:
        logging.warning('Token pull limit reached ...')
        auth = switch(auth)
        
    return auth 
# ---------------------------------------------      



# ------------------ WAITING ------------------
# Function: Waits until the pull limits are renewed
def check_wait(g):
    logging.info("waiting for API counter reset ... ")
    
    # Checks every minute if limit is renewed
    while g.get_rate_limit().core.remaining == 0:
        time.sleep(300)
        
    logging.info("API rate limit reset!")
    logging.info("Continuing pull requests ...")
# ---------------------------------------------



# ------------- SWITCHING TOKENS --------------
def switch(auth):
    token_wait.append(auth)
    if len(token_ready) != 0:
        auth = token_ready.pop(0)[1]
    else:
        auth = token_wait.pop(0)
        g = github.Github(auth)
        if g.get_rate_limit().core.remaining == 0:
            check_wait(g)
        
    logging.info("Switched to token: " + str(auth))
    return(auth)
# ---------------------------------------------



# --------------- LOADING FILE ----------------
def json_load(file):
    if os.path.exists(file) == True:
        with open(file, 'r+') as outfile:
            return(json.load(outfile))
# ---------------------------------------------


try:


    data = json_load(import_dir)
    logging.info('Processing of useres initiated ...')
    log_starttime = datetime.datetime.now()


    for i in data:

        i = i[1]
        count += 1
        if count >= start_at:

            try:
                    

                auth = check_limit(g,auth)
                g = github.Github(auth)
                api_calls += 1
                
                try:
                    repo = g.get_repo(data[i][1])
                    
                    auth = check_limit(g,auth)
                    g = github.Github(auth)
                    api_calls += 1
                    
                    try:
                        user = repo.get_commit(data[i][0]).author
                        
                        # Stores user names in a list
                        if user:
                            user_names.append(user.login)
                            completed += 1
                            
                                
                        else:
                            users_not_found.append(i)
                            er_404_user += 1
                        
                        
                    except github.GithubException as e:
                        if int(e.status )<= 500:
                            users_not_found.append(i)
                            er_404_user += 1
                        else:
                            er_other_user += 1
                            logging.warning("Error code " + str(e.status) + ': ' + str(e.data))
                            if fatal_er > 5:
                                logging.warning("Exit Sys ...")
                                logging.info("Last processed user: " + i)
                                sys.exit()
                            time.sleep(60)
                
                except github.GithubException as e:
                    if int(e.status) <= 500:
                        users_not_found.append(i)
                        er_404_repo += 1
                    else:
                        er_other_repo += 1
                        logging.warning("FATAL ERROR!")
                        logging.warning("Error code " + str(e.status) + ': ' + str(e.data))
                        users_not_found.append(i)
                        fatal_er += 1
                        if fatal_er > 5:
                            logging.warning("Exit Sys ...")
                            logging.info("Last processed user: " + i)
                            sys.exit()
                        time.sleep(60)


            except Exception as e:
                logging.warning(e)
                logging.warning(str(e))
                logging.info("Last processed user: " + i)
                users_not_found.append(i)

            
            processed += 1
            if processed % 100 == 0:
                logging.info('... ' + str(processed) + '/' + str(len(data)-start_at) + ' users processed ...' + '(' + str(count) + ')')
                logging.info(str(er_404_repo) + ', ' + str(er_other_repo) + ', ' + str(er_404_user) + ', ' 
                            + str(er_other_user) + ', ' + str(len(users_not_found)))   # Further information
                caching.cache(user_names, export_dir, csv)
                caching.cache(users_not_found, export_dir_missing, csv)
                user_names = []
                users_not_found = []

                fatal_er = 0


    logging.info('... ' + str(processed) + '/' + str(len(data)) + ' users processed ...')
    logging.info(str(er_404_repo) + ', ' + str(er_other_repo) + ', ' + str(er_404_user) + ', ' 
                + str(er_other_user) + ', ' + str(len(users_not_found)))   # Further information
    # Exporting remaining user data
    caching.cache(user_names, export_dir, csv)
    caching.cache(users_not_found, export_dir_missing, csv)
    user_names = []
    users_not_found = []
            

    logging.info(str(completed) + " of " + str(len(data)) + " users succesfully processed")
    logging.info(str(er_404_repo) + " repos could not be found")
    logging.info(str(er_404_user) + " users could not be found")
    logging.info(str(er_other_user + er_other_repo) + " other errors occured")

    log_endtime = datetime.datetime.now()
    log_runtime = (log_endtime - log_starttime)
    logging.info("Total runtime: " + str(log_runtime))

    
except Exception as e:
    logging.warning(e)
    logging.warning(str(e))
