from optparse import OptionParser
from mining import github_miner
from mining import v4_miner
from heuristics import heuristics


# Create the CLI parser
usage = "usage: %prog [options] arg"
parser = OptionParser()

# Add the available options to the parser
parser.add_option("-u", "--url", dest="url",  help="GitHub repository URL in format :user/:repository")
parser.add_option("-p", "--path", dest="path", help="Path to the git repository")
parser.add_option("--issues_output", dest="issues_output", help="Path to the Issues output directory")
parser.add_option("--events_output", dest="events_output", help="Path to the Issues events output directory")
parser.add_option("--pr_output", dest="pr_output", help="Path to the Pull Requests output directory")
parser.add_option("--username", dest="username", help="The GitHub username for authentication")
parser.add_option("--token", dest="token", help="The GitHub token for authentication")

# Parse the CLI args
(options, args) = parser.parse_args()

options.url = 'elastic/elasticsearch-hadoop'
options.username = 'r4phael'
options.token = '4aa9f722571591c5a9ce2c2480df4e277ac32c25'
options.issues_output = '/home/r4ph/desenv/data/issues/'
options.events_output = '/home/r4ph/desenv/data/events/'
options.pr_output = '/home/r4ph/desenv/data/prs/'

cdc = '2018-10-01'


#V4 Miner:
miner = v4_miner.V4Miner(options.username, options.token, cdc)
miner.collect_prs_v4()
miner.collect_issues_v4()


# Start GitHub mining
#miner = github_miner.GitHubMiner(options.url, options.username, options.token)
#miner.mine_issues(options.issues_output, options.events_output, cdc)
#miner.mine_pr(options.pr_output)

# Start the heuristics
# heuristics = heuristics.Heuristics(options.events_output)
# heuristics.run_heuristics()
