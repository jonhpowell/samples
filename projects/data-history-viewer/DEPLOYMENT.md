# Deployment Steps for Trebuchet Applications (Rough Draft)

This document attempts to outline the general steps to deploy an application on a Trebuchet Kubernetes 
cluster. Steps are suggested that should result in a robust, scalable application residing on one of our 
Trebuchet cluster environments, such as Dev or Integration.

## Overview

This document details steps needed to deploy a sample Python application. A more complete treatment
would also cover other programming languages used by the Trebuchet team such as GoLang and Javascript.

Note: many of the specific directions (especially software installations) below work for Mac computers. 
Directions may be slightly different for *nix* or Windows machines.

### Conventions

The following symbolic names need to be replaced with your specific names:
* BUILD_RELEASE_NAME: gitlab-specific release (project name + git hashid)
* PROJECT_NAME: the gitlab name of your project.
* PROJECT_HOME: local file system root of project.
* PROJECT_NAMESPACE: the K8s namespace used by the project for deployment.

## Sample Application Details

[Data History Service](https://scm.trebuchetdev.com/analytics/data-history-viewer) source code.

It consists of the following subsystems and technologies:

* A basic Data Access Layer (DAL) implementation interface to the AWS Glue/Athena client that enables historical 
data to be queried using plain SQL. 
* A swagger-generated REST API that provides secure, metered DAL access behind the Trebuchet Gateway.
* Implemented in Python.
* Uses Swagger Python code-gen to produce the API skeleton/stubs implementations.
* Uses many 3rd-party Python libraries (large and small) to do common tasks such as connexion/flask (web server engine) and 
boto3 (AWS driver) to access key services and functionality. A complete list is in ${PROJECT_ROOT}/requirements.txt. 
* Docker is the container technology used for efficient virtualization, lifecycle control and development flexibility.
* The application will be deployed to a K8s cluster (currently control-3.dev.us-west.trebuchet.ai) 
behind the Trebuchet Gateway.
* Gitlab is used as the Continuous Integration / Continuous Delivery (CICD) pipeline that provides a 
central team source-code repository for source code authoring, review and deployment.
* Kubernetes (K8s) is the clustering technology used for grouping and scaling microservices that make 
up the application.
* Helm is open-source software used for efficiently managing the lifecycle of Kubernetes clusters.

## First steps (Configuration)

### git and Gitlab

In addition to managing the source code repository, this tool enables K8s deployment integration. A critical
gitlab configuration file called `.gitlab-ci.yml` usually sits in the git project's home directory. This
file identifies build lifecycle, relevant Helm charts, Docker containers and supported K8s deployment targets.

It will need to be precisely configured for your project -- and is generally the glue that connects all the 
needed pieces together for project lifecycle control -- build, test & deploy.

Steps to start:
* Establish a gitlab account under your userid.
* Create your new gitlab project and add initial README.md markup documents in the root folder. 
Or, instead of creating the entire project from scratch, you could clone a similar reference 
example, and then change many of the specifics, which may be much more efficient.
* Checkout your project from git to your local file system (gitlab often shows the exact git commands 
to use when you establish a new project).
    * Setup git (your defaults, etc.) using something like [a sample setup]
(https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup).
    * Checkout files: `git checkout -b your_git_working_branch_name` into your working directory.

#### Renaming a Project

Use the following steps to change the name of a Gitlab project:
* Go into the gitlab UI, hit `Project`, then `Settings`
    * Expand `General project settings` and change name
    * Expand `Advanced settings` and under `Rename repository` update `Project name` and `Path`.
    * At your command line change the remote URI (copied from the UI):
        * `git remote set-url origin $HTTPS_URL_COPIED_FROM_GITLAB_PROJ_ROOT`
* You may have to rebuild your deployment pipeline in case the deployment step is omitted. It seems that this
should be done automatically when the .gitlab-ci.yml file is re-read.

### Nexus Repo

A repository used for docker, npm, pypy repos.

* Get credentials for this repo including username & password.

### Swagger

Swagger is an Interface Definition Language (IDL) that enables implementation of language-independent, REST
API's.

* Design your API using a Swagger editor or by copying another project's swagger and modifying it to your 
functionality and data objects.
    * `brew install swagger-codegen`
* Run Python code-gen (other languages should have similar code-generation capability): 
    * `swagger-codegen generate -i swagger.yaml -l python-flask`  (Generates python framework code stubs
using your swagger API definition file). We are going to use the connexion web server on top of flask. 
* Fill in methods needed for your API logic. In this application's case, a Data Access Layer (DAL) was 
written to interface AWS Athena to the various API methods.
* Implement and/or tweak and then run the generated unit tests.
* Test the web service locally, ensuring everything works with no containerization.
    * Start app __main__.py (assuming Python). For my code I need to set a `TEST_LOCALLY=True` env 
variable to use my local AWS API access keys/configuration.
    * Browse to http://localhost:8080/\<yourAppPathDefinedInSwagger\>
    * Consider using Linux `curl` to simulate API calls in testing scripts. The swagger-generated UI has sample 
    curl commands.
    * When you deploy to a K8s cluster the endpoint (obviously) changes from localhost, and the 8080 port needs 
to be forwarded to the relevant pod instance port (if you want to drive tests locally). Example: `kubectl -n pdss
port-forward data-history-viewer-1427104547-rm2gt 8080:8080`
* If desired, test the webservice via it's _external_ DNS address per [service
  types](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services---service-types). You may need help from another team member (via slack, etc) to establish DNS addresses that are not literal pod names or cluster IP's, so as the cluster ages your calling URI will still function transparently.

