import errno
import requests
import os
import json
import logging
import re
import tqdm
import datetime
import sys
from pymongo import MongoClient
from bson.objectid import ObjectId

# Logging basic date/time config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')


class IssueMiner:
    def __init__(self, url, issues_output_path, events_output_path, username, token, cdc):

        self.url = url
        self.issues_output_path = issues_output_path
        self.events_output_path = events_output_path
        self.username = username
        self.token = token

        self.closed_issues = {}
        self.closed_issues_numbers = []
        self.issues_events = {}
        self.issues_comments = {}
        self.base_url = 'https://api.github.com/repos/'
        # Step 1: Connect to MongoDB - Note: Change connection string as needed
        self.client = MongoClient(port=27017)
        self.db = self.client.reviews
        self.output = {}
        # Change Data Capture '2018-10-01'
        self.cdc = cdc

    def collect_issues_comments(self, url, number, first_page):

        # Get the comments data
        response = requests.get(url, auth=(self.username, self.token),
                                headers={'Accept': 'application/vnd.github.mockingbird-preview'})

        # Successful request
        if response.status_code == 200:

            if first_page:
                self.issues_comments[str(number)] = response.json()
            else:
                self.issues_comments[str(number)] = self.issues_comments.get(str(number)) + response.json()

            # Go to the next page
            if 'next' in response.links:
                self.collect_issues_comments(response.links['next']['url'], number, False)
        else:
            logging.warning(response.status_code)

    def mine_issues_comments(self):

        # Get the closed issues events
        logging.info('Mining closed Issues comments...')
        for issue in tqdm.tqdm(self.closed_issues_numbers):
            self.collect_issues_comments(url=self.base_url + self.url + '/issues/' + str(issue) + '/comments',
                                       number=issue, first_page=True)
        # Logs
        logging.info('GitHub Issues Comments successfully mined...')

        result = self.db.issues_comments.insert_one(self.issues_comments)
        logging.info('Saving Issues Comments in MongoDB Database ... ' + str(result))


    def collect_issues_events(self, url, number, first_page):

        # Get the events data
        response = requests.get(url, auth=(self.username, self.token),
                                headers={'Accept': 'application/vnd.github.mockingbird-preview'})

        # Successful request
        if response.status_code == 200:

            if first_page:
                self.issues_events[str(number)] = response.json()
            else:
                self.issues_events[str(number)] = self.issues_events.get(str(number)) + response.json()

            # Go to the next page
            if 'next' in response.links:
                self.collect_issues_events(response.links['next']['url'], number, False)
        else:
            logging.warning(response.status_code)

    def mine_issues_events(self):

        # Get the closed issues events
        logging.info('Mining closed Issues events...')
        for issue in tqdm.tqdm(self.closed_issues_numbers):
            self.collect_issues_events(url=self.base_url + self.url + '/issues/' + str(issue) + '/timeline',
                                       number=issue, first_page=True)

        # Logs
        logging.info('GitHub Issues events successfully mined...')

        # Create the output dir if not existent
        try:
            os.makedirs(self.events_output_path)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

        # Change the working directory to the output one
        os.chdir(self.events_output_path)

        # Logs
        # logging.info('Writing the Issues events to the output directory...\n')

        result = self.db.issues_events.insert_one(self.issues_events)
        logging.info('Saving Issues Events in MongoDB Database ... ' + str(result))

        # Write issues events
        #for key, value in self.issues_events.items():
            # Write the issue events to a JSON file
        #    with open(key + '.json', 'w') as output_file:
        #        json.dump(value, output_file)

    def collect_issues(self, url):

        # Get the issues data
        response = requests.get(url, auth=(self.username, self.token))

        # Successful request
        if response.status_code == 200:

            if 'last' in response.links:

                # Get the total number of pages
                total_pages = int(re.findall(r'\d+', response.links['last']['url'])[-1])

                # Get issues
                for i in tqdm.tqdm(range(1, total_pages + 1)):
                    response = requests.get(url + '&page=' + str(i), auth=(self.username, self.token))

                    # Successful request
                    if response.status_code == 200:

                        # Save the closed issues numbers
                        for closed_issue in response.json():
                            self.closed_issues[str(closed_issue['number'])] = closed_issue
                            self.closed_issues_numbers.append(closed_issue['number'])

                            #Save only issues that are not pull-requests
                            #if 'pull_request' not in closed_issue:

                    else:
                        logging.warning(str(response.status_code))
                    break
            else:
                # Get issues
                for i in tqdm.tqdm(range(1)):
                    response = requests.get(url + '&page=' + str(i), auth=(self.username, self.token))

                    # Successful request
                    if response.status_code == 200:

                        # Save the closed issues numbers
                        for closed_issue in response.json():
                            self.closed_issues[str(closed_issue['number'])] = closed_issue
                            self.closed_issues_numbers.append(closed_issue['number'])

                            # Save only issues that are not pull-requests
                            # if 'pull_request' not in closed_issue:
                    else:
                        logging.warning(str(response.status_code))

        else:
            logging.warning(str(response.status_code))

    def mine_issues(self):

        # Create the output logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Start mining issues
        logger.info('Mining GitHub Issues...')
        #self.collect_issues(url=self.base_url + self.url + '/issues?state=closed&since=>' + str(self.cdc))
        self.collect_issues(url=self.base_url + self.url + '/issues?state=closed')
        logger.info('GitHub Issues successfully mined')


        # Create the output dir if not existent
        try:
            os.makedirs(self.issues_output_path)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

        # Change the working directory to the output one
        os.chdir(self.issues_output_path)

        # Logs
        logging.info('Writing the closed Issues to the output directory...\n')

        # TODO: Get ID xD
        # query_results = self.db.issues.find_one({'project': 'Elasticsearch-Hadoop'})

        #v = []
        #for value in self.closed_issues.values():
        #    v.append(value)

        # print('self.closed_issues: ' + str(self.closed_issues))
        result = self.db.issues.insert_one(self.closed_issues)
        logging.info('Saving Issues in MongoDB Database ... ' + str(result))

        # self.output['issues'] = self.closed_issues

        # self.output['project'] = 'Elasticsearch-Hadoop'
        # self.output['url'] = 'elastic/elasticsearch-hadoop'
        # self.output['update_at'] = datetime.datetime.now()
        # self.output['issues'] = v

        #result = self.db.issues.insert_one(self.output)
        #logging.info('Saving in MongoDB Database ... ' + str(result))

        '''
        # Write issues
        if query_results is None:

            # TODO: Refactor the for to put in one line
            v = []
            for value in self.closed_issues.values():
                v.append(value)

            self.output['issues'] = self.closed_issues

            self.output['project'] = 'Elasticsearch-Hadoop'
            self.output['url'] = 'elastic/elasticsearch-hadoop'
            self.output['update_at'] = datetime.datetime.now()
            self.output['issues'] = v

            result = self.db.issues.insert_one(self.output)


        else:
            project_id = str(query_results.get('_id'))
            logging.info('Project already exists in Database...')
            logging.info('ETL Incremental')
            for key, value in self.closed_issues.items():

                # Write the issue events to a JSON file
                # logging.info('Consulting Issue: ' + key + ' in Database')
                query_results = self.db.issues.find_one(
                    {'_id': ObjectId(project_id), 'issues.number': {'$eq': int(key)}})

                if query_results == None:
                    try:
                        self.db.issues.update({'_id': ObjectId(project_id)},
                                              {'$push': {'issues': value}})
                        logging.info('Issue ' + str(key) + ' inserted in Database')
                    except:
                        logging.info('Error on add Issue')
                        # "Unexpected error:", sys.exc_info()[0]
                        raise

                else:
                    try:
                        self.db.issues.update({'_id': ObjectId(project_id)},
                                              {'$pull': {'issues': {'number': int(key)}}})

                        self.db.issues.update({'_id': ObjectId(project_id)},
                                              {'$push': {'issues': value}})
                        logging.info('Rem/inserting Issue: ' + key + ' in Database')
                    except:
                        logging.info('Error on rem/add Issue')
                        # "Unexpected error:", sys.exc_info()[0]
                        raise

                        # result = self.db.reviews.insert_one(value)

                        # Step 4: Print to the console the ObjectID of the new document
                        # print('Created Issue {0} as ObjectID {1}'.format(key, result.inserted_id))

                        # with open(key + '.json', 'w') as output_file:
                        # json.dump(value, output_file)
        '''