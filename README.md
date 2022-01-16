# Geography of Open Source Software

The goal of this project was to measure open source software contribution activity at a national, regional, and local level using data from GitHub and adjacent platforms. This data is used to better understand how open source interacts with the rest of the economy, for instance as a complement or substitute for proprietary work.

For output data see: https://github.com/johanneswachs/OSS_Geography_Data.

For an analysis of this data, see:
> J. Wachs, M. Nitecki, W. Schueller, A. Polleres. "The Geography of Open Source Software: Evidence from GitHub." Technological Forecasting and Social Change. (2022)
https://www.sciencedirect.com/science/article/pii/S0040162522000105

We thank the City of Vienna for funding support.


### Python scripts

The data collection scripts are written in Python. <br />
The APIs of the services Github, Twitter, and Bing Maps are used. <br />
The codes were implemented in Python 3 and tested on a Linux machine. The required dependencies for the scripts are: tweepy, urllib, github, nuts_finder and pandas. <br />

The codes can be used to collect all user-provided information from Github and Twitter, including usernames, location information, emails, Twitter usernames, other associated accounts/websites, workplaces, bios, sponsor information, etc. Users can also be gelocated based on their location information from said services or by analysis of their email suffixes against a list of country and university domains. Depending on the available data, the user can be located on a national or subnational level.


## Data Collection

1. **Username Fetching** <br /> Depending on if the Github usernames of contributors are already available and known, this step can be skipped: <br /> The data collection works as a data flow passing multiple scripts, with each script enriching the available data. In the first step, the usernames of Github contributors are extracted from the provided commit information. The [`Williams_Method.py`](https://github.com/n1tecki/Geography-of-Open-Source-Software/blob/main/code/Williams_Method.py) script takes a CSV file containing commit SHAs of relevant users and calls it via the Github API. The author of that commit is then traced and his username exported into a CSV file. Commits that could not be traced to the author or no longer exist are exported into a separate CSV. To check for redundancies, the [`Redundance_Processing.py`](https://github.com/n1tecki/Geography-of-Open-Source-Software/blob/main/code/Redundance_Processing.py) code makes sure each username is unique. <br /><br />
2. **Github Data Collection** <br /> The CSV file with unique usernames is passed on to the [`Github_API.py`](https://github.com/n1tecki/Geography-of-Open-Source-Software/blob/main/code/Github_API.py) script, which calls the Github API and gathers the data of the user. Additionally, the [`graphQL_API`](https://github.com/n1tecki/Geography-of-Open-Source-Software/blob/main/code/Resources/graphQL_API.py) script is called, which additionally collects sponsor information about each user via the Github GraphQL API. The resulting data is exported as a JSON file. Usernames that could not be found or no longer exist are exported into a separate CSV file. <br /><br />
3. **Twitter Data Collection** <br /> The [`Twitter_API.py`](https://github.com/n1tecki/Geography-of-Open-Source-Software/blob/main/code/Twitter_API.py) takes the JSON file with all the user information and calls the Twitter API to collect data about _only those users, that had a Twitter username in their Github profile._ The new data with Github as well as Twitter information is exported as a JSON file. <br /> Many location strings provided by contributors are too ambiguous. Those strings are saved in a seperate CSV file. <br /><br />
4. **Geocoding** <br /> In this step,  the [`Github_Geocoding.py`](https://github.com/n1tecki/Geography-of-Open-Source-Software/blob/main/code/Github_Geocoding.py) and [`Twitter_Geocoding.py`](https://github.com/n1tecki/Geography-of-Open-Source-Software/blob/main/code/Twitter_Geocoding.py) scripts forward the corresponding gathered location string provided by users to the Bing Maps API in order to geolocate them. The Bing Maps API query results in three most likely location matches, each containing information about the match probability. Each match contains the country, state and city information as a string, as well as the latitude and longitude coordinates. <br /><br />
5. **NUTS Geocoding** The JSON file with the geocoded contributors is then read by the [`NUTS_Geocoding.py`](https://github.com/n1tecki/Geography-of-Open-Source-Software/blob/main/code/Nuts_Geocoding.py) code. This code sets the appropriate NUTS codes based on the latitude and longitude coordinates for users located in Europe and exports the enriched data as a JSON file. <br /><br />
6. **Email Suffix Geocoding** <br /> To geocode as many contributors as possible, besides looking at the user-supplied location string, the infrastructure is also programmed to try and get country level location information based on email suffixes of users. [`Email_Suffix_Geocoding.py`](https://github.com/n1tecki/Geography-of-Open-Source-Software/blob/main/code/Email_Suffix_Geocoding.py) is the script, that compares the email suffixes against a list of many university suffixes and a list of country domains to provide additional location information, exporting it as a JSON file. <br /><br />

The Data Flow Diagram below summarises the geocoding infrastructure:
 
![alt text](https://github.com/n1tecki/Geography-of-Open-Source-Software/blob/main/DFD.jpg?raw=true)



