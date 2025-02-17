# Hunter Monitor

![alt text](resources/hunterMonitor_logo.png)

Hunter Monitor: Never miss again a ping back.

# Installation 

- Rename mailer.conf.template to mailer.conf
- Edit mailer.conf with your mailgun account (it's free)
- To avoid to be tagged as spam, use your domain as sender. To do it add domain in mailgun, then go to domain settings > DNS record and add them to your dns configuration.
- Add your server ip in https://app.mailgun.com/settings/ip-access-management to whitelist it (miss this step can be time consumming....)


Add one user to logusers group and edit /etc/nginx/nginx.conf to have the following line :
user www-data logusers;

for each virtualhost you want to monitor add the following line in your nginx conf

access_log /var/log/nginx/<name_of_the_file>.log;

```bash
cd hunterMonitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 /opt/hunterMonitor/hunterMonitor.py
```

To run it as a service 
- Edit the user in the  hunterMonitor.service 
- Edit the hunterMonitor location 

```bash
sudo cp hunterMonitor.service  /etc/systemd/system/
```