import json
import os
import errno
import requests
import logging
import re
import tqdm
import csv


# Logging basic date/time config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')


class PullRequestMiner:

    def __init__(self, url, output_path, username, token):

        self.url = url
        self.output_path = output_path
        self.username = username
        self.token = token

        self.closed_prs = {}
        self.closed_prs_numbers = []
        self.base_url = 'https://api.github.com/repos/'

    def collect_prs(self, url):

        # Get the pull-requests data
        response = requests.get(url, auth=(self.username, self.token))

        # Successful request
        if response.status_code == 200:

            if 'last' in response.links:

                # Get the total number of pages
                total_pages = int(re.findall(r'\d+', response.links['last']['url'])[-1])

                # Get pull-requests
                for i in tqdm.tqdm(range(1, total_pages + 1)):
                    response = requests.get(url + '&page=' + str(i), auth=(self.username, self.token))

                    # Successful request
                    if response.status_code == 200:

                        # Save the closed pull-requests numbers
                        for closed_pr in response.json():
                            self.closed_prs[str(closed_pr['number'])] = closed_pr
                            self.closed_prs_numbers.append(closed_pr['number'])
                    else:
                        logging.warning(str(response.status_code))
        else:
            logging.warning(str(response.status_code))

    def mine_prs(self):

        # Create the output logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Start mining pull-requests
        logger.info('Mining GitHub Pull Requests...')
        self.collect_prs(url=self.base_url + self.url + '/pulls?state=closed')
        logger.info('GitHub Pull Requests successfully mined')

        # Create the output dir if not existent
        try:
            os.makedirs(self.output_path)
        except OSError as error:
            if error.errno != errno.EEXIST:
                raise

        # Change the working directory to the output one
        os.chdir(self.output_path)

        # Logs
        logging.info('Writing the closed Pull Requests to the output directory...\n')

        # Write Pull Requests
        for key, value in self.closed_prs.items():

            # Write the pull Requests to a JSON file
            with open(key + '.json', 'w') as output_file:
                json.dump(value, output_file)
