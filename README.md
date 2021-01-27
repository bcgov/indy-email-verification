[![img](https://img.shields.io/badge/Lifecycle-Dormant-ff7f2a)](https://github.com/bcgov/repomountie/blob/master/doc/lifecycle-badges.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

# HL Indy Email Verification Service

## Pre-Requisites

- [Docker](https://www.docker.com/products/docker-desktop)

- [s2i](https://github.com/openshift/source-to-image/releases)

- [jq](https://stedolan.github.io/jq)

- [ngrok](https://ngrok.com)

`jq` and `ngrok` are available on package manager systems for different platforms such as [Homebrew](https://brew.sh/) (Mac), [Chocolatey](https://chocolatey.org/) (Windows) and various Linux distribution package managers.

## Running

Open two shell/terminal sessions:

1. From within the [scripts](./scripts) folder execute `./start-ngrok.sh`. This will create a tunnel for the agent.

2. From within the [docker](./docker) folder:
    - run `./manage build` to assemble the runtime images for the services
    - when the build completes, run `./manage up`

_Refer to `manage -h` for additional usage information._

Once services are started, visit [http://localhost:8080](http://localhost:8080) to see the app running and visit [http://localhost:8050](http://localhost:8050) to see any outbound mail the app is sending (it won't actually send any email message in the development environment.)

## Deploying to Openshift

**Please make sure you have [Openshift Developer Tools](https://github.com/BCDevOps/openshift-developer-tools/tree/master/bin) installed and available on your path.**

### Param Files

Navigate to the openshift folder and view the existing param files.  Go into email-verification-agent-deploy.param and email-verification-service-deploy.param and uncomment  
`# NAMESPACE_NAME=myproject`  
and set it to whatever your project namespace is, in this case the namespace is 4a9599.  
`NAMESPACE_NAME=4a9599`  

Also navigate to settings.sh and at the line `export PROJECT_NAMESPACE=${PROJECT_NAMESPACE:-myproject}` replace `myproject` with your project namespace name

go into postgresql-deploy.param and comment out `POSTGRESQL_USER`, `POSTGRESQL_PASSWORD` and `POSTGRESQL_ADMIN_PASSWORD` if they are not already commented out. The characters in the regular expression sometimes get treated as bash special characters. These values will be populated with randomly generated keys

### Builds
Now that our param files are set up, we're ready to start the builds using the openshift developer script [here](https://github.com/BCDevOps/openshift-developer-tools/tree/master/bin#generate-the-build-and-images-in-the-tools-project-deploy-jenkins).  
Remember to tag the build images to the environment that you're deploying to using the following commands.

> oc tag email-verification-agent:latest email-verification-agent:dev -n 4a9599-tools  
oc tag email-verification-service:latest email-verification-service:dev -n 4a9599-tools  
oc tag postgresql:latest postgresql:dev -n 4a9599-tools  
oc tag email-verification-demo:latest email-verification-demo:dev -n 4a9599-tools  

Now that the builds have been completed and tagged it's time to start the deployment

### Deploy

Follow the [deployment](https://github.com/BCDevOps/openshift-developer-tools/tree/master/bin#generate-the-deployment-configurations-and-deploy-the-components) section to kickoff the deployment. Follow the prompts on the screen and the deployment will start. This deployment will initially fail because we haven't registered our did and ver key on the ledger. To do so, go to https://bcgov-email-verification-agent-admin-dev.apps.silver.devops.gov.bc.ca/api/doc or wherever you set your admin route to point to, and authorize with your api-key. Next scroll down untill to see the wallet section and execute the /walllet/did get request with no parameters. This should return your did and verkey.  

Next we have to register our agent on the ledger. This tutorial uses the [sovrin staging network](https://selfserve.sovrin.org/) but you can use whatever network you like, so long as it is exposed to the internet. if you're using sovrin staging, make sure you select `StagingNet` from the dropdown on the sovrin website. Enter your DID and VerKey in the fields and click submit (leave payment address blank).  
  
Next we have to accept the taa. Go back to the swagger api interface and run get /ledger/taa from the ledger section. Copy the entire contents of the text attribute from the response and paste it into the text attribute in POST /ledger/taa/accept. Copy the version number as well and set the `mechanism` attribute to be `at_submission`. Execute the request and you should see an empty response body with status code 200.  

Go back to the openshift developer console and start a rollout on email-verification-service if it hasn't already restarted. Once email-verification-service is up and running, you're ready to start issuing email credentials.

### Troubleshooting
Git doesn't always save the file permisions on executable files, if you get any permision denied errors while running scripts, make sure you run `chmod +x <file>` on any .sh file
