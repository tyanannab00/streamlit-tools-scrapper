import requests
import json
import time
import nsq
from telegram import Bot

# Konfigurasi
tokenBot = '7043239270:AAGxyI0mfQi1aAiGeHBabUXZ5c54Hysx0Vc'
chat_id = '-1002202267314'
thread_id = 2
nsq_address = 'http://192.168.21.200:4161'
target_hostnames = [
    'master.kubernetes.test',
    'worker01.kubernetes.test',
    'worker02.kubernetes.test',
    'worker03.kubernetes.test',
    'worker04.kubernetes.test'
]
target_broadcast_addresses = [
    '192.168.21.110',
    '192.168.21.84',
    '192.168.21.85',
    '192.168.21.34',
    '192.168.21.35'
]

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
    if response.status_code != 200:
        print(f"Gagal: {response.status_code} - {response.text}")
    return response

def check_nsqd_hosts(): #tambahin parameter test_mode=False buat test alert
    try:
        response = requests.get(f"{nsq_address}/nodes")
        if response.status_code == 200:
            data = response.json()
            print(f"Response from nsqlookupd: {data}")
            hosts = data.get('producers', [])
            # if test_mode:
            #     hosts = [host for host in hosts if host.get('hostname') != 'worker02.kubernetes.test']
            # return hosts
           
            filtered_hosts = [host for host in hosts if host.get('hostname') in target_hostnames or host.get('broadcast_address') in target_broadcast_addresses]
            return filtered_hosts
        else:
            print(f"Failed to fetch data from nsqlookupd: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error while checking nsqd hosts: {e}")
        return []
    
def find_missing_hosts(current_hosts, target_hostnames, target_broadcast_addresses):
    current_hostnames = [host.get('hostname') for host in current_hosts]
    current_broadcast_addresses = [host.get('broadcast_address') for host in current_hosts]

    missing_hostnames = [hostname for hostname in target_hostnames if hostname not in current_hostnames]
    missing_broadcast_addresses = [address for address in target_broadcast_addresses if address not in current_broadcast_addresses]

    return missing_hostnames, missing_broadcast_addresses


def monitor_nsqd(): #pakein parameter test_mode=False buat test alert
    # while True:
    #     nsqd_hosts = check_nsqd_hosts()
    #     if not nsqd_hosts:
    #         print("Gaada host yang ketemu wak, cek telegram")  # Debug print
    #         send_telegram_message("Alert: No nsqd hosts are currently available!")
    #     else:
    #         print(f"NSQd hosts found: {len(nsqd_hosts)} - Hostnames: {[host.get('hostname') for host in nsqd_hosts]}, Broadcast Addresses: {[host.get('broadcast_address') for host in nsqd_hosts]}")
    

    while True:
        nsqd_hosts = check_nsqd_hosts() #tambahin test_mode=test_mode buat test alert
        missing_hostnames, missing_broadcast_addresses = find_missing_hosts(nsqd_hosts, target_hostnames, target_broadcast_addresses)
        
        if missing_hostnames or missing_broadcast_addresses:
            missing_details = ""
            if missing_hostnames:
                missing_details += f"Missing Hostnames: {', '.join(missing_hostnames)}"
            if missing_broadcast_addresses:
                if missing_details:
                    missing_details += " | "
                missing_details += f"Missing Broadcast Addresses: {', '.join(missing_broadcast_addresses)}"
            alert_message = f"Ada Nodes yang ilang Wak !! \n\n{missing_details}"
            print(alert_message)  # Debug print
            send_telegram_message(alert_message)
        else:
            print(f"All NSQd hosts are available - Hostnames: {[host.get('hostname') for host in nsqd_hosts]}, Broadcast Addresses: {[host.get('broadcast_address') for host in nsqd_hosts]}")
        
        time.sleep(60)


if __name__ == "__main__":
    monitor_nsqd() #set test_mode jadi true buat test alert
