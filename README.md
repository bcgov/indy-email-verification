# HL Indy Email Verification Service

## Running 

Make sure [Docker](https://docker.com) is installed and running.

Install [ngrok[](https://ngrok.com).

1. Run `ngrok http 10000`

1. Copy the `https` url it generates for you (**must be https**)

1. Edit line 13 of `docker/docker-compose.yml` and change the link to the ngrok link you copied.

1. In the `docker` directory run;
     1. `manage build` and `manage up`.  *Refer to `manage -h` for additional usage information.*


Then visit [http://localhost:8080](http://localhost:8080) to see the app running and visit [http://localhost:8050](http://localhost:8050) to see any outbound mail the app is sending (it won't actually send any email message in the development environment.)