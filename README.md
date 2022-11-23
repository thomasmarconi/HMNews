# HMNews
COP 4521 groupId=19 Thomas Marconi - tcm19, Jack Hayes - jth19e
# Homework assignment 1
How does "curl hmnews.xyz" work? It seems that there are two
different commands of what's going on here. The first command
"curl hmnews.xyz" is really "curl http://hmnews.xyz". This 
firstly goes to some dns resolver to see what IP is 
associated with hmnews.xyz. It gets that 143.198.176.35 is 
the IP and sends a request to that IP address. It gets a 
connection on port 80. Nginx redirects this port to 443 
which is https. This is where the SSL certificates are
exchanged and compared to see if the client and server
are legitimate. To do this it get's the location of the SSL
certificate on the server and does a series of TLS handshakes
to verify that the server certificate is legitimate. Now that
it is connected, NGinx serves it the "/" route html page. 
How it knows what is stored in that route is the flask app. The 
flask app which is constantly being run by gunicorn returns
on a request to that route an html template that is stored on
the server which has been defined in the python code to 
return whenever a call to that route is issued. The text defined
in the html template is now displayed to the terminal. The curl
command then closes the connection and all is well. 

On a similar note, if "curl https://hmnews.xyz" is the command
pretty much all is the same except that it's inital connection 
is on port 443 instead of 80 and there is no redirection. The 
SSL certificate is verified and then the rest of what is written
above happens.

# Security
One of the first steps in making our website more secure was by adding passwordless ssh. This makes it so that the machine is only accessible through ssh from either my or Thomas’ devices. We also implemented https into our server and routed all http traffic through https. Using https will make our website less susceptible to man in the middle attacks and passive attacks like eavesdropping on communications happening on the site. Another piece of security was using ubuntu’s ufw to only allow incoming traffic from ngnix and ssh. The final piece of security is Auth0 which prevents different types of attacks by adding a login page before using the site, restricting access from unwanted users.

# Upgrades And Updates
Upgrades and Updates: The steps we will take to update the server will be as follows: 1) create a backup of server with outdated components 2) Shut down the server 3) apt update and apt upgrade 4) make sure server is working correctly, if not restore from backup. We have not yet, but further down the line will create a script to run and help automate the process a little. Updates can be done whenever a component receives a new version.
Changed after midterm: unattended-upgrades package install and enabled to handle auto updating

# Config Files
Copies of all config files are in /home/gitRepo/hmnews/config folder
actual ssh config path: /etc/ssh/sshd_config
actual nginx config path: /etc/nginx/nginx.conf
actual gunicorn config path: /etc/systemd/system/hmnews.service
actual auth0 config path: /home/gitRepo/hmnews/.env
actual dns setting path: /home/gitRepo/hmnews/config/dnsRecords.txt

# Ease of Installation of the software
To get our repo running on your machine you need to install and set up a few things. Nginx, gunicorn, flask, certbot, auth0, ufw, and crontab all need to be set up. There are two main tutorials for helping with these: https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-22-04 and https://auth0.com/docs/quickstart/webapp/python/interactive. We'll start with cloning the repo to your server. Cd to your desired directory and run the command git clone https://gitlab.com/thomasmarconi/hmnews.git. Authenticate with your git credentials and then cd into hmnews. Next you should have a lot of the required dependencies for things in the venv folder so you can hop right into configuring gunicorn. Run "sudo apt update sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools". Then go ahead and hop into the virtual environment with "source venv/bin/activate" All of these next packages should be installed but we'll run the commands just in case. Run "pip install wheel" and "pip install gunicorn flask". Let's just quickly to configuring your firewall. Assuming it's off go ahead and allow your desired ports with "sudo ufw allow  "portNum"". You at least need to do "sudo ufw allow 80", "sudo ufw allow 22" and "sudo ufw allow 443". Then do "sudo ufw enable". Jumping back to gunicorn go ahead and run "gunicorn --bind 0.0.0.0:5000 wsgi:app" Now we need to make a systemd service unit file. We'll do this by sudo nano /etc/systemd/system/ "yourProject".service. In this file write: 

[Unit]
Description=Gunicorn instance to serve hmnews
After=network.target

[Service]
User="yourUser"
Group=www-data
WorkingDirectory= "absPathToRepo"
Environment="PATH= "absPathToRepo"/venv/bin"
ExecStart= "absPathToRepo"/venv/bin/gunicorn --workers 3 --bind unix:hmnews.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target

Save and exit the file. Then run "sudo systemctl start  "yourProject"" and "sudo systemctl enable  "yourProject"". Check the status with "sudo systemctl status  "yourProject"" Next to configure nginx create a file by "sudo nano /etc/nginx/sites-available/ "yourSite"" In this file write: 

server {
	add_header Content-Security-Policy "default-src 'self'; img-src 'self';" always;

	add_header Strict-Transport-Security 'max-age=31536000; includeSubDomains; preload';

	add_header X-XSS-Protection "1; mode=block";

	add_header X-Frame-Options "SAMEORIGIN";

	add_header X-Content-Type-Options nosniff;

	add_header Referrer-Policy "strict-origin";

	add_header Permissions-Policy "geolocation=(),midi=(),sync-xhr=(),microphone=(),camera=(),magnetometer=(),gyroscope=(),fullscreen=(self),payment=()";

	server_name  "yourUrl www."yourUrl";

	location / {
		include proxy_params;
		proxy_pass http://unix:"absPathToRepo"/hmnews/hmnews.sock;
	}

	location /images/ {
		root  "absPathToRepo "/hmnews;
	}
}
server {
	listen 80;

	listen [::]:80;

	server_name  "yourDomain " www. "yourDomain";

	return 301 https:// "yourDomain"$request_uri;

}

Save and exit this file. Then like the file to site-enabled with "sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled" and you can text it for syntax error with "sudo nginx -t". Start nginx with "sudo systemctl restart nginx". Now to configure certbot. Run "sudo apt install python3-certbot-nginx" and then "sudo certbot --nginx -d your_domain -d www.your_domain" This should give you SSL certificates and it'll update your nginx conf file. Now if you're not in your virtual environment go back into that with "source venv/bin/activate". Run "pip install -r requirements.txt" Now you'll have to change the .env file in the repo with the information with your Auth0 program. That will look like:
# 📁 .env -----

AUTH0_CLIENT_ID=YOUR_CLIENT_ID
AUTH0_CLIENT_SECRET=YOUR_CLIENT_SECRET
AUTH0_DOMAIN=YOUR_DOMAIN
APP_SECRET_KEY=

and Generate a string for APP_SECRET_KEY using openssl rand -hex 32 from your shell. The other values can be found on your auth0 application settings page. On this page you should set the Application Login Uri to https:// "yourDomain"/login. You allowed callback URLs https:// "yourDomain"/callback and your Allowed Logout URL to https:// "yourDomain"/. You should save those settings on the website. Then in your server you need to make a few changed to  run the reload.sh script on server. Replace where it says hmnews with  "yourProject". Then run the script and you should be able to access the website through https:// "yourDomain". If there are issues you can run sudo systemctl status  "yourProject".

To setup crontab run sudo crontab -e and write these lines in the file:

0 * * * * systemctl stop  "yourProject"

0 * * * * /usr/bin/python3  "absPathToRepo"/hmnews/init_db.py

0 * * * * systemctl daemon-reload

0 * * * * systemctl start  "yourProject"

0 * * * * systemctl enable  "yourProject"

0 * * * * systemctl start  "yourProject"

