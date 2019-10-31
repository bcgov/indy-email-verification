# HL Indy Email Verification Service

## Running

Make sure [Docker](https://docker.com) is installed and running.

Install [ngrok[](https://ngrok.com).

1. Run `ngrok http 10000`

1. Copy the `https` url it generates for you (**must be https**)

1. Search and replace `https://65cf3bd1.ngrok.io` with the link to the ngrok link you copied (there should be two instances, at lines 13 and 24).

1. In the `docker` directory run;
   1. `manage build` and `manage up`. _Refer to `manage -h` for additional usage information._

Then visit [http://localhost:8080](http://localhost:8080) to see the app running and visit [http://localhost:8050](http://localhost:8050) to see any outbound mail the app is sending (it won't actually send any email message in the development environment.)
