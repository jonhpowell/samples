---

title: Cloud Vendor Feature Mapping Matrix
short_desc: Compares most popular cloud PaaS and Iass offerings in the context of DataPipe's Trebuchet project
keywords: ['Cloud', 'Vendor', 'Comparison', 'PaaS', 'IaaS']

layout: page

featured: images/pic03.jpg

audience: 

---

# Introduction

Part of our product development is walking the fine line between utilizing major cloud vendor \(AWS, Azure & GCP\) features yet avoiding lock-in.

This page is intended to be a one-stop resource for general guidance for comparing vendor offerings to maximize our use of off-the-shelf technology yet be able to move our products with minimal effort between vendors.

# Compute
| Feature | Category | Sub-Category | Amazon Web Services Offering | Azure Offering | Google Cloud Offering |
| ------- | -------- | ------------ | ---------------------------- | -------------- | --------------------- |
| Compute | | | | | |
| | VM's | | | Compute Engine: fast boot, SSD or HD
| | Containers | | EC2 Container Service | | Container Engine
| | Nodes	| | [EC2](https://aws.amazon.com/ec2/?nc2=h_m1): secure, scalable, elastic | | [App Engine](https://cloud.google.com/appengine/): 
Storage	| | | | |
| | Object / Blob	Directory/file-based | S3: cheap file storage with 11 9's of reliability | [Data Lake Storage](https://azure.microsoft.com/en-us/blog/the-intelligent-data-lake/): HDFS-based � essential unlimited capacity (# objects, object size) | Cloud Storage: cheap file storage with 11 9's of reliability
| | NoSQL	Document or key-value based | DynamoDB: single-digit msec reads for key-value or document stores, fully managed, most popular NoSQL DB, fairly expensive | DocumentDB | * Bigtable: fairly expensive * Datastore: for webscale
| | Relational (OLTP) | | Aurora: faster, cheaper MySQL and PostgreSQL-compatible DB, fully managed. Limits: 32 vCPUs, 244GiB memory storage up to 64TB | AzureSQL | * Spanner: infinite-scale RDBMS with sub 10 msec read access *Cloud SQL: MySQL & PostgreSQL (you manage)
| | | RDS	Microsoft SQL Server, Oracle, MySQL, MarieDB, PostgreSQL | | Microsoft SQL Server, 
| |  Analytics (OLAP) | Huge scale, managed, VERY reliable (11 9's?) | 1) Athena: columnar, SQL-based engine that maintains metadata to efficiently query S3 data sources, integrates with Glue for ETL & discovery; [Tuning Tips](https://aws.amazon.com/blogs/big-data/top-10-performance-tuning-tips-for-amazon-athena/), 2) Redshift: relational, fully managed analytics DB a) Redshift Spectrum: SQL queries on S3 in data formats you already use, including CSV, TSV, Parquet, Sequence, and RCFile. | * [Data Lake Analytics](https://azure.microsoft.com/en-us/blog/the-intelligent-data-lake/): analyze data lake datasets (serverless), Python interface, U-SQL for queries, billed in "[Analytics Hours](https://azure.microsoft.com/en-us/pricing/details/data-lake-analytics/)." * HDInsight: Hadoop infrastructure, Kafka & Spark, scalable R envrionment, Jupyter notebook | [BigQuery](https://cloud.google.com/bigquery/): petabyte-scale columnar DB
| Stream Processing | | | | |
| | Large scale | | Datapipeline: windowed batch data processing framework that stores to S3, DynamoDB, RDS or EMR | [Stream Analytics](https://azure.microsoft.com/en-us/services/stream-analytics/): use Streaming Analytics Query Language, | [DataFlow](https://cloud.google.com/dataflow/): 
| Messaging | | | | |
| | PaaS | | SQS: simple, scalable, best-effort ordering, at least once delivery queuing service | | [PubSub](https://cloud.google.com/pubsub/)
| Serverless | | | | |
| | | Lambda (not yet robust) | Cloud Functions | [Cloud Functions](https://cloud.google.com/functions/)
| IaaS | | | | |
| | Managed Hadoop, Spark | | EMR: | | [Dataproc](https://cloud.google.com/dataproc/): 
Miscellaneous | | | | |
| | Integration | ETL | 1) [Glue](https://aws.amazon.com/glue/): fully-managed, Spark-based ETL service that discovers schemas and allows efficient searching & querying, auto-generates Python code; [use document](http://docs.aws.amazon.com/athena/latest/ug/athena-ug.pdf), 2) *Firehose* : integrates buffering, transform functions, encryption and output to S3,Redshift, or Elasticsearch Service (near realtime based on window time)
| | API Proxy | | API Gateway: allows exposing REST services to AWS components to outside consumers, managed & scalable | |
| | Orchestration	| | Step Functions | | 
| | Visualization	| | Quicksite: integrated tool | HDInsight? |
| | Financial / Budget / Spend | | Finance: cost explorer, budgets, reports to watch spend | | 
| | Logging | | CloudTrail: tracks account access & usage for auditing etc. | | Stackdriver: integrated logging solution
| | Analytics | Notebook | | [Datalab](https://cloud.google.com/datalab/): 
| | Data Preparation | | | [DataPrep](https://cloud.google.com/dataprep/): 
| | Machine Learning | Offerings | | | [ML Platform](https://cloud.google.com/ml-engine/), jobs, NLP, translation, vision, video intelligence, 
| | Language | Python | Boto API allows access to AWS services/instances | |

