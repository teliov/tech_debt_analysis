#! /usr/bin/env python3

import argparse
import datetime
from dateutil import parser
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

def run_analysis(access_token, repo_name, user, issue_count=2000):
    per_page = 100
    auth_header = "token %s" % (access_token)
    headers = {
        'authorization': auth_header,
        'accept': 'application/vnd.github.v3+json'
    }

    close_time_bins = {}

    url = "https://api.github.com/repos/%s/%s/issues" % (user, repo_name)

    params = {
        'per_page': per_page,
        'state': "closed",
    }

    count = 0

    while True:
        try:
            response = requests.get(url, params=params, headers=headers)
            json_data = response.json()

            for issue in json_data:
                if 'closed_at' not in issue:
                    continue
                if 'created_at' not in issue:
                    continue

                closed_at_str = issue['closed_at']
                created_at_str = issue['created_at']

                if not closed_at_str or not created_at_str:
                    continue

                closed_at = parser.parse(closed_at_str)
                created_at = parser.parse(created_at_str)

                delta = closed_at - created_at

                diff_in_days = delta.days

                if diff_in_days > 31:
                    diff_in_days = 32

                if diff_in_days < 0:
                    diff_in_days = 0

                if diff_in_days in close_time_bins:
                    close_time_bins[diff_in_days] += 1
                else:
                    close_time_bins[diff_in_days] = 1

                count += 1


            links = parseLinkHeader(response.headers)
            if "next" not in links:
                break
            else:
                url = links["next"]
                params = {}


            if count > issue_count:
                break

        except Exception as e:
            print("Got error . Reason: %s Aborting!\n" % (str(e)))
            break

    output_file = open("issue_analysis.json", "w")
    json.dump(close_time_bins, output_file, indent=4)
    output_file.close()

    print("analysis complete!")

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='Run analysis on closed issues in a repo')

    arg_parser.add_argument('--repo', required=True, dest='repo', type=str)
    arg_parser.add_argument('--access_token', required=True, dest='access_token', type=str)
    arg_parser.add_argument('--owner', required=True, dest='owner', type=str)
    arg_parser.add_argument('--issue_count', dest='issue_count',  type=int, default=2000)

    args = arg_parser.parse_args()

    run_analysis(args.access_token, args.repo, args.owner, args.issue_count)
