import logging

batch_nr = 0

logging.basicConfig(filename='/home/codeuser/code/LOGS/batch%s_LOG_Redundance_Processing.log' % batch_nr, 
                    filemode='a', format='%(asctime)s [%(levelname)s] - %(message)s', 
                    datefmt='%d-%m-%y %H:%M:%S', level=logging.INFO)

try:


    # Reading in list of users with redundant entries
    with open('/home/codeuser/code/data/raw_data/batch%s_redundant_usernames.csv' % batch_nr, 'r') as infile:
        # Getting unique usernames
        pure = list(dict.fromkeys(infile))
    
        
    # Exporting unique usernames
    with open('/home/codeuser/code/data/processed_data/batch%s_usernames.csv' % batch_nr, 'w') as outfile:
        for i in pure:
            outfile.write(i)


except Exception as e:
    logging.warning(e)
    logging.warning(str(e))
