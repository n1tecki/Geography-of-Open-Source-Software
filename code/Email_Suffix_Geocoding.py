import json
import csv
import os



batch_nr = 4
NAN = 0
directory = '/home/codeuser/code/data/processed_data/batch%s_final.json' % batch_nr



with open('/home/codeuser/code/data/raw_data/batch%s_geloc_emailmatch_export.json' % batch_nr, "r") as f:
    data = json.load(f)

with open('/home/codeuser/code/data/external_data/uni_email_suffix.json', "r") as f:
    uni_suffix = json.load(f)

with open('/home/codeuser/code/data/external_data/country_domains.csv', 'r', encoding='utf-8-sig') as csv_file:
    reader = csv.reader(csv_file, delimiter = ',')
    country_suffix = {rows[1]:rows[0] for rows in reader}



for i in data:

    uni_suffix_list = []
    country_code_list = []

    try:
        for j in data[i]['email_address']:
            split = j.split('@')
            suffix = split[1]
            suffix_parts = suffix.split('.')
            country_code = suffix_parts[-1]
            country_code_list.append(country_code)
            uni_suffix_list.append(suffix)
    except:
        pass

    try:
        email = data[i]['email']
        split = email.split('@')
        suffix = split[1]
        suffix_parts = suffix.split('.')
        country_code = suffix_parts[-1]
        country_code_list.append(country_code)
        uni_suffix_list.append(suffix)
    except:
        pass



    data[i]['email_country'] = {}
    data[i]['email_country']['country'] = 'NaN'
    data[i]['email_country']['university'] = 'NaN'
    data[i]['email_country']['university_country'] = 'NaN'



    # Checking for country domains
    for a in country_code_list:
        if a.upper() in country_suffix:
            country = country_suffix[a.upper()]
            data[i]['email_country']['country'] = country



    # Checking for university domains
    for ii in uni_suffix:
        for jj in uni_suffix_list:
            if jj in ii['domains']:
                data[i]['email_country']['university'] = ii['name']
                data[i]['email_country']['university_country'] = ii['country']
            


# Exporting file
if os.path.exists(directory) == True:
    with open(directory, 'r+') as outfile:
        cache = json.load(outfile)
        cache.update(data) # append new data to existing file

# Creating export file if one doesn't exist yet
else:
    with open(directory, 'w') as outfile:
        json.dump(data, outfile)
