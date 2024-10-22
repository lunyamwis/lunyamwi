from celery import shared_task
import pandas as pd
import os
import requests
import json
import subprocess
from boostedchatScrapper.spiders.instagram import InstagramSpider
from boostedchatScrapper.spiders.helpers.instagram_login_helper import login_user
from django.utils import timezone
from .models import InstagramUser
from boostedchatScrapper.spiders.constants import STYLISTS_WORDS,STYLISTS_NEGATIVE_WORDS


db_url = f"postgresql://{os.getenv('POSTGRES_USERNAME')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DBNAME')}"
load_tables = True

@shared_task()
def scrap_followers(username,delay,round_):
    inst = InstagramSpider(load_tables=load_tables,db_url=db_url)
    inst.scrap_followers(username,delay,round_=round_)

@shared_task()
def scrap_users(query,round_,index):
    inst = InstagramSpider(load_tables=load_tables,db_url=db_url)
    inst.scrap_users(query,round_=round_,index=index)
    
@shared_task()
def scrap_info(delay_before_requests,delay_after_requests,step,accounts,round):
    inst = InstagramSpider(load_tables=load_tables,db_url=db_url)
    inst.scrap_info(delay_before_requests,delay_after_requests,step,accounts,round)
    load_info_to = 1
    if load_info_to == 1:
        load_info_to_database()
    elif load_info_to == 2:
        load_info_to_csv()
    
@shared_task()
def insert_and_enrich(keywords_to_check,round_number):
    inst = InstagramSpider(load_tables=load_tables,db_url=db_url)
    inst.insert_and_enrich(keywords_to_check,round_number=round_number)


@shared_task()
def scrap_mbo():
    try:
            # Execute Scrapy spider using the command line
        subprocess.run(["scrapy", "crawl", "mindbodyonline"])
        
    except Exception as e:
        print(e)
    

def qualify_algo(client_info,keywords_to_check):
    keyword_found = None
    if client_info:
            keyword_counts = {keyword: 0 for keyword in keywords_to_check}

            # Iterate through the values in client_info
            for value in client_info.values():
                # Iterate through the keywords to check
                for keyword in keywords_to_check:
                    # Count the occurrences of the keyword in the value
                    keyword_counts[keyword] += str(value).lower().count(keyword.lower())

            # Check if any keyword has more than two occurrences
            keyword_found = any(count >= 1 for count in keyword_counts.values())
    return keyword_found

def load_info_to_csv():
    try:
        prequalified = pd.read_csv('prequalified.csv')
        df = prequalified.reset_index()
        for i,user in enumerate(df['level_1']):
            try:
                db_user = InstagramUser.objects.filter(username=user).latest('created_at')
                print(user)
                try:
                    df.at[i,'outsourced_info'] = db_user.info
                except Exception as err:
                    print(err,'---->outsourced_info_error')
                try:
                    df.at[i,'relevant_information'] = db_user.info
                except Exception as err:
                    print(err,'---->relevant infof error')
            except Exception as err:
                print(err,f'---->user--{user} not found')
        df.to_csv('prequalified.csv',index=False)
    except Exception as err:
        print(err,"file not found")  


def load_info_to_database():
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        yesterday = timezone.now() - timezone.timedelta(days=1)
        yesterday_start = timezone.make_aware(timezone.datetime.combine(yesterday,timezone.datetime.min.time()))

        instagram_users = InstagramUser.objects.filter(created_at__gte=yesterday_start)
        for user in instagram_users:
            try:
                account_dict = {
                    "igname": user.username,
                    "is_manually_triggered":True,
                    "relevant_information": user.info
                }
                response = requests.post(
                    "https://api.booksy.us.boostedchat.com/v1/instagram/account/",
                    headers=headers,
                    data=json.dumps(account_dict)
                )
                account = response.json()
                print(account)
                # Save outsourced data
                
                outsourced_dict = {
                    "results": {**user.info,"media_id":user.item_id}, # yet to test
                    "source": "instagram"
                }
                # import pdb;pdb.set_trace()
                response = requests.post(
                    f"https://api.booksy.us.boostedchat.com/v1/instagram/account/{account['id']}/add-outsourced/",
                    headers=headers,
                    data=json.dumps(outsourced_dict)
                )
                if response.status_code in [200,201]:
                    print("successfully posted outsourced data")
                else:
                    print("failed to post outsourced data")
                # Save relevant data
                if qualify_algo(user.info,STYLISTS_WORDS):
                    try:
                        inbound_qualify_data = {
                            "username": user.username,
                            "qualify_flag": True,
                            "relevant_information": json.dumps(user.relevant_information),
                            "scraped":True
                        }
                        response = requests.post("https://api.booksy.us.boostedchat.com/v1/instagram/account/qualify-account/",data=inbound_qualify_data)

                        if response.status_code in [200,201]:
                            print(response.json())
                            print(f"Account-----{user.username} successfully qualified")
                    except Exception as err:
                        print(err,f"---->error in qualifying user {user.username}")
                else:
                    print("failed to qualify")
            except Exception as err:
                print(err, f"---->error in posting user {user.username}")
    except Exception as err:
        print(err, "---->error in posting data")




@shared_task()
def scrap_media(media_links):
    inst = InstagramSpider(load_tables=load_tables,db_url=db_url)
    inst.scrap_media(media_links)
    