#!/bin/python3
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
import time
import os

# Load configuration from YAML
with open("mailer.conf", "r") as file:
    config = yaml.safe_load(file)

class LogHandler(FileSystemEventHandler):
    def __init__(self, file_path, target, application, mailgun_config):
        self.file_path = file_path
        self.target = target
        self.application = application
        self.mailgun_config = mailgun_config
        self.last_line = ""

    def on_modified(self, event):
        if event.src_path == self.file_path:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                new_line = lines[-1].strip() if lines else ""
                if new_line != self.last_line:
                    ip = new_line.split()[0]
                    endpoint = new_line.split('"')[1].split()[1]
                    #Do not send mail for admin access to XSSHunter
                    if endpoint.startswith("/admin") or endpoint.startswith("/api") or endpoint.startswith("/screenshots"):
                        print("Ignore admin access")
                    else:
                        print(new_line)
                        body = f"New request on {self.application} at {self.target} : {ip}"
                        subject = f"[Work] {self.application} received a sollicitation"
                        print(body)
                        response = self.send_simple_message(body, subject)
                        if response.status_code == 200:
                            print(f"Email sent successfully for {self.target}")
                        else:
                            print(f"Failed to send email for {self.target}: {response.status_code} - {response.text}")

    def send_simple_message(self, body, subject):
        mailgun_url =  "https://api.mailgun.net/v3/"+self.mailgun_config['domain']+".mailgun.org/messages"
        return requests.post(
  		mailgun_url,
  		auth=("api", self.mailgun_config['api_key']),
  		data={"from": f"<{self.mailgun_config['endpoint']}>",
  			"to": [{self.mailgun_config['recipient']}],
  			"subject": subject,
  			"text": body})


    def send_email(self, log_entry):
        data = {
            "from": f"Log Monitor <monitor@{self.mailgun_config['endpoint']}>",
            "to": self.mailgun_config['recipient'],
            "subject": f"New request on {self.target}",
            "text": f"Log entry: {log_entry}"
        }
        response = requests.post(
            self.mailgun_config['endpoint'],
            auth=("api", self.mailgun_config['api_key']),
            data=data
        )
        if response.status_code == 200:
            print(f"Email sent successfully for {self.target}")
        else:
            print(f"Failed to send email for {self.target}: {response.status_code} - {response.text}")
            self.mailgun_config['endpoint'],
            auth=("api", self.mailgun_config['api_key']),
            data=data

# Set up observers for each log file
observers = []
for log_config in config['logs']:
    if not os.path.isfile(log_config['path']):
        print(f"Error: {log_config['path']} file not found.")
        exit()
    handler = LogHandler(log_config['path'], log_config['target'], log_config['application'], config['mailgun'])
    observer = Observer()
    observer.schedule(handler, path=os.path.dirname(log_config['path']), recursive=False)
    observers.append(observer)


# Start observing
try:
    for observer in observers:
        observer.start()
    print("Log monitoring started.")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping log monitoring.")
    for observer in observers:
        observer.stop()
for observer in observers:
    observer.join()
