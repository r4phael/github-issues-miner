import logging
import glob
import json
import ntpath
import os


# Logging basic date/time config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')


class ClosedByCommit:

    def __init__(self, input_path):
        self.input_path = input_path
        self.closed_by_commit = []

    def get_closed_issues(self):

        # Label closed issue
        is_closed_by_commit = False

        # Create the output logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.info('Looking for Issues closed by commits...')

        # Get all files in the input directory
        input_files = glob.glob(self.input_path + '/*.json')

        # Get the events from all closed issues
        for input_file in input_files:

            # Get the events from a single closed issue
            with open(input_file) as data_file:
                issue_events = json.load(data_file)

            # Look for events that match the "closes/fixes #commit" syntax
            for issue_event in issue_events:

                # Check if the event matches the "closes/fixes #commit" syntax
                if issue_event['event'] == 'closed' and issue_event['commit_id']:
                    is_closed_by_commit = True
                    # print(os.path.splitext(ntpath.basename(input_file))[0])
                    # print(issue_event['commit_id'])

                # Check if the issue was reopened after being closed by a commit
                if is_closed_by_commit and issue_event['event'] == 'reopened':
                    is_closed_by_commit = False

            if is_closed_by_commit:
                self.closed_by_commit.append(os.path.splitext(ntpath.basename(input_file))[0])

        return self.closed_by_commit
