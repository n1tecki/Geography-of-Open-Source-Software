# Caching and exporting data
import requests


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
