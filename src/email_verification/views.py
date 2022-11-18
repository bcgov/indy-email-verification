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
API_KEY = os.environ.get("AGENT_ADMIN_API_KEY", "")

def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render({"form": EmailForm()}, request))


def submit(request):
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():

            response = requests.post(f"{AGENT_URL}/connections/create-invitation",headers={"x-api-key": API_KEY})
            invite = response.json()

            connection_id = invite["connection_id"]
            invite_url    = invite["invitation_url"]

            form.instance.connection_id = connection_id
            form.instance.invite_url = invite_url
            form.save()

            email = form.instance.email

            redirect_url = f"{os.environ.get('SITE_URL')}/verify/{connection_id}"

            logging.critical("REDIRECT_URL"); 
            logging.critical({redirect_url});

            template = loader.get_template("email.html")
            email_html = template.render({"redirect_url": redirect_url}, request)

            send_mail(
                "Invitation du Service de Vérification de Courriel du Québec",
                (
                    "Suivez ce lien pour vous connecter à notre "
                    f"service de vérification: {redirect_url}"
                ),
                "Service de Verification de Courriel du Québec  <noreply@mcn.gov.qc.ca>",
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

    didcomm_url = re.sub(r"^https?:\/\/\S*\?", "didcomm://invite?", invitation_url)

    template = loader.get_template("verify.html")

    stream = io.BytesIO()
    qr_png = qrcode.make(invitation_url)
    qr_png.save(stream, "PNG")
    qr_png_b64 = base64.b64encode(stream.getvalue()).decode("utf-8")

    return HttpResponse(
        template.render(
            {
                "qr_png": qr_png_b64,
                "didcomm_url": didcomm_url,
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
        connection_id = str(message["connection_id"])

        SessionState.objects.filter(connection_id=connection_id).update(
            state="connection-formed"
        )

        time.sleep(5)

        logger.info(
            f"Sending credential offer for connection {connection_id} "
            f"and credential definition {credential_definition_id}"
        )

        verification = get_object_or_404(Verification, connection_id=connection_id)

        request_body = {
            "auto_issue": True,
            "connection_id": connection_id,
            "cred_def_id": credential_definition_id,
            "credential_preview": {
                "attributes": [
                    {
                        "name": "email",
                        "value": verification.email,
                        "mime-type": "text/plain",
                    },
                    {
                        "name": "time",
                        "value": str(datetime.utcnow()),
                        "mime-type": "text/plain",
                    },
                ]
            },
        }

        try:
            response = requests.post(
                f"{AGENT_URL}/issue-credential/send-offer",headers={"x-api-key": API_KEY}, json=request_body
            )
            response.raise_for_status()
        except Exception:
            logger.exception("Error sending credential offer:")
            SessionState.objects.filter(connection_id=connection_id).update(
                state="offer-error"
            )
        else:
            SessionState.objects.filter(connection_id=connection_id).update(
                state="offer-sent"
            )

        return HttpResponse()

    # Handle completion of credential issue
    if topic == "issue_credential" and message["state"] == "credential_issued":
        credential_exchange_id = message["credential_exchange_id"]
        connection_id = message["connection_id"]

        logger.info(
            "Completed credential issue for credential exchange "
            f"{credential_exchange_id} and connection {connection_id}"
        )

        SessionState.objects.filter(connection_id=connection_id).update(
            state="credential-issued"
        )

        return HttpResponse()

    logger.warning(f"Webhook for topic {topic} and state {message['state']} is not implemented")
    return HttpResponse()
