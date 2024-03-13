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

def fetch_data(page):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    headers = {'User-Agent': user_agent}
    response = requests.get(f'https://www.immoweb.be/fr/search-results/maison-et-appartement/a-vendre/arrondissement?countries=BE&page={page}&orderBy=relevance', headers=headers)
    return response.json()

def main():
    flag = True
    page = 1
    df_list = []
    
    while flag and page <= 500:
        print(f'page : {page} - time : {datetime.datetime.now()}')
        sleep(random.randint(1, 5))
        
        results = fetch_data(page)
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
    
    csv_name = f"immo/outputfolder/database_{datetime.datetime.today().strftime('%Y%m%d')}.csv"
    full_df.to_csv(csv_name, sep='|')

    df_out = (
        full_df[['property.type', 'property.bedroomCount', 'property.location.postalCode', 'extractDate', 'price.mainValue', 'id']]
        .groupby(['property.type', 'property.bedroomCount', 'property.location.postalCode', 'extractDate'])
        .agg({'id': 'count', 'price.mainValue': 'sum'})
        .reset_index()
    )
    df_out.columns = ['property.type', 'property.bedroomCount', 'property.location.postalCode', 'extractDate', 'count_id', 'sum_value']
    df_out.to_csv("toduckdbbbbb.csv")

    SERVICETOKENMD = os.environ.get("SERVICETOKENMD")

    if SERVICETOKENMD:
        con = duckdb.connect(f'md:aggregated?motherduck_token={SERVICETOKENMD}') 
        con.sql(f"INSERT INTO aggregated_table SELECT * FROM toduckdbbbbb.csv")
        con.sql(f"INSERT INTO fulldata SELECT * FROM '{csv_name}'")
    else:
        print("SERVICETOKENMD environment variable not set!")
    return df_out.shape[0]
if __name__ == "__main__":
    count = main()

    sender_email = SOME_SECRET
    sender_password = EMAIL_PASSWORD_ME
    receiver_email = SOME_SECRET
    subject = "Hello from Python!"
    body = f"You have extracted {count} housing offers"

    # Call the send_email function
    send_email(sender_email, sender_password, receiver_email, subject, body)




