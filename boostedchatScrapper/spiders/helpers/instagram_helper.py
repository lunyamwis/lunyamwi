from instagrapi import Client


def extract_inbox_data(data):
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


def fetch_pending_inbox(session_id):
    client = Client()
    client.login_by_sessionid(sessionid=session_id)

    inbox = client.private_request("direct_v2/pending_inbox/",params = {
        'visual_message_return_type': 'unseen',
        'eb_device_id': '0',
        'no_pending_badge': 'true',
        'persistentBadging': 'true',
        'push_disabled': 'true',
        'is_prefetching': 'false',
        'request_session_id': client.request_id,
        },)
    inbox_dataset = extract_inbox_data(inbox)
    return inbox_dataset
    
def approve_inbox_requests(session_id,inbox_dataset):
    client = Client()
    client.login_by_sessionid(sessionid=session_id)
    inbox_dataset = fetch_pending_inbox(session_id=session_id)
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

def send_direct_answer( session_id, thread_id, message):
    client = Client()
    client.login_by_sessionid(sessionid=session_id)
    client.direct_answer(thread_id,message)