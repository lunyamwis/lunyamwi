import json
import os
import requests
from boostedchatScrapper.models import ScrappedData
from django.db.models import Q

# Function to get access token
def get_access_token():
    try:
        response = requests.post("https://api.thecut.co/v1/auth/token", headers={
            "Authorization": "Basic YzgwMWE2NmEtNDJlMC00ZTZhLThiZTMtOTIwYzExNWY4NWJkOjU1NTM0MTFjLWIxNjMtNDYyNi1iYWU2LTk2YTczMjMzNzMyMQ==",
            "Auth-Client-Version": "1.25.1",
            "Device-Name": "Tm9raWEgQzMy",
            "Installation-Id": "17E229B5-41B7-4F4D-B44A-C76559665E54",
            "Device-Operating-System": "TIRAMISU (33)",
            "Device-Model": "Nokia Nokia C32",
            "Auth-Client-Name": "android-app",
            "Device-Fingerprint": "3a3f05ba6c66de6a",
            "Device-Platform": "android",
            "Signature": "v1 MTcwODMyNTg5NjpKSjltTUVSZjNmMXhtMUNLWHEzOHR1U0RUdDQxQmNpYTo4V09jZTUrS0dNa21ZR0doSGNmbmlxVlR1R0RFbmZIUkRSd1h0RXJua0FzPQ==",
            "Content-Type": "application/json; charset=utf-8",
            "Content-Length": "77",
            "Host": "api.thecut.co",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/4.11.0"
        }, json={
            "grant_type": "password",
            "username": "surgbc@gmail.com",
            "password": "ca!kacut"
        })
        data = response.json()
        return data["access_token"]
    except Exception as e:
        print("Error fetching access token:", e)
        raise e

# Function to make API call with access token
def make_api_call(access_token, entry, round_number,record=None):
    if not record:
        try:

            response = requests.get(f"https://api.thecut.co/v2/search/barbers?latitude={entry['lat']}&longitude={entry['lon']}&keywords=", headers={
                "Authorization": f"Bearer {access_token}",
                "Auth-Client-Version": "1.25.1",
                "Device-Name": "Tm9raWEgQzMy",
                "Installation-Id": "17E229B5-41B7-4F4D-B44A-C76559665E54",
                "Device-Operating-System": "TIRAMISU (33)",
                "Device-Model": "Nokia Nokia C32",
                "Auth-Client-Name": "android-app",
                "Device-Fingerprint": "3a3f05ba6c66de6a",
                "Session-Id": "f822af9b4e3a61e0d5b71eacbca9c5a686fba9d2b968792e729a6138f4fde7e8122528f7230406f75ed335f6b822c732",
                "Device-Platform": "android",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Id": "65d2df444fd2435e639c4b43",
                "Signature": "v1 MTcwODMzNTg5NzprTFVKNmxjNFpiUzU4aXdUTFFsTENWQTFWNUlGSVFLMDpLQlhiand2bVpCeFppZmZieGFtYnd5bzh6aWp3c3FpSUU4ZHd6azViRHRrPQ=="
            })
            data = response.json()
            try:
                for thecutData in data:
                    ScrappedData.objects.create(
                        name = thecutData.get('keywords')[0],
                        inference_key = thecutData.get('keywords')[1],
                        response = thecutData,
                        round_number = round_number
                    )
            except Exception as err:
                print(err)
        except Exception as e:
            print("Error making API call:", e)
    else:
        try:
            # TODO: check on how are we getting a single record
            response = requests.get(f"https://api.thecut.co/v2/search/barbers?latitude={entry['lat']}&longitude={entry['lon']}&keywords=", headers={
                "Authorization": f"Bearer {access_token}",
                "Auth-Client-Version": "1.25.1",
                "Device-Name": "Tm9raWEgQzMy",
                "Installation-Id": "17E229B5-41B7-4F4D-B44A-C76559665E54",
                "Device-Operating-System": "TIRAMISU (33)",
                "Device-Model": "Nokia Nokia C32",
                "Auth-Client-Name": "android-app",
                "Device-Fingerprint": "3a3f05ba6c66de6a",
                "Session-Id": "f822af9b4e3a61e0d5b71eacbca9c5a686fba9d2b968792e729a6138f4fde7e8122528f7230406f75ed335f6b822c732",
                "Device-Platform": "android",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Id": "65d2df444fd2435e639c4b43",
                "Signature": "v1 MTcwODMzNTg5NzprTFVKNmxjNFpiUzU4aXdUTFFsTENWQTFWNUlGSVFLMDpLQlhiand2bVpCeFppZmZieGFtYnd5bzh6aWp3c3FpSUU4ZHd6azViRHRrPQ=="
            })
            data = response.json()
            try:
                # how will we retrieve the record for one
                if record:
                    check_data = ScrappedData.objects.filter(Q(name__icontains=record)|Q(inference_key__icontains=record))
                    if check_data.exists():
                        dataset = check_data.last()
                        for thecutData in data:
                            dataset.response = thecutData
                            dataset.round_number=round_number
                            dataset.save()
                        print("successfully updated a single record")
                    else:
                        for thecutData in data:
                            ScrappedData.objects.create(
                                name = thecutData.get('keywords')[0],
                                inference_key = thecutData.get('keywords')[1],
                                response = thecutData,
                                round_number = round_number
                            )
                        print("Successfully inserted a single record")
            except Exception as err:
                print(err)
        except Exception as e:
            print("Error making API call:", e)


def scrap_the_cut(round_number,record=None):
    try:
        # Get access token
        access_token = get_access_token()
        print({"accessToken": access_token})

        # Read JSON file
        json_filename = "boostedchatScrapper/spiders/helpers/jsons/town_coordinates.json"
        with open(json_filename, "r") as f:
            json_data = json.load(f)

        data = []
        for item, coords in json_data.items():
            location = coords.split(",")
            data.append({"name": item, "lat": location[0], "lon": location[1]})

        # Call API with access token for each entry
        for entry in data:
            print(entry)
            make_api_call(access_token, entry,round_number,record=record)
    except Exception as e:
        print("An error occurred:", e)

