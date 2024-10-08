import requests
import json
import time
from datetime import datetime

# Konfigurasi
tokenBot = '7043239270:AAGxyI0mfQi1aAiGeHBabUXZ5c54Hysx0Vc'
chat_id = '-1002202267314'
nsq_stats_address = 'http://192.168.21.166:4151/stats?format=json'
thread_id = 2

# Daftar Channel
target_channel = {
    "event": [
        "coordinator", "coordinator-0#ephemeral", "coordinator-1#ephemeral",
        "coordinator-10#ephemeral", "coordinator-11#ephemeral", "coordinator-12#ephemeral",
        "coordinator-13#ephemeral", "coordinator-14#ephemeral", "coordinator-15#ephemeral",
        "coordinator-16#ephemeral", "coordinator-17#ephemeral", "coordinator-18#ephemeral",
        "coordinator-19#ephemeral", "coordinator-2#ephemeral", "coordinator-3#ephemeral",
        "coordinator-4#ephemeral", "coordinator-5#ephemeral", "coordinator-6#ephemeral",
        "coordinator-7#ephemeral", "coordinator-8#ephemeral", "coordinator-9#ephemeral",
        "extractor", "merger", "metric"
    ],
    "online-news": ["nsq-to-kafka-profiling", "nsq-to-nsq", "parser_ph"],
    "online-news-recovery": ["nsq-to-kafka-profiling", "nsq-to-nsq"],
    "result": ["storage"],
    "sender": ["error-content-v2#ephemeral", "immproducer"]
}

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{tokenBot}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'message_thread_id': thread_id
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response

def fetch_nsq_stats():
    try:
        response = requests.get(nsq_stats_address)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"Error while fetching data: {e}")
        return None

def monitor_channels():
    while True:
        data = fetch_nsq_stats()
        if data:
            missing_channels = {}
            zero_connection_channels = []
            for topic in data.get('topics', []):
                topic_name = topic.get('topic_name')
                if topic_name in target_channel:
                    found_channels = [channel.get('channel_name') for channel in topic.get('channels', [])]
                    missing = [channel for channel in target_channel[topic_name] if channel not in found_channels]
                    if missing:
                        missing_channels[topic_name] = missing

                    #ngecek koneksi yang ilang
                    for channel in topic.get('channels', []):
                        if channel.get('client_count', 0) == 0:
                            zero_connection_channels.append((topic_name, channel.get('channel_name')))
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # if data:
            # missing_channels = []
            # for topic in data.get('topics', []):
            #     if topic.get('topic_name') == 'event':
            #         found_channels = [channel.get('channel_name') for channel in topic.get('channels', [])]
            #         missing_channels = [channel for channel in expected_channels if channel not in found_channels]
            #         break

            if missing_channels:
                alert_message = f"Ada Channel Yang Tolong dicek \n Channel yang ilang : "
                for topic_name, channels in missing_channels.items():
                    alert_message += f"Topics '{topic_name}': {', '.join(channels)}\n"
                print(alert_message)
                send_telegram_message(alert_message)

            if zero_connection_channels:
                for topic_name, channel_name in zero_connection_channels:
                    alert_message = f"Alert: Topic '{topic_name}' saat ini connection '{channel_name}' 0 at {current_time}"
                    print(alert_message)
                    send_telegram_message(alert_message)
                    
            if not missing_channels and not zero_connection_channels:
                print(f"Semua Channel Run Well (OK) timestamp: {current_time}")
                
         time.sleep(360)

if __name__ == "__main__":
    monitor_channels()
