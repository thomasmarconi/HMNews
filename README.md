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

# Config Files
Copies of all config files are in /home/gitRepo/hmnews/config folder
actual ssh config path: /etc/ssh/sshd_config
actual nginx config path: /etc/nginx/nginx.conf
actual gunicorn config path: /etc/systemd/system/hmnews.service
actual auth0 config path: /home/gitRepo/hmnews/.env
actual dns setting path: /home/gitRepo/hmnews/config/dnsRecords.txt


