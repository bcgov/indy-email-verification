import base64
import io
import os
import re
import json
import time
from datetime import datetime

import qrcode
import requests


from django.http import (
    JsonResponse,
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseBadRequest,
)
from django.template import loader
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

from .forms import EmailForm
from .models import Verification, SessionState

import logging

logger = logging.getLogger(__name__)

AGENT_URL = os.environ.get("AGENT_URL")


def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render({"form": EmailForm()}, request))


def submit(request):
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():

            response = requests.post(f"{AGENT_URL}/connections/create-invitation")
            invite = response.json()

            connection_id = invite["connection_id"]
            invite_url = invite["invitation_url"]

            form.instance.connection_id = connection_id
            form.instance.invite_url = invite_url
            form.save()

            email = form.instance.email

            redirect_url = f"{os.environ.get('SITE_URL')}/verify/{connection_id}"

            template = loader.get_template("email.html")
            email_html = template.render({"redirect_url": redirect_url}, request)

            send_mail(
                "BC Email Verification Invite",
                (
                    "Follow this link to connect with our "
                    f"verification service: {redirect_url}"
                ),
                "Email Verification Service <noreply@gov.bc.ca>",
                [email],
                fail_silently=False,
                html_message=email_html,
            )

            SessionState.objects.get_or_create(
                connection_id=connection_id, state="invite-created"
            )

            return HttpResponseRedirect(f"/thanks?email={form.instance.email}")
        else:
            return HttpResponseBadRequest()


def thanks(request):
    try:
        email = request.GET["email"]
    except Exception:
        return HttpResponseBadRequest()

    template = loader.get_template("thanks.html")
    return HttpResponse(template.render({"email": email}, request))


def state(request, connection_id):
    state = SessionState.objects.get(connection_id=connection_id)
    resp = {"state": state.state}
    try:
        attendee = Verification.objects.get(connection_id=connection_id)
        resp["email"] = attendee.email
    except Exception:
        pass

    return JsonResponse(resp)


def in_progress(request, connection_id):
    state = SessionState.objects.get(connection_id=connection_id)
    template = loader.get_template("in_progress.html")
    return HttpResponse(
        template.render({"connection_id": connection_id, state: state.state}, request)
    )


def verify_redirect(request, connection_id):
    verification = get_object_or_404(Verification, connection_id=connection_id)
    invitation_url = verification.invite_url

    streetcred_url = re.sub(
        r"^https?:\/\/\S*\?", "id.streetcred://invite?", invitation_url
    )

    template = loader.get_template("verify.html")

    stream = io.BytesIO()
    qr_png = qrcode.make(invitation_url)
    qr_png.save(stream, "PNG")
    qr_png_b64 = base64.b64encode(stream.getvalue()).decode("utf-8")

    return HttpResponse(
        template.render(
            {
                "qr_png": qr_png_b64,
                "streetcred_url": streetcred_url,
                "invitation_url": invitation_url,
                "connection_id": verification.connection_id,
            },
            request,
        )
    )


@csrf_exempt
def webhooks(request, topic):

    message = json.loads(request.body)
    logger.info(f"webhook recieved - topic: {topic} body: {request.body}")

    if topic == "connections" and message["state"] == "request":
        connection_id = message["connection_id"]
        SessionState.objects.filter(connection_id=connection_id).update(
            state="connection-request-received"
        )

    # Handle new invites, send cred offer
    if topic == "connections" and message["state"] == "response":
        credential_definition_id = cache.get("credential_definition_id")
        assert credential_definition_id is not None

        SessionState.objects.filter(connection_id=message["connection_id"]).update(
            state="connection-formed"
        )

        time.sleep(5)

        logger.info(
            f"Sending credential offer for connection {message['connection_id']} "
            f"and credential definition {credential_definition_id}"
        )

        request_body = {
            "connection_id": message["connection_id"],
            "cred_def_id": credential_definition_id,
        }

        response = requests.post(
            f"{AGENT_URL}/issue-credential/send-offer", json=request_body
        )

        SessionState.objects.filter(connection_id=str(message["connection_id"])).update(
            state="offer-sent"
        )

        return HttpResponse()

    # Handle cred request, issue cred
    if topic == "issue_credential" and message["state"] == "request_received":
        credential_exchange_id = message["credential_exchange_id"]
        connection_id = message["connection_id"]

        logger.info(
            "Sending credential issue for credential exchange "
            f"{credential_exchange_id} and connection {connection_id}"
        )

        verification = get_object_or_404(Verification, connection_id=connection_id)
        request_body = {
            "credential_preview": {
                "attributes": [
                    {"name": "email", "value": verification.email},
                    {"name": "time", "value": str(datetime.utcnow())},
                ]
            }
        }

        response = requests.post(
            f"{AGENT_URL}/issue_credential/{credential_exchange_id}/issue",
            json=request_body,
        )

        SessionState.objects.filter(connection_id=connection_id).update(
            state="credential-issued"
        )

        return HttpResponse()

    return HttpResponse()
