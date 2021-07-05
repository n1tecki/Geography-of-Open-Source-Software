import pandas as pd
import csv



# Loading all collected infos 
df = pd.read_csv('github_accounts.csv', delimiter = ',')
df = df.drop(labels = 'Unnamed: 0', axis = 1)



# Extracting each location source that uniquely explains location and grouping by
github_loc = df[df['github_country'].notnull()]
github_loc = github_loc[['github_country']].groupby(['github_country']).agg({'github_country': ['count']}).reset_index()
github_loc.columns = github_loc.columns.map('_'.join)
github_loc.columns = ['country','github_count']

twitter_loc = df[(df['github_country'].isnull()) & (df['twitter_country'].notnull())]
twitter_loc = twitter_loc[['twitter_country']].groupby(['twitter_country']).agg({'twitter_country': ['count']}).reset_index()
twitter_loc.columns = twitter_loc.columns.map('_'.join)
twitter_loc.columns = ['country','twitter_count']

email_loc = df[(df['github_country'].isnull()) & (df['twitter_country'].isnull()) & (df['email_country'].notnull())]
email_loc = email_loc[['email_country']].groupby(['email_country']).agg({'email_country': ['count']}).reset_index()
email_loc.columns = email_loc.columns.map('_'.join)
email_loc.columns = ['country','mail_count']

uni_loc = df[(df['github_country'].isnull()) & (df['twitter_country'].isnull()) & (df['email_country'].isnull()) & (df['university_country'].notnull())]
uni_loc = uni_loc[['university_country']].groupby(['university_country']).agg({'university_country': ['count']}).reset_index()
uni_loc.columns = uni_loc.columns.map('_'.join)
uni_loc.columns = ['country','uni_count']



# Merging the datasets
export = github_loc.merge(twitter_loc, how = 'outer')
export = export.merge(email_loc, how = 'outer')
export = export.merge(uni_loc, how = 'outer')



# Some fine work on the df
export = export.fillna(0)
export[['github_count', 'twitter_count', 'mail_count', 'uni_count']] = export[['github_count', 'twitter_count', 'mail_count', 'uni_count']].astype(int)



# Summing up locations of all 
export['total'] = export['github_count'] + export['twitter_count'] + export['mail_count'] + export['uni_count']



# Exporting stats
export = export.sort_values(by=['total'], ascending=False)
export.to_csv('world_stats.csv', sep=',')





