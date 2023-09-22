#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import datetime
import pandas as pd
from pandas import json_normalize
from time import sleep
import random 
import os
import duckdb

flag = True
page = 1
date = datetime.datetime.now().strftime("%d")
df_list =[]
while flag:
    print(f'page : {page} - time : {datetime.datetime.now()}')
    sleep(random.randint(1,5))
    # Define the user agent string
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'

    # Set the headers with the user agent
    headers = {'User-Agent': user_agent}

    # Make the HTTP request with the specified headers
    response = requests.get(f'https://www.immoweb.be/fr/search-results/maison-et-appartement/a-vendre/bruxelles/arrondissement?countries=BE&page={page}&orderBy=relevance', headers=headers)
    print(len(response.json()['results']))
    if len(response.json()['results']) == 0:
        flag = False
        break
    if page > 500:
        flag = False
        break
    page+=1
    meta = []
    #print(response.json()['results'])
    df = json_normalize(response.json(), record_path='results')
    df_list.append(df)    

full_df = pd.concat(df_list)
full_df["extractDate"] = datetime.datetime.now()
full_df["extractYear"] = datetime.datetime.now().strftime("%Y")
full_df["extractMonth"] = datetime.datetime.now().strftime("%m")
full_df["extractDay"] = datetime.datetime.now().strftime("%d")
csv_name = f"immo/outputfolder/database_{datetime.datetime.today().strftime('%Y%m%d')}.csv"
full_df.to_csv(csv_name, sep='|')

SERVICETOKENMD = os.environ["SERVICETOKENMD"]


# initiate the MotherDuck connection through a service token through
con = duckdb.connect(f'md:aggregated?motherduck_token={SERVICETOKENMD}') 
con.sql(f"INSERT INTO aggregated_table SELECT * FROM {csv_name}")
