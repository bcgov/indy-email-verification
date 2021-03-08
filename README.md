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
### Param Files  

***You only need to edit the param file if you intend to deploy on your own namespace***  

Navigate to the openshift folder and view the existing param files.  Go into email-verification-agent-deploy.param and email-verification-service-deploy.param and set  
`NAMESPACE_NAME=a99fd4`  
and set it to whatever your project namespace is.

Also navigate to settings.sh and at the line `export PROJECT_NAMESPACE=${PROJECT_NAMESPACE:-a99fd4}` replace `a99fd4` with your project namespace name

### Builds
Now that our param files are set up, we're ready to start the builds using the openshift developer script [here](https://github.com/BCDevOps/openshift-developer-tools/tree/master/bin#generate-the-build-and-images-in-the-tools-project-deploy-jenkins).  
Now that the builds have been completed it's time to start the deployment and tag the images

### Deploy

Follow the [deployment](https://github.com/BCDevOps/openshift-developer-tools/tree/master/bin#generate-the-deployment-configurations-and-deploy-the-components) section to kickoff the deployment. Follow the prompts on the screen and the deployment will start. Look over the deployment configuration and make sure everything is in order, next tag the image streams  

> oc -n a99fd4-tools tag email-verification-agent:latest email-verification-agent:dev  
oc -n a99fd4-tools tag email-verification-service:latest email-verification-service:dev  
oc -n a99fd4-tools tag postgresql:latest postgresql:dev  
oc -n a99fd4-tools tag email-verification-demo:latest email-verification-demo:dev  

This deployment will initially fail because we haven't registered our did and ver key on the ledger. To do so, go to https://email-verification-agent-admin-dev.apps.silver.devops.gov.bc.ca/api/doc or wherever you set your admin route to point to, and authorize with your api-key. Next scroll down untill to see the wallet section and execute the /wallet/did get request with no parameters. This should return your did and verkey.  

Next we have to register our agent on the ledger. This tutorial uses the [sovrin staging network](https://selfserve.sovrin.org/) but you can use whatever network you like, so long as it is exposed to the internet. if you're using sovrin staging, make sure you select `StagingNet` from the dropdown on the sovrin website. Enter your DID and VerKey in the fields and click submit (leave payment address blank).  
  
Next we have to accept the taa. Go back to the swagger api interface and run get /ledger/taa from the ledger section. Copy the entire contents of the text attribute from the response and paste it into the text attribute in POST /ledger/taa/accept. Copy the version number as well and set the `mechanism` attribute to be `at_submission`. Execute the request and you should see an empty response body with status code 200.  

Go back to the openshift developer console and start a rollout on email-verification-service if it hasn't already restarted. Once email-verification-service is up and running, you're ready to start issuing email credentials.

