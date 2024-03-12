import requests
import datetime
import pandas as pd
from pandas import json_normalize
from time import sleep
import random
import os
import duckdb

def fetch_data(page):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    headers = {'User-Agent': user_agent}
    response = requests.get(f'https://www.immoweb.be/fr/search-results/maison-et-appartement/a-vendre/bruxelles/arrondissement?countries=BE&page={page}&orderBy=relevance', headers=headers)
    return response.json()['results']

def main():
    flag = True
    page = 1
    df_list = []
    
    while flag and page <= 500:
        print(f'page : {page} - time : {datetime.datetime.now()}')
        sleep(random.randint(1, 5))
        
        results = fetch_data(page)
        if not results:
            flag = False
            break
        
        df_list.append(json_normalize(results))
        page += 1

    full_df = pd.concat(df_list)
    full_df["extractDate"] = datetime.datetime.now()
    full_df["extractYear"] = full_df["extractDate"].dt.strftime("%Y")
    full_df["extractMonth"] = full_df["extractDate"].dt.strftime("%m")
    full_df["extractDay"] = full_df["extractDate"].dt.strftime("%d")
    
    csv_name = f"immo/outputfolder/database_{datetime.datetime.today().strftime('%Y%m%d')}.csv"
    full_df.to_csv(csv_name, sep='|', index=False)

    df_out = (
        full_df[['property.type', 'property.bedroomCount', 'property.location.postalCode', 'extractDate', 'price.mainValue', 'id']]
        .groupby(['property.type', 'property.bedroomCount', 'property.location.postalCode', 'extractDate'])
        .agg({'id': 'count', 'price.mainValue': 'sum'})
        .reset_index()
    )
    df_out.columns = ['property.type', 'property.bedroomCount', 'property.location.postalCode', 'extractDate', 'count_id', 'sum_value']
    df_out.to_csv("toduckdbbbbb.csv", index=False)

    SERVICETOKENMD = os.environ.get("SERVICETOKENMD")

    if SERVICETOKENMD:
        con = duckdb.connect(f'md:aggregated?motherduck_token={SERVICETOKENMD}') 
        con.execute(f"INSERT INTO aggregated_table SELECT * FROM CSVREAD('toduckdbbbbb.csv')")
        con.execute(f"INSERT INTO fulldata SELECT * FROM CSVREAD('{csv_name}')")
    else:
        print("SERVICETOKENMD environment variable not set!")

if __name__ == "__main__":
    main()