## Deployment to a Kubernetes Cluster

Trebuchet applications are usually deployed as a Docker container to a specific Kubernetes (K8s) cluster 
using the Helm management tool.

The following technologies are used to correctly deploy your Trebuchet application.

### Docker (Lowest-level Container Technology)

Containerizing your application decouples it from the deployment infrastructure (such as operating system)
and allows your application to be easily scaled by replication.

* `brew cask install docker`  (initial install; Mac-OS specific)
* Start the docker application daemon  (usually easiest from UI)
* `docker ps`  (to ensure the docker daemon is started)
* `docker stop $CONTAINER_ID`   (to stop a particular dockerized application, $CONTAINER_ID from the ps command)
* `docker login docker.trebuchetdev.com`   (can be used to push/pull images from Docker image repos)
* `docker-compose up -build`  (docker build your application based on your Dockerfile)

Run your app locally in a Docker container:
* `cd $PROJECT_HOME`
* `docker build -t $PROJECT_NAME .`
* `docker images`  (shows built images that can be run)
* `docker ps -s`  (shows running containers)
* `docker run -p 8080:8080 --rm -ti $PROJECT_NAME`   (iterate this until all deploy/run errors are fixed)
* `docker run -p 8080:8080 --rm -ti $PROJECT_NAME sh`   (starts a shell on your container)
* `docker rm /$PROJECT_NAME`  (removes your application)

### Kubernetes (K8s) - (Orchestrates Containers of Applications)

Kubernetes Concepts:

1. K8s enables running/managing containers on physical & virtual hardware 
(the industry is moving to container-centric vs. host-centric architecture).
2. Generally, we have a single-process Docker image inside each Pod in a ReplicaSet.
3. Deployment controller -- controls creation, deletion & modification of pods.
* `kubectl get -n $PROJECT_NAMESPACE deployments`  (look at what has been deployed to $PROJECT_NAMESPACE)

Install Kubernetes CLI (commonly used tool for accessing K8s clusters)
* `brew install kubectl`  (Mac-OS specific)
* `kubectl version`  (make sure the install worked and it is a reasonable version)
* Sample kubectl commands (to get specific pod names use `kubectl -n $PROJECT_NAMESPACE get pods`):
    * `kubectl exec -ti -n platform sample-app-617221629-0rjxn bash`  (run bash shell on fictitious pod name)
    * `kubectl logs -n $PROJECT_NAMESPACE $pod_instance`
        * e.g. `kubectl logs -n platform an-app-617221629-0r`
* Sometime you may have to alter a cluster namespace:
    * `kubectl edit ns $PROJECT_NAMESPACE`  (will open you up into an editor to make your changes)

### Helm (To Ease Kubernetes Cluster Management)

Helm streamlines installation & management of K8s applications.

A *Chart* is a Helm package, containing all resource definitions necessary to run your app.
Charts are collected in a *Repository* where they can be collected and shared.
A *Release* is an instance of a chart running in a K8s cluster, and multiple instances can be 
installed in the same cluster, even running different versions of the same application. Releases
are created when they are installed, and each release having a unique name.

