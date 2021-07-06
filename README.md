# Geography of Open Source Software

The goal of the project was to measure open source software contribution activity at a national, regional, and local level using data from GitHub and adjacent platforms. This data is used to better understand how open source interacts with the rest of the economy, for instance as a complement or substitute for proprietary work.


### Python scripts

The data collection scripts are written in Python and calls the APIs of the services Github, Twitter and Bing Maps.

The codes can be used to collect all user provided information from Github and Twitter, including usernames, location information, emails, twitter username, other associated accounts/websites, workplace sponsor information, etc. Users can also be gelocoated based on their location information from said services or comparison of their email suffixes against a list of country and university domains. Depending on the available data, the user can be located on a national or subnational level.

The code was implemented in Python 3 and tested on a Linux machine. The required dependencies for the scripts are: tweepy, urllib, github, nuts_finder and pandas.


## Data Collection

#### 1.**Username Fetching** <br /> Depending on if the github usernames of contributors are already avalable and known, this step can be skipped: <br /> The data collection works as a data flow passing musltiple scripts, with each script enriching the available data. In the first step, the usernames of Github contributors are extrected from commit information. The **_Williams_Methode.py_** script takes a CSV file containing commit SHAs of relevant users and calls it via the Github API. Having called the commit itself, the author of that commit is traced and exported into a CSV file. Commits that could not be traced to the author or no longer exist are exported into a seperate CSV. To check for redundancies in the usernames, the **_Redundance_Processing.py_** code makes sure each username is unique.
2. **Github Data Collection** <br /> As a consecutive step, the CSV file with unique usernames is passed on to the **_Github_API.py_** script, which calls the Github API and gathers the data of the user. Additionally, the **_graphQL_API_** script is called, which additionally collects sponsor information about each user. The resulting data is exported as a JSON file. Usernames that could not be found or no longer exist are exported into a seperate CSV file. 
3. **Twitter Data Collection** <br /> The **_Twitter_API.py_** then takes the JSON file with all the user information and calls the Twitter API to collect data about _only those users, that had a Twitter username in their Github profile._ 


 
![alt text](https://github.com/n1tecki/Geography-of-Open-Source-Software/blob/main/DFD.jpg?raw=true)



