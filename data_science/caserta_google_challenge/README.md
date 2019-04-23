# Caserta Google Challenge Project

## Synopsis

Project to test knowledge/skills on GCP, Json, CSV, SQL, etc.

Read current crypto data from CoinMarketCap API, convert it, up

## Background

### Solution

* Simple Python script that reads CAP data, converts it to CSV and writes it to a file.
    * Used Python 3.x in this script because of unicode issue reading/parsing JSON. And it appears that Google 
now supports 3.x (since I last used Python on GCP it did not).
    * Trouble with using field '24hr_volume_usd' as BigQuery key -- simple solution is to modify it upon import.
    * Used Python *requests* and *csv* libraries to perform http upload & csv writing, respectively.
* File was then uploaded using the console to GCP Cloud Storage and is available publicly 
[here](https://console.cloud.google.com/storage/browser/caserta_gcp_challenge?project=sage-webbing-197320)
    * Needed to get into GCP IAM and add viewer role and assign to the storage bucket.
* This file was then imported into BigQuery
    * Initialization took at least 30 minutes!
* DataLab Portion
    * Initialization took 10 minutes (getting AppEngine access)
    * Setup *gcloud* utils manually (could maybe have used Mac *brew* if had more time to experiment)
    * *gcloud* setup worked well after manually altering PATH (very clean vs. AWS!)
    * Created data lab instance *caserta-challenge-datalab* (Slooooow again)
    * Passphrase clue for this datalab instance: usual + 'ssh'
    * Have local instance working at localhost:8081
    * Datalab reconnect command is: `datalab connect caserta-challeng-datalab`.
    * Cleanup after done with Datalab instance (so not billed):
        * `datalab delete --delete-disk caserta-challeng-datalab`
        * `gcloud compute firewall-rules delete datalab-network-allow-ssh`
        * `gcloud compute networks delete datalab-network`
        * `gcloud source repos delete datalab-notebooks`
    
* To pull iPython notebook: `gcloud compute scp --recurse \
datalab@instance-name:/mnt/disks/datalab-pd/content/datalab/notebooks instance-name-notebooks`

### Relevant Notebook Examples
* Cloud storage: `/datalab/docs/tutorials/Storage/Storage APIs.ipynb`
* BigQuery: `/datalab/docs/tutorials/BigQuery/BigQuery/BigQuery APIs.ipynb`
