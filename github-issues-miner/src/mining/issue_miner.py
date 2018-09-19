import errno
import requests
import os
import json
import logging
import re
import tqdm


# Logging basic date/time config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')


class IssueMiner:

    def __init__(self, url, issues_output_path, events_output_path, username, token):

        self.url = url
        self.issues_output_path = issues_output_path
        self.events_output_path = events_output_path
        self.username = username
        self.token = token

        self.closed_issues = {}
        self.closed_issues_numbers = []
        self.issues_events = {}
        self.base_url = 'https://api.github.com/repos/'

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
        logging.info('Writing the Issues events to the output directory...\n')

        # Write issues events
        for key, value in self.issues_events.items():

            # Write the issue events to a JSON file
            with open(key + '.json', 'w') as output_file:
                json.dump(value, output_file)

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

                            # Save only issues that are not pull-requests
                            if 'pull_request' not in closed_issue:
                                self.closed_issues[str(closed_issue['number'])] = closed_issue
                                self.closed_issues_numbers.append(closed_issue['number'])
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
        self.collect_issues(url=self.base_url + self.url + '/issues?state=closed&labels=bug')
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

        # Write issues
        for key, value in self.closed_issues.items():

            # Write the issue events to a JSON file
            with open(key + '.json', 'w') as output_file:
                json.dump(value, output_file)
