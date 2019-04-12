import base64
import io
import os
import re

import qrcode
import requests


from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)
from django.template import loader
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404


from .forms import EmailForm
from .models import Verification

import logging

logger = logging.getLogger(__name__)

AGENT_URL = "http://icatagent:5000"


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
            email_html = template.render(
                {"redirect_url": redirect_url}, request
            )

            send_mail(
                "BC Email Verification Invite",
                f"Follow this link to connect with our verification service: {redirect_url}",
                "email-verify-test@lucent.is",
                [email],
                fail_silently=False,
                html_message=email_html,
            )

            return HttpResponseRedirect(f"/thanks?email={form.instance.email}")
        else:
            return HttpResponseBadRequest()


def thanks(request):
    try:
        email = request.GET["email"]
    except:
        return HttpResponseBadRequest()

    template = loader.get_template("thanks.html")
    return HttpResponse(template.render({"email": email}, request))


def verify_redirect(request, connection_id):
    verification = get_object_or_404(Verification, connection_id=connection_id)

    streetcred_url = re.sub(
        r"^https?:\/\/\S*\?", "id.streetcred://invite?", verification.invite_url
    )

    template = loader.get_template("verify.html")

    stream = io.BytesIO()
    qr_png = qrcode.make(verification.invite_url)
    qr_png.save(stream, "PNG")
    qr_png_b64 = base64.b64encode(stream.getvalue()).decode("utf-8")

    return HttpResponse(
        template.render(
            {"qr_png": qr_png_b64, "streetcred_url": streetcred_url}, request
        )
    )

