import requests

def query(user, auth):
    headers = {"Authorization": 'token ' + auth}
    target_user = '"' + user + '"'

    query = """
    {
        user(login:""" + target_user  + """) {
            name
            sponsorshipsAsMaintainer(first: 100, includePrivate: true) {
                totalCount
                nodes {
                    privacyLevel
                    sponsor {
                        login
                    }
                }
            }
            repositories (first:100, ownerAffiliations:OWNER) {
                totalCount
                nodes {
                    name
                    url
                    isPrivate
                }
            }
        }
    }
     """
    
    response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)

    # Capturing bad requests
    if ('errors' in response.json()) == True:
        return "Query Error"
    else:
        return(response.json())
