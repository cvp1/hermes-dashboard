"""SMTP send helpers: Gmail (app password) and Proton Mail Bridge."""
import os
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate

from . import secrets

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 1026
DEFAULT_SENDER = os.environ.get("MAIL_SENDER", "you@proton.me")
DEFAULT_PW_FILE = "~/dex/mail_bridge"


def build_message(subject, body, to=DEFAULT_SENDER, sender=DEFAULT_SENDER, html=None):
    """Build the ``EmailMessage`` (plain, plus an HTML alternative if given)."""
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    # Without a local Date header the bridge assigns one and mislabels send time.
    msg["Date"] = formatdate(localtime=True)
    msg.set_content(body)
    if html is not None:
        msg.add_alternative(html, subtype="html")
    return msg


def send_proton_bridge(subject, body, to=DEFAULT_SENDER, sender=DEFAULT_SENDER, html=None,
         pw_file=DEFAULT_PW_FILE, host=DEFAULT_HOST, port=DEFAULT_PORT, timeout=20):
    """Send a plain (and optionally HTML-alternative) email via Proton Bridge.

    The bridge uses a self-signed cert, so verification is disabled (STARTTLS).
    Password from ``$PROTON_BRIDGE_PW`` or ``pw_file``.
    """
    pw = secrets.load_secret("PROTON_BRIDGE_PW", pw_file, what="Proton Bridge password")
    msg = build_message(subject, body, to=to, sender=sender, html=html)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    with smtplib.SMTP(host, port, timeout=timeout) as s:
        s.starttls(context=ctx)
        s.login(sender, pw)
        s.send_message(msg)


# Gmail SMTP transport; requires a Google App Password.
GMAIL_HOST = "smtp.gmail.com"
GMAIL_PORT = 465  # implicit TLS
GMAIL_SENDER = os.environ.get("GMAIL_SENDER", "you@gmail.com")
GMAIL_PW_FILE = "~/.key/gmail_app"


def send_gmail(subject, body, to=GMAIL_SENDER, sender=GMAIL_SENDER, html=None,
               pw_file=GMAIL_PW_FILE, host=GMAIL_HOST, port=GMAIL_PORT, timeout=20):
    """Send via Gmail SMTP; password from ``$GMAIL_APP_PW`` or ``pw_file``."""
    pw = secrets.load_secret("GMAIL_APP_PW", pw_file, what="Gmail app password")
    msg = build_message(subject, body, to=to, sender=sender, html=html)
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=ctx, timeout=timeout) as s:
        s.login(sender, pw)
        s.send_message(msg)


def send(subject, body, to=DEFAULT_SENDER, sender=GMAIL_SENDER, html=None, **kwargs):
    """Default send: Gmail SMTP transport, delivered to the Proton address unless ``to`` is given."""
    return send_gmail(subject, body, to=to, sender=sender, html=html, **kwargs)
