import csv
import pandas as pd
import random
import numpy as np

csv_file = 'emails_list.csv'

df = pd.read_csv(csv_file, error_bad_lines=False, delimiter = ';')
logins = df['login'].values

#logins_random = np.random.choice(logins,2000)

with open('users.txt', 'w') as f:
    for item in logins: #logins_random:
        f.write("%s\n" % item)

