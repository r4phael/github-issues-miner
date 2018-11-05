import issue_miner
import pr_miner
import v4_miner


class GitHubMiner:

    def __init__(self, url, username, token):
        self.url = url
        self.username = username
        self.token = token

    def mine_issues(self, issues_output, events_output, cdc):

        # Mine GitHub closed issues
        mine_issues = issue_miner.IssueMiner(self.url, issues_output, events_output, self.username, self.token, cdc)
        mine_issues.mine_issues()
        mine_issues.mine_issues_events()
        mine_issues.mine_issues_comments()

    def mine_pr(self, pr_output):

        # Mine GitHub closed pull-requests
        mine_prs = pr_miner.PullRequestMiner(self.url, pr_output, self.username, self.token)
        mine_prs.mine_prs()
        mine_prs.mine_prs_reviews()


    def mine_v4(self):
        mine_v4 = v4_miner.V4Miner(self.token, self.username)
        mine_v4.mine_issues()
