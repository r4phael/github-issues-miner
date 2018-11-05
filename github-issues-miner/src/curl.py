import requests
import re
import logging
import csv

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

d_email = {}
d_email_final = {}

base_url = 'https://api.github.com/users/'
#username = 'r4phael'
#token = '4aa9f722571591c5a9ce2c2480df4e277ac32c25'

#users = ['tenderlove','nik9000']
users = [line.rstrip('\n') for line in open('users.txt')]

for user in users :

    logger.info('Mining User... ' + str(user))

    url = base_url + user + '/events'
    response = requests.get(url=url) #, auth=(username, token))

    if response.status_code == 200:
        for events in response.json():
            for payload in events['payload']:
                if 'commits' in payload:
                    for commits in events['payload']['commits']:
                        d_email[(commits['author']['email'])] = commits['author']['name']

    for key, value in d_email.items():
        if EMAIL_REGEX.match(key):
            #l_email_final.append(email)
            d_email_final[key] = value


print(d_email_final)

with open('dict.csv', 'w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['email','user'])
    for key, value in d_email_final.items():
        writer.writerow([key, value])