* `brew install kubernetes-helm`  (Mac-OS specific. NOTE: check the K8s version on the cluster you want 
to use, as this installs the latest helm which may not be compatible with your cluster's K8s version).
* Quickstart [here](https://docs.helm.sh/using_helm/#quickstart-guide) if you want more background.
* `cd $PROJECT_DIR`  (get to local project workspace)
* `kubectl cluster-info`  (to ensure you are running in your desired cluster)
* `helm init`   (first time-only initialization step)
* `helm repo update`   (pulls in latest from local chart repo)
* `helm ls`   (lists deployed releases)
* `helm install $BUILD_RELEASE_NAME`   (installs onto cluster)
* `helm install -n $PROJECT_NAME --namespace $PROJECT_NAMESPACE deployment/charts/$PROJECT_NAME`
* `helm delete $BUILD_RELEASE_NAME`   (takes off cluster)

Good idea: use [sem-var](https://semver.org)-style tags to differentiate deployment images. Use the 
gitlab tag feature to apply up-counting sem-var version numbers as the code changes.

### Kube2iam (Security Proxy)

An open-source tool we use to manage/proxy AWS roles in a K8s cluster.

### AWS CLI (Command Line for Amazon Web Services)

Command line interface to do common AWS operations. It needs your environment properly configured via
the ~/.aws directory, which often contains a config and credentials file. This configuration will
provide or restrict access to certain resources, depending on how it is configured. Operating temporarily
in another profile is easily accomplished with the `--profile` command line flag.

To operate in a different profile (per shell):
* `export AWS_PROFILE=$OTHER_PROFILE`
* `aws iam get-user`  (shows current user profile)
* `aws --profile dhd iam get-user`  (operate under a different profile)

Installation

* `brew install awscli`  (Mac-specific)

### Trebuchet Tools (Our Project-Specific Tools)

The Trebuchet-specific CLI tool is `tre`. With it you can perform common Trebuchet platform 
operations and get status.

Installation:
* `aws s3 cp s3://platform-bin/darwin/tre /usr/local/bin/tre && chmod +x /usr/local/bin/tre`
* `tre login cluster --env integration`  (You must login to get cluster access)
    * Sets up ~/.kube/config
    * You will need credentials from the security team (@pbarker).
    * Genesis is the overall control cluster where `tre` runs.

Common commands (at least do the login to get going):
* `tre login env`  (get info for all clusters), where

| endpoint | definition/purpose |
| ---------| ------------------ | 
| authendpoint | control cluster's authentication server (Hydra) |
| clusterauthendpoint | duplicate of above, but going away with app-controller solution |
| adminendpoint | Admin API endpoint. Interaction point for control cluster level tenant CRUD |
| apiendpoint | API Gateway. This is where services would be exposed for external use. |
| defaultcluster | development testing control cluster |
| platformendpoint | staging/preproduction control cluster |

* `tre login user --env dev`  (log into the dev environment; you will need to get a user/pass from @pbarker)
* `tre login cluster --env dev`  (point kubectl to the dev environment)
* `tre login context`   (get your current context)
* `tre infra get account drn:1::accounts:SSjtOzEyOyDLQr5q` (to get account id for staging)
* `tre infra health`   (get cluster health)
* `tre infra list cluster --alias control-3-dev.us-west.trebuchet.ai`  (list control-3 cluster members)

### Trebuchet Environments (K8s Clusters)

The Trebuchet team supports and number of deployment environments depending on the stability of the application.

Following is a generally-accepted promotion plan for apps that need to be deployed to production:
* Debug locally.
* Build/run/test with docker locally.
* Run/test on the Trebuchet *dev* K8s cluster (checking in code with gitlab-ci/cd will often automate this).
* Run/test on the Trebuchet *integration* K8s cluster (usually done manually with `helm`).
* Run/test, on the Trebuchet K8s *production* cluster (can be done manually by an deployment stage in 
gitlab_ci or promotion step in rcs).

#### Commonly-used Control-Cluster environments (as of this writing and using `tre login env`):

Documented [here](https://datapipe.atlassian.net/wiki/spaces/PCE/pages/106075025/AWS+Account+Management) but 
may be out-of-date. 
  
The following table is valid as of 2018.02.07:

| Environment | Cluster Name | DRN |
| ------------| ------------ | --- |
| New Dev | control-3.dev.us-west.trebuchet.ai | drn:1::clusters:THHU2HeEvjAMHHxH |
| Integration | control.integration.us-west.trebuchet.ai | drn:1::clusters:?? |
| Staging | control.staging.us-east.trebuchet.ai | drn:1::clusters:1TA4cRYTbNTi7Txc |

#### Accessing / Viewing Pod Logs (Detailed Debugging Information):

Nice to be able to export logs outside of container for post-mortem analysis in case pod dies or is killed):

* `kubectl -n pdss logs po/my_pod_name -f tail`  (tail continually gets last entries)
* kubectl logs -n logs -n lme --tail cluster-proc-name
    * Example: `kubectl describe rs data-history-viewer-317937145`  (describe state of most recently deployed K8s replica set)
* `kubectl -n pdss logs -f po/my_pod_name`  (`pdss` is PROJECT_NAMESPACE)
* `brew tap johanhaleby/kubetail && brew install kubetail` (Handy logging tool allows viewing N separate logs in central place)
    * `kubetail -n infra`  (looks at all infra namespace logs)

#### K8s Cluster Clean Up

Sometimes it is necessary to restart your cluster deployments and reset their state.

* `helm delete $PROJECT_NAME --purge`  
* and maybe delete remaining instances by hand using `kubectl`.

#### Executing a remote shell on a K8s cluster

`kubectl -n $PROJECT_NAMESPACE exec -it my_pod_name /bin/sh`  (execute shell on computer for login)

Testing in Clustered Environments (Dev, Integration, Staging...)
* Determine the URI to hit from `kubectl -n $PROJECT_NAMESPACE get services` (http://${PROJECT_NAME}.pdss.svc.cluster.local)
* Example: http://data-history-viewer.pdss.svc.cluster.local
* Use port-forwarding to test via browsing from a local computer:
  * `kubectl -n $PROJECT_NAMESPACE port-forward $pod-name 8080:8080` where pod-name is 1 of pods from `kubectl -n pdss get all`

#### Debugging (Efficiently Verify & Fix Problems in Your Application)

* Ensure your app is deployed by checking in the gitlab pipelines area after you check in code, which are
dependent on the branch or tag specified in your helm chart for deployment.
* Setup your environment using the following commands:
* `tre login user --env dev`  (login to Trebuchet; writes config to ~/.trebuchet folder and 
maybe even ~/.kube/config first time)
* `tre login context clean`   (is sometimes needed to clean up local context)
* `tre login cluster --env dev`  (set K8s cluster access)
Now, look for your app by namespace or exact name:
* `kubectl get namespaces`   (see all cluster namespaces)
* `helm ls`   (lists deployed releases)
* `kubectl get pods --all-namespaces`   (gets all pods for your environment)
* `kubectl get pods -n $PROJECT_NAMESPACE`   (gets all pods with that namespace)
You can also check your gitlab pipeline for all the stages it executed and view log files at each stage there.
To check pod deployment
* `tre login cluster --env dev`  (ensure you are setup for the desired env cluster)
* `kubectl get all -n $PROJECT_NAMESPACE`  (gets state of deployed pods)
* `kubectl -n $PROJECT_NAMESPACE describe deploy/data-history-viewer`
    * Example: `kubectl -n pdss describe rs/data-history-viewer-1410745306`
    
If you get stuck you can ask questions, depending on the problem, in slack channels such
as @treb-internal or @treb-support-internal as a start.

#### K8s Cluster Cleanup (In Case Something Goes Really Wrong etc.)

* Deployment: `helm delete $PROJECT_NAME --purge`
* Unused pods (in the rare case something goes wrong and helm doesn't complete the cleanup): `kubectl -n $PROJECT_NAMESPACE delete rs/$DEPLOYED_POD_NAMES` (delete deployment first, then replica-sets, then everything else)

### Permissions / Roles / Service Accounts:
* K8s Service Accounts are only needed for K8s API access
* AWS access should be provided by the global.iam_role, provided by the kube2iam package.
* kubectl -n $PROJECT_NAMESPACE get serviceaccounts

### Rudimentary Monitoring (Get Visibility on If / How Well Your App is Functioning)

Simple tool to monitor your cluster's status in realtime:
* `brew install watch`

Examples:

* `watch kubectl -n $PROJECT_NAMESPACE get pods`  (watch in 1 window, clean up in another if get into bad state)
* `watch -n 10  kubectl -n $PROJECT_NAMESPACE get pods`  (set watcher to different interval)

Q: Can I test my app on a K8s cluster besides Trebuchet?

A: 

* You can test on an existing clustering environment (see above) from your local computer.
* You can run a local K8s [MiniKube](https://github.com/kubernetes/minikube) cluster.

Q: How can I create my own K8s namespace for my applications?

A: Follow these directions (there may be an easier way):

1. Create a namespace yaml file and apply it using `kubectl apply -f [path to yaml]`. A sample
namespace file: 

```apiVersion: v1
kind: Namespace
metadata:
  name: $PROJECT_NAMESPACE
  labels:
    tenant: "985"
    workload: $PROJECT_NAME
    environment: dev```

2. `kubectl get secret -n lme docker-trebuchetdev-com -o json | jq .data`
3. `echo "[the .dockercfg value]" | base64 --decode`
4. `kubectl create secret docker-registry docker-trebuchetdev-com -n $PROJECT_NAMESPACE --docker-username=[from decoded value]
   --docker-password=[from decoded value] --docker-email=[from decoded value] --docker-server=https://docker.trebuchetdev.com`
5. create serviceaccount yaml and apply it `kubectl apply -n $PROJECT_NAMESPACE -f [path to yaml]`

```apiVersion: v1
imagePullSecrets:
- name: docker-trebuchetdev-com
kind: ServiceAccount
metadata:
  name: default```

6. You now have your very own namespace to helm install into. Also get the whole tenant, workload, 
environment tagging to test building dashboards with it.
You don't need the workload/tenant/environment part, but you need the docker secret.


