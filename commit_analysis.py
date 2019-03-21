#! /usr/bin/env python3
import argparse
import datetime
import json
import requests



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


def run_analysis(access_token, repo_name, user, start_year, end_year):
    years = range(start_year, end_year + 1)
    per_page = 100

    auth_header = "token %s" % (access_token)
    headers = {
        'authorization': auth_header,
        'accept': 'application/vnd.github.v3+json'
    }

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

    print("Analysis Complete")

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Run analysis on commits in a repo')

    arg_parser.add_argument('--repo', required=True, dest='repo', type=str)
    arg_parser.add_argument('--access_token', required=True, dest='access_token', type=str)
    arg_parser.add_argument('--owner', required=True, dest='owner', type=str)
    arg_parser.add_argument('--start_year', required=True, dest='start', type=int)
    arg_parser.add_argument('--end_year', required=True, dest='end', type=int)

    args = arg_parser.parse_args()

    run_analysis(args.access_token, args.repo, args.owner, args.start, args.end)
