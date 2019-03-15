# Rackspace AutoAI

We propose a predictive analytics tool for our customers

How to provide the OpenStack cloud a predictive analytic tool using using Automated ML. Currently GCP has AutoML that seems to only be for DeepLearning algorithms and even AWS does not seem to provide such capability. Let's empower our customers with Machine Learning without the hassle to understanding it.

## Reference Customer Description

* Joe is a marketing manager who has CSV files of churn data on his customers and he wants to know the likelihood
of a given customer leaving next month. He is fine with submitting a new test data file every month to get his results.

* Jody is an operations engineer who wants to predict machine failure. She has CSV time-series data for a few
devices and wants to predict the likelihood of a device failure every day using a REST API.

## Other resources

DataRobot: https://www.datarobot.com/

https://www.youtube.com/watch?v=ZChA63CpX5o 

https://www.youtube.com/watch?v=CgV2TJdrb7E

https://www.youtube.com/watch?v=cENIYiqJTNE

H2O DriverLess AI: http://docs.h2o.ai/?_ga=2.116087951.863179124.1548955277-433120363.1548805132#driverless-ai

https://www.youtube.com/watch?v=yzAhjinmdzk

https://www.youtube.com/watch?v=r1UbHG4Uw24

https://www.youtube.com/watch?v=niiibeHJtRo

Google AutoML: https://cloud.google.com/automl/

https://www.youtube.com/watch?v=kgxfdTh9lz0

https://www.youtube.com/watch?v=-zteIdpQ5UE


## Bootstrap the project

    $ virtualenv python=py3.6 auto-ai
    $ source <path-to-auto-ai-venv>/bin/activate
    $ cd <path-to-auto-ai-repo>
    $ pip install -r requirements.txt
    
### To start project's webserver:
 
    $ cd <path-to-auto-ai-repo>
    $ python manage.py runserver

   Then you can visit the entering page ag: http://127.0.0.1:5000/
