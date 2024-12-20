import requests
import datetime
import pandas as pd
from pandas import json_normalize
from time import sleep
import random
import os
import duckdb
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

try:
    SOME_SECRET = os.environ["EMAIL_ME"]
    EMAIL_PASSWORD_ME = os.environ["EMAIL_PASSWORD_ME"]
except KeyError:
    SOME_SECRET = "Token not available!"
    EMAIL_PASSWORD_ME  ="HAHA"

def send_email(sender_email, sender_password, receiver_email, subject, body):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to the email
    message.attach(MIMEText(body, "plain"))

    # Create SMTP session for sending the email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Enable secure connection
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message.as_string())

def fetch_data(page,t,p):
    url = f'https://www.immoweb.be/fr/search-results/{t}/a-vendre/?countries=BE&provinces={p}&page={page}&orderBy=relevance'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers)
    return response.json()

def main(t,p):
    flag = True
    page = 1
    df_list = []
    url = f'https://www.immoweb.be/fr/search-results/{t}/a-vendre/?countries=BE&provinces={p}&page=1&orderBy=relevance'
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    headers = {'User-Agent': user_agent}
    response = requests.get(url, headers=headers)
    print(response.status_code)
    print(response.text)  
    response = response.json()
    if response['marketingCount']%30==0:
        pages = (response['marketingCount']//30)
    else:
        pages = (response['marketingCount']//30)+1
    print("=====")
    print(f" count of props : {response['marketingCount']}")
    print(url)
    while flag and page <= pages:
        print(f'type : {t} province : {p} page : {page} - time : {datetime.datetime.now()}')
        sleep(random.randint(2, 5))
        
        results = fetch_data(page,t,p)
        if len(results)==0:
            flag = False
            break
        
        df_list.append(json_normalize(results['results']))
        page += 1

    full_df = pd.concat(df_list)
    full_df["extractDate"] = datetime.datetime.now()
    full_df["extractYear"] = full_df["extractDate"].dt.strftime("%Y")
    full_df["extractMonth"] = full_df["extractDate"].dt.strftime("%m")
    full_df["extractDay"] = full_df["extractDate"].dt.strftime("%d")
    
    return full_df

if __name__ == "__main__":
    df_list = []
    provinces = ['BRUSSELS','EAST_FLANDERS','NAMUR','LUXEMBOURG','WALLOON_BRABANT','FLEMISH_BRABANT','LIEGE','WEST_FLANDERS','HAINAUT','LIMBURG','ANTWERP']
    type = ['maison','appartement']
    for p in provinces:
        for t in type:
            df = main(t,p)
            df_list.append(df)
    # Ensure the directory exists
    output_dir = 'immo/outputfolder/'
    os.makedirs(output_dir, exist_ok=True)
    csv_name = f"{output_dir}database_{datetime.datetime.today().strftime('%Y%m%d')}.csv"
    print(csv_name)
    full_df = pd.concat(df_list)
    full_df.to_csv(csv_name, sep='|')

    df_out = (
        full_df[['property.type', 'property.bedroomCount', 'property.location.postalCode', 'extractDate', 'price.mainValue', 'id']]
        .groupby(['property.type', 'property.bedroomCount', 'property.location.postalCode', 'extractDate'])
        .agg({'id': 'count', 'price.mainValue': 'sum'})
        .reset_index()
    )
    df_out.columns = ['property.type', 'property.bedroomCount', 'property.location.postalCode', 'extractDate', 'count_id', 'sum_value']
    df_out.to_csv("toduckdbbbbb.csv")
    count = full_df.shape[0]
    SERVICETOKENMD = os.environ.get("SERVICETOKENMD")

    if SERVICETOKENMD:
        con = duckdb.connect(f'md:aggregated?motherduck_token={SERVICETOKENMD}') 

        con.sql(f"CREATE OR REPLACE TABLE V2fulldata AS SELECT * FROM '{csv_name}'") # last run only

        con.sql(f"""INSERT INTO V2aggregated_table 
                SELECT
                    "property.location.country",
                    "property.location.region",
                    "property.location.province",
                    "property.location.district",
                    "property.location.locality",
                    "property.location.postalCode",
                    "property.type",
                    CASE
                        WHEN "property.netHabitableSurface" <= 50 THEN '0-50'
                        WHEN "property.netHabitableSurface" <= 100 THEN '51-100'
                        WHEN "property.netHabitableSurface" <= 150 THEN '101-150'
                        ELSE 'Over 150'
                    END AS netHabitableSurface_bin,
                    COUNT(*) AS num_properties,
                    SUM("property.netHabitableSurface") AS sum_net_habitable_surface,
                    AVG("property.netHabitableSurface") AS avg_net_habitable_surface,
                    SUM("property.roomCount") AS sum_room_count,
                    AVG("property.roomCount") AS avg_room_count,
                    SUM("price.mainValue") AS sum_price,
                    AVG("price.mainValue") AS avg_price,
                    MAX("price.mainValue") AS max_price,
                    MIN("price.mainValue") AS min_price,
                    MAX("property.landSurface") AS max_land_surface,
                    "extractDate",
                    "extractYear",
                    "extractMonth",
                    "extractDay",
                    PERCENTILE_CONT(0.05) WITHIN GROUP (ORDER BY "price.mainValue") AS low_percentile,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY "price.mainValue") AS high_percentile,
                    CASE
                        WHEN "price.mainValue" < low_percentile THEN 'isToLow'
                        ELSE NULL
                    END AS price_flag_low,
                    CASE
                        WHEN "price.mainValue" > high_percentile THEN 'isToHigh'
                        ELSE NULL
                    END AS price_flag_high
                FROM
                    V2fulldata
                GROUP BY
                    "property.location.country",
                    "property.location.region",
                    "property.location.province",
                    "property.location.district",
                    "property.location.locality",
                    "property.location.postalCode",
                    "property.type",
                    "netHabitableSurface_bin",
                    "extractDate",
                    "extractYear",
                    "extractMonth",
                    "extractDay",
                    "price.mainValue"
                """)
    else:
        print("SERVICETOKENMD environment variable not set!")

    sender_email = SOME_SECRET
    sender_password = EMAIL_PASSWORD_ME
    receiver_email = SOME_SECRET
    subject = "Hello from Python!"
    body = f"You have extracted {count} housing offers"

    # Call the send_email function
    send_email(sender_email, sender_password, receiver_email, subject, body)




