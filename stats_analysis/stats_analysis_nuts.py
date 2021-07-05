import pandas as pd
import csv



# PROVIDE LEVEL OF NUTS (NUTS1, NUTS2 or NUTS3)
nuts_lvl = 2



# Loading all collected infos 
df = pd.read_csv('/home/codeuser/Data_Analysis/github_accounts.csv', delimiter = ',')
df = df.drop(labels = 'Unnamed: 0', axis = 1)



if nuts_lvl == 3:
    df['current_nuts'] = df['github_nuts3']
elif nuts_lvl == 2:
    df['current_nuts'] = df['github_nuts3'].str[:4]
elif nuts_lvl == 1:
    df['current_nuts'] = df['github_nuts3'].str[:3]
elif nuts_lvl == 0:
    df['current_nuts'] = df['github_nuts3'].str[:2]



# Extracting each location source that uniquely explains location and grouping by
github_loc = df[(df['github_state'].notnull()) & (df['current_nuts'].notnull())]
github_loc = github_loc[['current_nuts']].groupby(['current_nuts']).agg({'current_nuts': ['count']}).reset_index()
github_loc.columns = github_loc.columns.map('_'.join)
github_loc.columns = ['nuts3','github_count']

twitter_loc = df[(df['twitter_state'].notnull()) & (df['current_nuts'].notnull())]
twitter_loc = twitter_loc[['current_nuts']].groupby(['current_nuts']).agg({'current_nuts': ['count']}).reset_index()
twitter_loc.columns = twitter_loc.columns.map('_'.join)
twitter_loc.columns = ['nuts3','twitter_count']



# Merging the datasets
export = github_loc.merge(twitter_loc, how = 'outer')



# Some fine work on the df
export = export.fillna(0)
export[['github_count', 'twitter_count']] = export[['github_count', 'twitter_count']].astype(int)



# Summing up locations of all 
export['total'] = export['github_count'] + export['twitter_count']



# Exporting stats
export = export.sort_values(by=['total'], ascending=False)
export.to_csv('/home/codeuser/Data_Analysis/nuts%s_stats.csv' % nuts_lvl, sep=',')
