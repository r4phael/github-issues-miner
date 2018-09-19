import closed_by_commit
import closed_by_pr
import logging


# Logging basic date/time config
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')


class Heuristics:

    def __init__(self, input_path):
        self.input_path = input_path
        self.closed_by_commit = []
        self.closed_by_pr = []

    def run_heuristics(self):

        # Create the output logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Get issues closed by commits
        by_commit = closed_by_commit.ClosedByCommit(self.input_path)
        self.closed_by_commit = by_commit.get_closed_issues()

        # # Get issues closed by pull-requests
        # by_pr = closed_by_pr.ClosedByPullRequest(self.input_path)
        # self.closed_by_pr = by_pr.get_closed_issues()
        #
        # # Remove repeated Issues found by the heuristics
        # for issue in self.closed_by_pr:
        #     if issue in self.closed_by_commit:
        #         self.closed_by_pr.remove(issue)

        logger.info('Issues closed by commits (H1): ' + str(len(self.closed_by_commit)))
        # logger.info('Issues closed by Pull Requests (H2): ' + str(len(self.closed_by_pr)))
