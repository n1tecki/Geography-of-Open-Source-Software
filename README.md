# Geography of Open Source Software

The goal of the project was to measure open source software contribution activity at a national, regional, and local level using data from GitHub and adjacent platforms. This data is used to better understand how open source interacts with the rest of the economy, for instance as a complement or substitute for proprietary work.


### Python scripts

The data collection scripts are written in Python and calls the APIs of the services Github, Twitter and Bing Maps.

The codes can be used to collect user information from Github and Twitter, including usernames, location information, emails, ... sponsor information. Users can also be gelocoated based on their location information from said services or comparison of their email suffixes against a list of country and university domains. Depending on the available data, the user can be located on a national or subnational level.

The code was implemented in Python 3 and tested on a Linux machine. The required dependencies for the scripts are: tweepy, urllib, github, nuts_finder and pandas.


## Data Collection

Depending on if the github usernames of contributors are already avalable and known, this step can be skipped:
The data collection works as a data flow passing musltiple scripts, with each script enriching the available data. 
In the first step, the usernames of Github contributors are extrected from commit information. The <span style="font-size:larger;">**Williams_Methode.py**</span> script takes a CSV file containing commit SHAs of relevant users and calls it via the Github API. Having called the commit itself, the author of that commit is traced and exported into a CSV file. To check for redundancies in the usernames, the **Redundance_Processing.py** code makes sure each username is unique.


 
![alt text](https://github.com/n1tecki/Geography-of-Open-Source-Software/blob/main/DFD.jpg?raw=true)



