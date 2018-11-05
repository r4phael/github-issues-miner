# import errno
import requests
# import os
# import json
import logging
import re
import tqdm
# import datetime
# import sys
from pymongo import MongoClient
# from bson.objectid import ObjectId
from github import Github

# Logging basic date/time config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')


class V4Miner:
    def __init__(self, username, token, cdc):

        self.username = username
        self.token = token
        self.closed_issues = {}
        self.closed_issues_numbers = []
        self.closed_prs = {}
        self.closed_prs_numbers = []
        self.graphql_url = 'https://api.github.com/graphql'
        self.base_url = 'https://api.github.com/repos/'
        self.cdc = cdc

        # Step 1: Connect to MongoDB - Note: Change connection string as needed
        self.client = MongoClient(port=27017)
        self.db = self.client.v4

    def collect_issues_v4(self):

        # Create the output logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        logger.info('Collecting GitHub Issues Number...')
        self.collect_number_issues()

        logger.info('Mining GitHub Issues...')
        # Get the issues data
        # response = requests.post(url, json=self.query, auth=(self.username, self.token))
        headers = {'Authorization': 'bearer %s' % self.token}
        for issue in self.closed_issues_numbers:

            query = {
                'query': '{  repository(owner: "elastic", name: "elasticsearch-hadoop") {    issueOrPullRequest(number:' + str(
                    issue) + ') {      __typename      ... on Closable {       '
                             ''
                             ''
                             ' closed        closedAt      }      ... on Issue {        id        number        url        title        body        bodyText        closed        createdAt        closedAt        updatedAt        authorAssociation        author {          login          url          resourcePath        }        labels(last: 5) {          totalCount          edges {            node {              id              color              createdAt            }          }        }        comments(last: 100) {          totalCount          edges {            node {              id              body              bodyText              createdAt              updatedAt              author {                login                url                resourcePath              }            }          }        }        timeline(last: 10) {          edges {            node {              __typename              ... on ClosedEvent {                actor {                  login                  url                  resourcePath                }              }            }          }        }      }      ... on PullRequest {        id        number        url        title        state        body        merged        closed        createdAt        closedAt        updatedAt        mergedAt        author {          login          url          resourcePath        }        labels(last: 5) {          totalCount          edges {            node {              id              color              createdAt              name              description            }          }        }        mergedBy {          avatarUrl          login          resourcePath          url        }        comments(last: 100) {          totalCount          edges {            node {              id              body              bodyText              createdAt              updatedAt              author {                login                url                resourcePath              }            }          }        }        reviews(last: 100) {          totalCount          edges {            node {              id              body              bodyText              authorAssociation              createdAt              updatedAt              author {                login                url                resourcePath              }            }          }        }        timeline(last: 10) {          edges {            node {              __typename              ... on MergedEvent {                actor {                  login                  url                  resourcePath                }              }              ... on ClosedEvent {                actor {                  login                  url                  resourcePath                }              }            }          }        }      }    }  }}'}
            print(headers)
            response = requests.post(self.graphql_url, json=query, headers=headers)

            # Successful request
            if response.status_code == 200:
                # Successful request
                # Save the closed issues numbers
                self.closed_issues = response.json()
                # Start mining issues

                # Logs
                logging.info('Writing the closed Issues to the output directory...\n')
                result = self.db.issues.insert_one(self.closed_issues['data'])
                logging.info('Saving Issues in MongoDB Database ... ' + str(result))

            else:
                logging.warning(str(response.status_code))

    def collect_number_issues(self):

        # Get the issues data
        # url = self.base_url + 'elastic/elasticsearch-hadoop' + '/issues?state=closed&since=>' + str(self.cdc)
        url = self.base_url + 'elastic/elasticsearch-hadoop' + '/issues?state=closed'

        response = requests.get(url=url, auth=(self.username, self.token))

        # Successful request
        if response.status_code == 200:

            if 'last' in response.links:
                # Get the total number of pages
                total_pages = int(re.findall(r'\d+', response.links['last']['url'])[-1])
            else:
                total_pages = 1

            # Get issues
            for i in tqdm.tqdm(range(1, total_pages + 1)):
                response = requests.get(url + '&page=' + str(i), auth=(self.username, self.token))

                # Successful request
                if response.status_code == 200:

                    # Save the closed issues numbers
                    for closed_issue in response.json():
                        self.closed_issues[str(closed_issue['number'])] = closed_issue
                        self.closed_issues_numbers.append(closed_issue['number'])

                        # Save only issues that are not pull-requests
                        # if 'pull_request' not in closed_issue:?

                else:
                    logging.warning(str(response.status_code))
                break

            logging.info('Total of GitHub Prs... ' + str(len(self.closed_issues_numbers)))

        else:
            logging.warning(str(response.status_code))

    def collect_prs_v4(self):

        # Create the output logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        logger.info('Collecting GitHub Prs Number...')
        self.collect_number_prs()

        logger.info('Mining GitHub Prs...')
        # Get the issues data
        # response = requests.post(url, json=self.query, auth=(self.username, self.token))
        headers = {'Authorization': 'bearer %s' % self.token}
        for pr in self.closed_prs_numbers:

            query = {
                'query': '{  repository(owner: "elastic", name: "elasticsearch-hadoop") {    issueOrPullRequest(number:' + str(
                    pr) + ') {      __typename      ... on Closable {        closed        closedAt      }      ... on Issue {        id        number        url        title        body        bodyText        closed        createdAt        closedAt        updatedAt        authorAssociation        author {          login          url          resourcePath        }        labels(last: 5) {          totalCount          edges {            node {              id              color              createdAt            }          }        }        comments(last: 100) {          totalCount          edges {            node {              id              body              bodyText              createdAt              updatedAt              author {                login                url                resourcePath              }            }          }        }        timeline(last: 10) {          edges {            node {              __typename              ... on ClosedEvent {                actor {                  login                  url                  resourcePath                }              }            }          }        }      }      ... on PullRequest {        id        number        url        title        state        body        merged        closed        createdAt        closedAt        updatedAt        mergedAt        author {          login          url          resourcePath        }        labels(last: 5) {          totalCount          edges {            node {              id              color              createdAt              name              description            }          }        }        mergedBy {          avatarUrl          login          resourcePath          url        }        comments(last: 100) {          totalCount          edges {            node {              id              body              bodyText              createdAt              updatedAt              author {                login                url                resourcePath              }            }          }        }        reviews(last: 100) {          totalCount          edges {            node {              id              body              bodyText              authorAssociation              createdAt              updatedAt              author {                login                url                resourcePath              }            }          }        }        timeline(last: 10) {          edges {            node {              __typename              ... on MergedEvent {                actor {                  login                  url                  resourcePath                }              }              ... on ClosedEvent {                actor {                  login                  url                  resourcePath                }              }            }          }        }      }    }  }}'}
            response = requests.post(self.graphql_url, json=query, headers=headers)

            # Successful request
            if response.status_code == 200:
                # Successful request
                # Save the closed issues numbers
                self.closed_prs = response.json()
                # Start mining issues

                # Logs
                logging.info('Writing the Closed Prs to the output directory...\n')
                result = self.db.pull_requests.insert_one(self.closed_prs['data'])
                logging.info('Saving Prs in MongoDB Database ... ' + str(result))

            else:
                logging.warning(str(response.status_code))

    def collect_number_prs(self):

        # Get the issues data

        url = self.base_url + 'elastic/elasticsearch-hadoop' + '/pulls?state=closed'

        response = requests.get(url=url, auth=(self.username, self.token))

        # Successful request
        if response.status_code == 200:

            if 'last' in response.links:
                # Get the total number of pages
                total_pages = int(re.findall(r'\d+', response.links['last']['url'])[-1])
            else:
                total_pages = 1

            # Get prs
            for i in tqdm.tqdm(range(1, total_pages + 1)):
                response = requests.get(url + '&page=' + str(i), auth=(self.username, self.token))

                # Successful request
                if response.status_code == 200:

                    # Save the closed issues numbers
                    for closed_pr in response.json():
                        self.closed_prs[str(closed_pr['number'])] = closed_pr
                        self.closed_prs_numbers.append(closed_pr['number'])

                else:
                    logging.warning(str(response.status_code))
                break

            logging.info('Total of GitHub Prs... ' + str(len(self.closed_prs_numbers)))

        else:
            logging.warning(str(response.status_code))

    def get_issues_prs(self):
        # or using an access token
        g = Github(self.token)
        repo = g.get_repo("elastic/elasticsearch-hadoop")

        print(g.rate_limiting)
        print(g.rate_limiting_resettime)

        pulls = repo.get_pulls(state='closed', base='master')
        print(pulls)
