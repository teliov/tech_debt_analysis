import datetime
import json
import requests

access_token = "5e6d259d55ace50dc7f3b67c5c85a70cafa8d465"
repo_name = "home-assistant"
user = "home-assistant"

per_page = 100
years = range(2014, 2020)


auth_header = "token %s" % (access_token)
headers = {
    'authorization': auth_header,
    'accept': 'application/vnd.github.v3+json'
}

def parseLinkHeader(headers):
    """
    adapted from:  https://github.com/PyGithub/PyGithub/blob/master/github/PaginatedList.py#L227
    """
    links = {}
    if "link" in headers:
        linkHeaders = headers["link"].split(", ")
        for linkHeader in linkHeaders:
            (url, rel) = linkHeader.split("; ")
            url = url[1:-1]
            rel = rel[5:-1]
            links[rel] = url
    return links

commit_hash = {}


for year in years:
    since = datetime.datetime(year, 1, 1)
    until = datetime.datetime(year, 12, 31, 23, 59, 59)
    since_str = since.isoformat()
    until_str = until.isoformat()
    url = "https://api.github.com/repos/%s/%s/commits" % (user, repo_name)
    params = {
        'since': since_str,
        'until_str': until_str,
        'per_page': per_page
    }
    
    author_count = {}
    while True:
        try:
            response = requests.get(url, params=params, headers=headers)
            json_data = response.json()

            for item in json_data:
                if "author" not in item:
                    continue

                author_obj = item["author"]

                if author_obj is None:
                    continue

                if "login" not in author_obj:
                    continue

                author = author_obj['login']
                if author is None:
                    continue

                if author not in author_count:
                    author_count[author] = 1
                else:
                    author_count[author] += 1


            # check if we can get more links
            links = parseLinkHeader(response.headers)
            if "next" not in links:
                break
            else:
                url = links["next"]
                params = {}
        except Exception as e:
            print("Got error searching between %s and %s. Reason: %s Aborting!\n" % (since_str, until_str, str(e)))
            break

    commit_hash[year] = author_count

output_file = open("commit_analysis.json", "w")
json.dump(commit_hash, output_file, indent=4)
output_file.close()