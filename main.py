import requests
import json
import time
import random

def read_query_ids(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def send_graphql_request(query_id):
    url = "https://backend.red-coin.site/api/graphql"
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://red-coin.site',
        'referer': 'https://red-coin.site/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }
    
    payload = {
        "variables": {
            "initData": query_id,
            "friendCode": None
        },
        "query": """
        mutation ($initData: String, $friendCode: String) {
          initGame(initData: $initData, friendCode: $friendCode) {
            user {
              id
              telegram_id
              name
              token
            }
          }
        }
        """
    }
    
    response = requests.post(url, headers=headers, json=payload)
    try:
        user_data = response.json()['data']['initGame']['user']
        return user_data, user_data.get('token')
    except (KeyError, TypeError):
        return None, None

def send_adsgram_request(telegram_id):
    url = f"https://backend.red-coin.site/api/adsgram?userId={telegram_id}&secret=6310"
    headers = {
        'accept': '*/*',
        'origin': 'https://red-coin.site',
        'referer': 'https://red-coin.site/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except requests.RequestException:
        return None

def start_farming(token):
    url = "https://backend.red-coin.site/api/graphql"
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://red-coin.site',
        'referer': 'https://red-coin.site/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36',
        'token': token
    }
    payload = {
        "variables": {},
        "query": """
        mutation ($is_vtono_boost: Boolean, $ton_transaction_unique_boost: String) {
          startFarming(
            is_vtono_boost: $is_vtono_boost
            ton_transaction_unique_boost: $ton_transaction_unique_boost
          ) {
            unique
            wait_time
            end_timer
            earn_per_second
            current_balance {
              tonomo
              vTono
              __typename
            }
            __typename
          }
        }
        """
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

def get_tasks():
    url = "https://backend.red-coin.site/api/graphql"
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://red-coin.site',
        'referer': 'https://red-coin.site/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }
    payload = {
        "operationName": "getTasks",
        "variables": {},
        "query": "mutation getTasks {\n  loadTasks {\n    tasks {\n      type\n      list {\n        id\n      }\n    }\n  }\n}"
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    try:
        # Check if the response is valid and contains 'data'
        response_json = response.json()
        data = response_json.get('data', {}).get('loadTasks', {})
        
        # Initialize an empty list for task ids
        task_ids = []
        
        # Loop through each category in 'tasks' and extract 'id' from each task in 'list'
        for category in data.get('tasks', []):
            for task in category.get('list', []):
                task_ids.append(task.get('id'))
        
        # If there are tasks in 'checkin', extract 'id' from them as well
        for checkin_task in data.get('checkin', []):
            task_ids.append(checkin_task.get('id'))

        return task_ids
    
    except (KeyError, TypeError, AttributeError):
        # If any error occurs, return an empty list
        return []

def claim_task(telegram_id, task_id):
    url = "https://backend.red-coin.site/api/graphql"
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'origin': 'https://red-coin.site',
        'referer': 'https://red-coin.site/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'
    }
    payload = {
        "variables": {"tasks_id": task_id},
        "query": "mutation ($tasks_id: ID) {\n  claimTasks(tasks_id: $tasks_id) {\n    amount\n    tonomo\n  }\n}"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    query_ids = read_query_ids("datas.txt")
    tasks = get_tasks()
    for query_id in query_ids:
        user_data, token = send_graphql_request(query_id)
        if user_data and token:
            telegram_id = user_data['telegram_id']
            name = user_data['name']
            print(f"User: {name}, Telegram ID: {telegram_id}, Token: {token}")

                        
            farming_response = start_farming(token)
            print("Farming Response:", farming_response)

            tasks = get_tasks()


            for task_id in tasks:
                claim_response = claim_task(telegram_id, task_id)
                print(f"Claim Response for Task {task_id}:", claim_response)


            
            for _ in range(10):
                adsgram_response = send_adsgram_request(telegram_id)
                
                if adsgram_response and not adsgram_response.get("success", False):
                    print("Ads limit reached or error encountered. Stopping further processing.")
                    break
                
                print("AdsGram Response:", adsgram_response)
        else:
            print(f"Error processing query ID: {query_id}")
