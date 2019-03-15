---

title: Data / Analytics Documentation
short_desc: designs & specifications relating to architectures, designs, implementations, models & data related to performing analyticss on the Trebuchet Platform.
<optional_short_description>

keywords: ['Analytics', 'OLAP', 'Data', 'Streaming', 'Data Map']

layout: page

featured: images/pic03.jpg

audience: []

---

# Data Mapping Project

## Goals

* Create an inventory of all data that is generated and stored by the Trebuchet platform
* Develop an understanding of how this data flows through all Trebuchet systems
* Understand current status of data retention including backup processes (if any) and retention periods

## Deliverables

* Medium to high-level summary of data flowing into, at rest, and out of each system service
**Service name, source, type, purpose, retention policy, backup plan, audit, outside access method (for Data Science team)
* System Architectural / Data Flow Diagram

## Challenges

* Capturing what data and related services are currently in place, in a temporary state, or planned for the future.
* Other parts of the platform/infrastructure are concurrently being developed so much is in a state of flux and not recently documented.

## Contacts

People who are the source of important project-level information.

| Project Area | Team Lead | Alternate Contact | Status |
------------ | --------- | ----------------- | ------ |
| Infrastructure | Brandon Cole | | Email sent 8/21 |
| CI/CD (deployment) |Jeff French | | Email sent 8/23 |
| LME | Ross Lonstein | Jeff Roberts? | Very productive zoom on 8/23, suggestions for convergence emailed |
| App Security | Patrick Barker | or Josh Rendek | Documented |
| App Developer Services | Allen Hurff | or Leo or Josh Leeder | May have part in prior email |
| Client Engineering? | Dan Stover | | |

## Contact Geo Location

| Name | Location | Core Work Day |
| ---- | -------- | ------------- |
| Jeff Roberts | Los Angeles, CA | PST |
| Patrick Barker | Denver, CO | |
| David Deal | San Diego, CA | PST |
| Arti Garg | Hayward, CA | PST |
| Jon Powell | San Diego, CA | 9am-5pm PST |
| Ross Lonstein | Woodstock, NY | EST |

## Architectural Diagram


## LME (Logging, Metrics & Eventing) Diagrams

Need to get diagrams...under development.

* Logs DataFlow
* Metrics Data Flow
* Elastic Search Kibana OAuth Diagrams
* LME Gatekeeper Logs Query API
* LME Unified Architecture Diagram (out of date?)

## Miscellaneous

* [Gatekeeper YAML](https://scm.trebuchetdev.com/lme/gatekeeper/blob/master/docs/swagger/gatekeeper.yaml)
* Logging JSON
  * [Typical](https://scm.trebuchetdev.com/lme/elasticsearch-cluster/blob/master/deployment/charts/elasticsearch-cluster/index-templates/log-message-example-filebeat-2.json)
  * [Ugly](https://scm.trebuchetdev.com/lme/elasticsearch-cluster/blob/master/deployment/charts/elasticsearch-cluster/index-templates/log-message-example-filebeat-ugly.json)

## Data Map

Service Name | Data Category | Description | Data Science Opportunities | Notes | Format | Outside Access Method | Retention Policy
------------ | ------------- | ----------- | -------------------------- | ----- | ------ | --------------------- | ----------------
Auth ("Hydra") | Client (Authentication) | https://scm.trebuchetdev.com/platform-external/hydra | who's accessing what, token allocations, then throw alerts, then don't need auth (want keys to live forever) | Aurora | | API bulk-headed by tenant & policy engine | 
| Policy (Authorization) | https://scm.trebuchetdev.com/platform-external/ladon | policy analysis (future) | | Aurora | | API bulk-headed by tenant & policy engine	| 
| K8 logs | Event stream thru stdout by pod? | | | log lines | |
Secrets ("Tetra") | Secrets | app-level key-value store, resources; DRN | (https://scm.trebuchetdev.com/appsec/tetra) | who's accessing what | Aurora | API bulk-headed by tenant & policy engine | 
| Configuration | | Aurora | | API bulk-headed by tenant & policy engine | | 
API-Gateway | Registered Services? | Proxy service sitting in front of all services [https://getkong.org/](https://scm.trebuchetdev.com/platform-dockerfiles/kong) | Every request from user comes thru here (opportunities for logging) Kong provides common services, full call, called-by map available; available on control plane and also for user | Postgres, 1 gateway/cust | | API call same as Auth??? |
| Audit logs | Event stream, would like examples | Upcoming | | | | 
IDP | User (same as Client?) | Part of Hydra | System of services: translates identities�outward identities such as Google, external gitlab... into a DRN | Postgres | | |
VMS (Vulnerability Mgt System) | Reports? | (https://scm.trebuchetdev.com/appsec/vms) | Scan registry of K8 / Docker containers before deploy, alert if does not meet security threshold; produces report which would be minable | Postgres | | |
Kampe/Talos | Malicious events | 1 per customer, push to event stream? https://scm.trebuchetdev.com/appsec/kampe | Sit in front of public domain website, siphons out malicious attacks, sanitizing requests | | | |
LME | API REST Gateway | Queryable using meta-parameters (default):  A) maxRecords: max records (100), B) index: Elastic Search index name (filebeat), C) sort: returned result order asc/desc (asc) | a) namespace, b) customerID, c) containerID, d) containerName, e) serviceserviceName, f) podName, g) timeRange - encoded, h) hostname, i) message - values are comma delimited list of keywords
| | | | |


## To Do:

* Ensure LME S3 emitter is working and has correct schema/directory structure for partitioning, etc.
* Look [here](https://kibana-control1.dev.datapipe.io) \(for logs & formatting\)
* Process Gatekeeper YAML for all tags with x: to get all possible field values?

### Questions:

## Glossary

* DSR: graph of DRN's (coming soon)
* DRN = DataPipe Resource Name
* drn:1:us-west:iam:clients/myclient
* drn:\<tenantID\>:\<location\>:\<service\>:\<path\>
* LME: Logging & Metrics
* OAS: [Open API Specification](https://en.wikipedia.org/wiki/OpenAPI_Specification) , allows YAML specification, generation of REST API's

## Miscellaneous Notes

### Logical Data Streams

* Logs (from stdout, all services)
* Events (going to Kafka)
* Telegraphic (measurements, going to InfluxDB)

LME

* Data Collection backbone
