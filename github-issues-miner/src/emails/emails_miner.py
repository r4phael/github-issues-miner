import requests
import re
import logging
import csv
import tqdm

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

d_email = {}
d_email_final = {}
d_email_sub = {}

base_url = 'https://api.github.com/users/'
username = 'r4phael'
token = ''

#users = ['tenderlove','nik9000']
users = [line.rstrip('\n') for line in open('emails/users.txt')]

for i in tqdm.tqdm(range(1, len(users))):

        logger.info('Mining User... ' + str(users[i]))
        url = base_url + users[i] + '/events'
        response = requests.get(url=url , auth=(username, token))

        if response.status_code == 200:
            for events in response.json():
                for payload in events['payload']:
                    if 'commits' in payload:
                        for commits in events['payload']['commits']:
                            d_email[(commits['author']['email'])] = commits['author']['name']

        else :
            logger.info('Http Error... ' + str(response.status_code))

        for key, value in d_email.items():
            d_email_sub = {}
            if EMAIL_REGEX.match(key):
                #l_email_final.append(email)
                d_email_final[key] = value
                d_email_sub[key] = value

        logger.info('List of Emails in Events:' + str(d_email_sub))

with open('dict.csv', 'w') as csv_file:

    logger.info('Writting csv file ....')
    writer = csv.writer(csv_file)
    writer.writerow(['AUTHOR','EMAIL'])
    for key, value in d_email_final.items():
        writer.writerow([value, key])