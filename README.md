# Fetch Rewards #
## Data Engineering Take Home: ETL off a SQS Qeueue ##
## Wills Mckenna's Answer ##


This was my answer to the challenge presented to me for the interview platform engineering take home. To run, first run make start in the data-engineering-take-home project. 

This will spin up the two resources, namely the queue and the postgres database as local docker images. 

Then navigate to the root folder of my project (deliverable) and after running 

pip install -r requirements.txt

to add the needed packages (mainly psycopg2 binary) you can run the full program with 

python main.py

This runs the program locally and communicates with both docker containers through boto3 sqs on the queue end and psycopg2 on the postrgres side. 

I transformed the data (i.e the masking) through using a public/private key RSA algorithm so that duplicate values can be spotted, as long as the keys
are kept track of.

## What I would have done with more time

I would have further extracted code and refactored to make the functions of the program better seperated, i.e have seperate files for reading (just the sqs methods), transforming (just the rsa manipulation methods), loading (just the database communication and loading), and then a client/controller file that was in charge of running this process. 

Although I have a few error checks, I would have liked to go through this and add several more try/catch statements, particular when connecting to the resources, so that we can know if there is an issue on the backend in this regard. For example adding in more try/catch when connecting to the database via psycopg. 

Another big missing piece would be to refactor this program to be essentially a listener/web server, and host this on a docker container, so that it could be part of the virtual distributed system that is already in place with the queue and the database. These three docker containers would be able to talk to each other. Then, if more messages were sent to the cue, this listener resource could immediateley (or say, after the cue filled back up to 100) catch that and start extracting, transforming, and loading to the postgres database. 

Refactoring in this way to expand on this distributed system would make scalability possible, so that we could increase number of docker containers or size of the servers (whether that be ec2s or k8s clusters). You could scale these resources up and down depending on the size and load of the queue, for instance if its a particularly busy time with users signing in.  

