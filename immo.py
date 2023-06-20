#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
import datetime
import pandas as pd
from pandas import json_normalize
from time import sleep
import random 

flag = True
page = 1
date = datetime.datetime.now().strftime("%d")
df_list =[]
while flag:
    print(f'page : {page} - time : {datetime.datetime.now()}')
    sleep(random.randint(1,5))
    response = requests.get(f'https://www.immoweb.be/fr/search-results/maison-et-appartement/a-vendre/bruxelles/arrondissement?countries=BE&page={page}&orderBy=relevance')
    print(len(response.text))
    if len(response.text) == 0:
        flag = False
        break
    if page > 250:
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
df.to_excel(f"immo/outputfolder/database_{datetime.datetime.today().strftime('%Y%m%d')}.xlsx")

