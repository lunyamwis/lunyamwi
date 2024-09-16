import time
import json
import uuid
import sys
import os
import re
import random
import logging
import pandas as pd
import requests
# current_dir = os.getcwd()




# Add the current directory to sys.path
# sys.path.append(current_dir)
import concurrent.futures
from .helpers.instagram_login_helper import login_user
from datetime import datetime, timedelta
from django.utils import timezone
from django.conf import settings
from urllib.parse import urlparse
#from kafka import KafkaProducer
from collections import ChainMap
from .constants import STYLISTS_WORDS,STYLISTS_NEGATIVE_WORDS
from sqlalchemy import create_engine, text,Table,MetaData,select,update
from api.instagram.models import InstagramUser
from api.scout.models import Scout,Device
from django.core.mail import send_mail
from django.db.models import Q

class InstagramSpider:
    name = 'instagram'
    # db_url = f"postgresql://{os.getenv('POSTGRES_USERNAME')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DBNAME')}"
    # engine = create_engine(db_url)
    # connection = engine.connect()
    # transaction = connection.begin()
    
    def __init__(self, load_tables: bool, db_url: str):
        if load_tables:
            self.metadata = MetaData()
            self.engine = create_engine(db_url)
            self.instagram_account_table = Table('instagram_account', self.metadata, autoload_with=self.engine)
            self.instagram_outsourced_table = Table('instagram_outsourced',self.metadata, autoload_with=self.engine)
            self.django_celery_beat_crontabschedule_table = Table('django_celery_beat_crontabschedule', self.metadata, autoload_with=self.engine)
            self.django_celery_beat_periodictask_table = Table('django_celery_beat_periodictask', self.metadata, autoload_with=self.engine)
            self.salesrep_table = Table('sales_rep_salesrep',self.metadata,autoload_with=self.engine)
            self.salesrep_instagram_table = Table('sales_rep_salesrep_instagram',self.metadata,autoload_with=self.engine)

    
    def store(self,users,source=1,linked_to='no_one',round=0):
        for user in users:
            InstagramUser.objects.create(username = user.username,info = user.dict(),source=source,linked_to=linked_to,round=round)

    def is_cursor_available(self):
        is_cursor_available = InstagramUser.objects.filter(Q(username__isnull=True) & Q(cursor__isnull=False))
        if is_cursor_available.exists():
            cursor = is_cursor_available.latest('created_at')
        return cursor

    def scrap_followers(self,username,delay,round_):
        scouts = Scout.objects.filter(available=True)
        scout_index = 0
        initial_scout = scouts[scout_index]
        try:
            client = login_user(initial_scout)
        except Exception as error:
            try:
                send_mail(
                    "Check Issue",
                    f"Please resolve {str(error)} for account {initial_scout.username}",
                    "from@example.com",
                    [initial_scout.email],
                    fail_silently=False,
                )
            except Exception as error:
                print(error)
            print(error)
        
        user_info = client.user_info_by_username(''.join(username))
        time.sleep(delay)
        steps = user_info.follower_count/12
        
        try:
            followers,cursor = client.user_followers_gql_chunk(user_info.pk, max_amount=3)
        except Exception as error:
            InstagramUser.objects.create(cursor=cursor)
            print(error)

        self.store(followers,round=round_)
        time.sleep(delay)
        if self.is_cursor_available:
            cursor = cursor
        for i in range(int(steps)-1):
            time.sleep(random.randint(delay,delay*2))
            try:
                followers, cursor = client.user_followers_gql_chunk(user_info.pk, max_amount=5,end_cursor=cursor)
            except Exception as error:
                InstagramUser.objects.create(cursor=cursor)
            self.store(followers,round=round_)

    def scrap_users(self,query,round_,index=0):
        scouts = Scout.objects.filter(available=True)
        scout_index = 0
        initial_scout = scouts[scout_index]
        
        client = login_user(scout=initial_scout)
        for i,user in enumerate(query[index:]):
            time.sleep(random.randint(4,8))
            print(i, user)

            try:
                users = client.search_users_v1(user,count=3)
            except Exception as error:
                print(error)
            self.store(users,round=round_)
            if i % 3 == 0:
                try:
                    scout_index = (scout_index + 1) % len(scouts)
                    client = login_user(scouts[scout_index])
                except Exception as error:
                    try:
                        send_mail(
                            "Check Issue",
                            f"Please resolve {str(error)} for account {initial_scout.username}",
                            "from@example.com",
                            [initial_scout.email],
                            fail_silently=False,
                        )
                    except Exception as error:
                        print(error)
                    print(error)
            if i % 16 == 0:
                time.sleep(random.randint(4,8))

       
    def scrap_extra(self, url, params, return_val):
        scouts = Scout.objects.filter(available=True)
        scout_index = 0
        initial_scout = scouts[scout_index]
        try:
            client = login_user(initial_scout)
        except Exception as error:
            try:
                send_mail(
                    "Check Issue",
                    f"Please resolve {str(error)} for account {initial_scout.username}",
                    "from@example.com",
                    [initial_scout.email],
                    fail_silently=False,
                )
            except Exception as error:
                print(error)
            print(error)
        result = client.private_request(url, params=params)
        self.store(result[return_val])    
        return result[return_val]
    
    def generate_comment(self, media, username):
        comment = None
        if media.thumbnail_url: # to handle a single image
            
            resp = requests.post(url=settings.AI_MICROSERVICE_URL+"blipInference/", data = {'media_url':media.thumbnail_url.strip()})
            if resp.status_code == 200:
                resp_ =  requests.post(url=settings.AI_MICROSERVICE_URL+"gptInference/",data={'prompt':f"Please carefully examine the caption provided to determine if it showcases the work of a barber known as {username}. If it appears to be a presentation of the barber's work, rephrase the caption to resemble a complimentary comment that could be directly posted under the image  on Instagram. If the caption does not depict work posted by the barber, please respond with the word ```AWESOME`` enclosed in triple backticks return in json format the rephrased caption 'generated_text': rephrased_caption, caption is as follows: {resp.json()['captioned_text']} "})
                if resp_.status_code == 200:
                    comment = json.loads(resp_.json()['choices'][0]['message']['content']).get('generated_text')

        else:
            for resource in media.resources: # to handle a reel or many images
                if resource.thumbnail_url:
                    resp = requests.post(url=settings.AI_MICROSERVICE_URL+"blipInference/", data = {'media_url':resource.thumbnail_url.strip()})
                    if resp.status_code == 200:
                        resp_ =  requests.post(url=settings.AI_MICROSERVICE_URL+"gptInference/",data={'prompt':f"Please carefully examine the caption provided to determine if it showcases the work of a barber known as {username}. If it appears to be a presentation of the barber's work, rephrase the caption to resemble a complimentary comment that could be directly posted under the image  on Instagram. If the caption does not depict work posted by the barber, please respond with the word ```AWESOME`` enclosed in triple backticks return in json format the rephrased caption 'generated_text': rephrased_caption, caption is as follows: {resp.json()['captioned_text']} "})
                        if resp_.status_code == 200:
                            comment = json.loads(resp_.json()['choices'][0]['message']['content']).get('generated_text')
                            break
        return comment
    
    def extract_inbox_data(self,data):
        inbox = data.get('inbox', {})
        threads = inbox.get('threads', [])

        result = []

        for thread in threads:
            users = thread.get('users', [])
            for user in users:
                username = user.get('username')
                thread_id = thread.get('thread_id')
                items = thread.get('items', [])

                for item in items:
                    item_id = item.get('item_id')
                    user_id = item.get('user_id')
                    item_type = item.get('item_type')
                    timestamp = item.get('timestamp')
                    message = item.get('text')

                    data_dict = {
                        'username': username,
                        'thread_id': thread_id,
                        'item_id': item_id,
                        'user_id': user_id,
                        'item_type': item_type,
                        'timestamp': timestamp
                    }

                    if item_type == 'text':
                        data_dict['message'] = message

                    result.append(data_dict)

        return result


    def scrap_inbox(self,scout):
        client = login_user(scout)
        inbox = client.private_request("direct_v2/pending_inbox/",params = {
            'visual_message_return_type': 'unseen',
            'eb_device_id': '0',
            'no_pending_badge': 'true',
            'persistentBadging': 'true',
            'push_disabled': 'true',
            'is_prefetching': 'false',
            'request_session_id': client.request_id,
         },)
        inbox_dataset = self.extract_inbox_data(inbox)
        return inbox_dataset
    
    def approve_inbox_request(self,scout,inbox_dataset):
        client = login_user(scout)
        inbox_dataset = self.scrap_inbox(scout)
        approved_requests = []
        data = {
            'filter': 'DEFAULT',
            '_uuid': client.uuid,
        }
        for dataset in inbox_dataset:
            if dataset.get('approve'):
                client.private_request(f"direct_v2/threads/{dataset.get('thread_id')}/approve/",data=data)
                approved_requests.append({
                    "username":dataset.get('username'),
                    "text": dataset.get('text'),
                    "thead_id":dataset.get('thread_id')
                })
        return approved_requests
    
    def respond(self, scout, thread_id, message):
        client = login_user(scout)
        client.direct_answer(thread_id,message)

    def extract_direct_inbox_data(self, data):
        headers = {
            'Content-Type': 'application/json'
        }
        
        threads = data
        
        result = []

        for thread in threads:
            users = thread.get('users', [])
            
            for user in users:
                username = user.get('username')
                thread_id = thread.get('thread_id')
                items = thread.get('items', [])

                for item in items:
                    item_id = item.get('item_id')
                    user_id = item.get('user_id')
                    item_type = item.get('item_type')
                    timestamp = item.get('timestamp')
                    message = item.get('text')

                    data_dict = {
                        'username': username,
                        'item_id': item_id,
                        'user_id': user_id,
                        'item_type': item_type,
                        'timestamp': timestamp,
                        'round': 1908,
                        'pending': True,
                        'is_manually_triggered':True,
                        'info': {**user}
                    }

                    # Save the lead information to the lead database - scrapping microservice
                    response = requests.post(
                        "https://scrapper.booksy.us.boostedchat.com/instagram/instagramLead/",
                        headers=headers,
                        data=json.dumps(data_dict)
                    )
                    if response.status_code in [200, 201]:
                        print("right track")

                    if item_type == 'text':
                        # Save the message
                        # Create an account for it/ also equally save outsourced info for it
                        account_dict = {

                            "igname": username,
                            "is_manually_triggered":True
                        }
                        # Save account data
                        response = requests.post(
                            "https://api.booksy.us.boostedchat.com/v1/instagram/account/",
                            headers=headers,
                            data=json.dumps(account_dict)
                        )
                        account = response.json()
                        # Save outsourced data
                        outsourced_dict = {
                            "results": {
                                **user
                            },
                            "source": "instagram"
                        }
                        response = requests.post(
                            f"https://api.booksy.us.boostedchat.com/v1/instagram/account/{account['id']}/add-outsourced/",
                            headers=headers,
                            data=json.dumps(outsourced_dict)
                        )
                        # Create a thread and store the message
                        data_dict['thread_id'] = thread_id
                        data_dict['message'] = message
                        
                        thread_dict = {
                            "thread_id": thread_id,
                            "account_id": account['id'],
                            "unread_message_count": 0,
                            "last_message_content": message,
                            "last_message_at": datetime.now().isoformat()
                        }
                        response = requests.post(
                            "https://api.booksy.us.boostedchat.com/v1/instagram/dm/create-with-account/",
                            headers=headers,
                            data=json.dumps(thread_dict)
                        )

                        thread_pk = response.json()['id']

                        # Save the message in the thread
                        message_dict = {
                            "content": message,
                            "sent_by": "Client",
                            "thread": thread_pk,
                            "sent_on": datetime.now().isoformat()
                        }
                        response = requests.post(
                            "https://api.booksy.us.boostedchat.com/v1/instagram/message/",
                            headers=headers,
                            data=json.dumps(message_dict)
                        )
                    
                    result.append(data_dict)

        return result

    def scrap_info(self,delay_before_requests,delay_after_requests,step,accounts,round,index=0):
        scouts = Scout.objects.filter(available=True)
        scout_index = 0
        initial_scout = scouts[scout_index]
        try:
            client = login_user(initial_scout)
        except Exception as error:
            try:
                send_mail(
                    "Check Issue",
                    f"Please resolve {str(error)} for account {initial_scout.username}",
                    "from@example.com",
                    [initial_scout.email],
                    fail_silently=False,
                )
            except Exception as error:
                print(error)
            print(error)
        
        yesterday = timezone.now().date() - timezone.timedelta(days=1)
        yesterday_start = timezone.make_aware(timezone.datetime.combine(yesterday, timezone.datetime.min.time()))
        # the instagram users who are manually triggered need to be given first priority
        instagram_users = InstagramUser.objects.filter(Q(created_at__gte=yesterday_start) & Q(is_manually_triggered=True))
        if instagram_users.exists():
            # manually qualify and assign those accounts
            headers = {
                'Content-Type': 'application/json'
            }
            for user in instagram_users:
                # check if account or thread exists otherwise pull the inbox afresh
                check_accounts_endpoint = "https://api.booksy.us.boostedchat.com/v1/instagram/checkAccountExists/"
                check_threads_endpoint = "https://api.booksy.us.boostedchat.com/v1/instagram/checkThreadExists/"
                check_data = {
                    "username": user.username
                }
                check_account_response = requests.post(check_accounts_endpoint,data=check_data)
                check_thread_response = requests.post(check_threads_endpoint,data=check_data)
                if check_account_response.json()['exists'] and check_thread_response.json()['exists']:
                    # manually trigger, qualify, and assign
                    # perform inbound triggering
                    inbound_trigger_data = {
                        "username": user.username
                    }
                    response = requests.post("https://api.booksy.us.boostedchat.com/v1/instagram/account/manually-trigger/",data=inbound_trigger_data)
                    if response.status_code in [200,201]:
                        print(f"Account-----{user.username} successfully triggered")

                    # perform inbound qualifying
                    inbound_qualify_data = {
                        "username": user.username,
                        "qualify_flag": True,
                        "relevant_information": user.relevant_information,
                        "scraped":True
                    }
                    response = requests.post("https://api.booksy.us.boostedchat.com/v1/instagram/account/qualify-account/",data=inbound_qualify_data)
                    if response.status_code in [200,201]:
                        print(f"Account-----{user.username} successfully qualified")

                    # perform outbound qualifying
                    user.qualified = True
                    user.save()


                    # perform salesrep assignment
                    endpoint = "https://api.booksy.us.boostedchat.com/v1/sales/assign-salesrep/"
                    payload = {"username": ""}
                    try:
                        response = requests.post(endpoint, data=json.dumps(payload), headers=headers)
                        response.raise_for_status()  # Raise an exception for HTTP errors
                        print(f"Account-----{user.username} successfully assigned")
                    except requests.exceptions.RequestException as e:
                        print( {"error": str(e)})
                else:
                    pass
                    # fetch the direct inbox items

                    # username = 'blendscrafters'
                    # endpoint = "https://mqtt.booksy.us.boostedchat.com"
                    # Send a POST request to the fetchDirectInbox endpoint
                    
                    # response = requests.post(f'{endpoint}/fetchDirectInbox', json={'username_from': username})
                    
                    # # Check the status code of the response
                    # if response.status_code == 200:
                    #     # Print the response JSON
                    #     print("all is well")
                    #     print(json.dumps(response.json(), indent=2))
                    #     inbox_data = response.json()
                    #     inbox_dataset = self.extract_direct_inbox_data(inbox_data)
                    #     print(inbox_dataset)
                        
                    # else:
                    #     print(f'Request failed with status code {response.status_code}')
        else:
            # pick the automatically generated ones
            instagram_users = InstagramUser.objects.filter(Q(created_at__gte=yesterday_start))

        print(len(instagram_users))
        
        for i, user in enumerate(instagram_users[index:], start=1):
            print(i)
            if user.username:
                time.sleep(random.randint(delay_before_requests,delay_before_requests+step))
                try:

                    info_dict = client.user_info_by_username(user.username).dict()
                    try:
                        user_medias = client.user_medias(info_dict.get("pk"),amount=5)
                        # comment = self.generate_comment(user_medias[0],user.username)
                        # info_dict.update({"media_comment":comment})
                        media_res = []
                        for user_media in user_medias:
                            if user_media:
                                media_info_ = client.media_info(user_media.id)
                                media_res.append({
                                    "media_id":media_info_.id,
                                    "media_url":media_info_.thumbnail_url,
                                    "media_caption":media_info_.caption_text,
                                    "media_taken_at":media_info_.taken_at
                                })
                        info_dict.update({"medias":media_res})
                    except Exception as error:
                        info_dict.update({"media_id":""})
                        print(error)
                    user.info = info_dict

                    user.save()
                    # try:
                    #     account_dict = {
                    #         "igname": user.username,
                    #         "is_manually_triggered":True
                    #     }
                    #     # Save account data
                    #     response = requests.post(
                    #         "https://api.booksy.us.boostedchat.com/v1/instagram/account/",
                    #         headers=headers,
                    #         data=json.dumps(account_dict)
                    #     )
                    #     account = response.json()
                    #     # Save outsourced data
                    #     outsourced_dict = {
                    #         "results": {
                    #             **user.info
                    #         },
                    #         "source": "instagram"
                    #     }
                    #     response = requests.post(
                    #         f"https://api.booksy.us.boostedchat.com/v1/instagram/account/{account['id']}/add-outsourced/",
                    #         headers=headers,
                    #         data=json.dumps(outsourced_dict)
                    #     )
                    #     inbound_qualify_data = {
                    #         "username": user.username,
                    #         "qualify_flag": True,
                    #         "relevant_information": user.relevant_information,
                    #         "scraped":True
                    #     }
                    #     response = requests.post("https://api.booksy.us.boostedchat.com/v1/instagram/account/qualify-account/",data=inbound_qualify_data)

                    #     if response.status_code in [200,201]:
                    #         print(f"Account-----{user.username} successfully qualified")
                    # except Exception as error:
                    #     print(error)
                        
                except Exception as error:
                    user.outsourced_id_pointer=True
                    user.save()
                    print(error)
                
                if i % step == 0:
                    try:
                        scout_index = (scout_index + 1) % len(scouts)
                        client = login_user(scouts[scout_index])
                    except Exception as error:
                        try:
                            send_mail(
                                "Check Issue",
                                f"Please resolve {str(error)} for account {initial_scout.username}",
                                "from@example.com",
                                [initial_scout.email],
                                fail_silently=False,
                            )
                        except Exception as error:
                            print(error)
                        print(error)
                if i % accounts == 0:
                    time.sleep(random.randint(delay_after_requests,delay_after_requests+step))
    

    
    
    
    def assign_salesreps(self,username,index):
        
        with self.engine.connect() as connection:
            salesreps = None

            try:
                get_salesreps = select([self.salesrep_table]).where(
                    self.salesrep_table.c.available == True
                )

                results = connection.execute(get_salesreps)
                salesreps = results.fetchall()
                
                print(f"no_salesreps=================={len(salesreps)}")
            except Exception as error:
                print(error)
            
            salesrep_id = salesreps[index % len(salesreps)]['id']
            get_account = select([self.instagram_account_table]).where(
                self.instagram_account_table.c.igname == username
            )
            try:
                results = connection.execute(get_account)
                account = results.fetchone()
            except Exception as error:
                print(error)

            if account:
                insert_statement = self.salesrep_instagram_table.insert().values({
                    'salesrep_id': salesrep_id,
                    'account_id': account['id']
                })
                try:
                    connection.execute(insert_statement)
                except Exception as error:
                    print(error)
            else:
                print(f"Account {username} does not exist")
            
            ig_users = InstagramUser.objects.filter(username=username)
            if ig_users.exists():
                ig_user = ig_users.last()
                ig_user.attached_salesrep = salesreps[index % len(salesreps)]['ig_username']
                ig_user.save()


    def qualify(self, client_info, keywords_to_check,time_to_begin_outreach):
        qualified = False
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

            if keyword_found:
                with self.engine.connect() as connection:
                    crontab_data = {'minute':time_to_begin_outreach.minute,'hour':time_to_begin_outreach.hour,
                                    'day_of_week':'*','day_of_month':time_to_begin_outreach.day,
                                    'month_of_year':time_to_begin_outreach.month,'timezone':'UTC'}
                    crontab_statement = self.django_celery_beat_crontabschedule_table.insert().values(crontab_data).returning(self.django_celery_beat_crontabschedule_table.c.id)
                    result = connection.execute(crontab_statement)
                    crontab_id = result.fetchone()
                    if crontab_id:
                        periodic_data = {'name':f"SendFirstCompliment-{client_info['username']}-workflow",'task':'instagram.tasks.send_first_compliment','crontab_id':crontab_id['id'],
                                        'args':json.dumps([client_info['username']]),'kwargs':json.dumps({}),'enabled':True,'one_off':True,'total_run_count':0,'date_changed':datetime.now(),
                                        'description':'test','headers':json.dumps({})}
                        periodic_task_statement = self.django_celery_beat_periodictask_table.insert().values(periodic_data)
                        try:
                            connection.execute(periodic_task_statement)
                        except Exception as error:
                            print(error)
                        print(f"successfullyninsertedperiodictaskfor->{client_info['username']}")
                        qualified = True
        return qualified,keyword_counts


    
    def insert_and_enrich(self, keywords_to_check, round_number):
        instagram_users = InstagramUser.objects.filter(round=round_number)
        hour = 4
        for i, instagram_user in enumerate(instagram_users):
            if instagram_user.username and not instagram_user.info.get('is_private'):
                # import pdb;pdb.set_trace()
                try:
                    with self.engine.connect() as connection:
                        try:
                            existing_username_query = select([self.instagram_account_table]).where(
                                self.instagram_account_table.c.igname == instagram_user.username
                            )
                        except Exception as err:
                            try:
                                existing_username_query = select(self.instagram_account_table).where(
                                    self.instagram_account_table.c.igname == instagram_user.username
                                )
                            except Exception as err:
                                print(err)
                        existing_username = connection.execute(existing_username_query).fetchone()
                        print(existing_username)
                        if existing_username:
                            pass
                        else:
                            insert_statement = self.instagram_account_table.insert().values(
                                id=str(uuid.uuid4()),
                                created_at=timezone.now(),
                                updated_at=timezone.now(),
                                igname=instagram_user.username,
                                full_name=instagram_user.info.get('full_name', ''),
                                assigned_to="Robot",
                                dormant_profile_created=True,
                                qualified=False,
                                index=1,
                                linked_to="not"
                            ).returning(self.instagram_account_table.c.id)

                            account_id = connection.execute(insert_statement).fetchone()[0]

                            insert_statement = self.instagram_outsourced_table.insert().values(
                                id=str(uuid.uuid4()),
                                created_at=timezone.now(),
                                updated_at=timezone.now(),
                                source="ig",
                                results=instagram_user.info,
                                account_id=account_id
                            ).returning(self.instagram_outsourced_table.c.results)

                            record = connection.execute(insert_statement).fetchone()
                            qualified,keyword_counts = self.qualify(record['results'], keywords_to_check, datetime.now() + timedelta(hours=hour))
                            if qualified:
                                filtered_dict = {key: value for key, value in keyword_counts.items() if value >= 2}
                                instagram_user.qualified_keywords = str(filtered_dict)
                                instagram_user.qualified = True
                                instagram_user.save()
                                self.assign_salesreps(instagram_user.username, i)

                except Exception as error:
                    print(error)
