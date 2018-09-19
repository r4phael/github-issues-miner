import logging
import glob
import json
import ntpath
import os


# Logging basic date/time config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')


class ClosedByPullRequest:

    def __init__(self, input_path):
        self.input_path = input_path
        self.closed_by_pr = []

    def get_closed_issues(self):

        # Label closed issue
        is_closed_by_pr = False

        # Create the output logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.info('Looking for Issues closed by pull-requests...')

        # Get all files in the input directory
        input_files = glob.glob(self.input_path + '/*.json')

        # Get the events from all closed issues
        for input_file in input_files:

            # Get the events from a single closed issue
            with open(input_file) as data_file:
                issue_events = json.load(data_file)

            # Look for cross-references events of closed pull-request
            for issue_event in issue_events:

                # Check if the event is a cross-reference of a closed pull-request
                if issue_event['event'] == 'cross-referenced' and issue_event['source']['issue']['state'] == 'closed' \
                        and 'pull_request' in issue_event['source']['issue']:
                    # print(input_file)
                    is_closed_by_pr = True

                # Check if the issue was reopened after being closed by a pull-request
                if is_closed_by_pr and issue_event['event'] == 'reopened':
                    is_closed_by_pr = False

            if is_closed_by_pr:
                self.closed_by_pr.append(os.path.splitext(ntpath.basename(input_file))[0])

        return self.closed_by_pr
