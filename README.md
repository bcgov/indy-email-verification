# HL Indy Email Verification Service

## Running 

Make sure [Docker](https://docker.com) is installed and running.

Install [ngrok[](https://ngrok.com).

1. Run `ngrok http 10000`

2. Copy the `https` url it generates for you (**must be https**)

3. Edit line 13 of `docker/docker-compose.yml` and change the link to the ngrok link you copied.

4. In the `docker` directory run `docker-compose build` and `docker-compose up`.


Then visit [http://localhost:8000](http://localhost:8000) to see the app running and visit [http://localhost:8050](http://localhost:8050) to see any outbound mail the app is sending (it won't actually send any email message in the development environment.)