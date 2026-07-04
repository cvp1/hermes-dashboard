"""Proton Mail Bridge SMTP send for the CC projects (stdlib-only).

Consolidates the near-identical ``send()`` in solar-health, battery-health,
energy-report and morning-brief. The bridge listens on 127.0.0.1:1026 with a
self-signed cert, so TLS verification is disabled (STARTTLS only). Self-send is
the norm here: ``From`` and ``To`` both default to Craig's Proton address.
"""
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formatdate

from . import secrets

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 1026
DEFAULT_SENDER = "craig.vandeputte@proton.me"
DEFAULT_PW_FILE = "~/dex/mail_bridge"


def build_message(subject, body, to=DEFAULT_SENDER, sender=DEFAULT_SENDER, html=None):
    """Build the ``EmailMessage`` (plain, plus an HTML alternative if given).

    Factored out from :func:`send` so it can be unit-tested without a live SMTP
    connection.
    """
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    # Stamp a proper local-time Date header. Without it the timestamp is assigned
    # downstream (the bridge/Proton), which mislabels the send time in the client.
    msg["Date"] = formatdate(localtime=True)
    msg.set_content(body)
    if html is not None:
        msg.add_alternative(html, subtype="html")
    return msg


def send_proton_bridge(subject, body, to=DEFAULT_SENDER, sender=DEFAULT_SENDER, html=None,
         pw_file=DEFAULT_PW_FILE, host=DEFAULT_HOST, port=DEFAULT_PORT, timeout=20):
    """Send a plain (and optionally HTML-alternative) email via Proton Bridge.

    FRAGILE: the bridge needs a GUI session + unlocked keyring, so it is DOWN
    after a reboot until revived — unattended sends silently fail. The fleet's
    default ``send()`` now uses Gmail SMTP instead (see below); this legacy
    transport is kept for completeness / manual fallback.

    The bridge password is read from ``$PROTON_BRIDGE_PW`` or ``pw_file``.
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


# --- Gmail SMTP (app-password) transport ---------------------------------
# Reboot-proof alternative to the Proton bridge: Google's SMTP needs no local
# daemon, so it survives a reboot where the bridge (GUI session + unlocked
# keyring) does not. Requires a Google App Password (2-Step Verification must be
# on) stored in ~/.key/gmail_app. Used for work-context mail; the ranch jobs
# still default to Proton via send() above.
GMAIL_HOST = "smtp.gmail.com"
GMAIL_PORT = 465  # implicit TLS (SMTPS); Gmail has a valid cert, so verify normally
GMAIL_SENDER = "craig.vandeputte@gmail.com"
GMAIL_PW_FILE = "~/.key/gmail_app"


def send_gmail(subject, body, to=GMAIL_SENDER, sender=GMAIL_SENDER, html=None,
               pw_file=GMAIL_PW_FILE, host=GMAIL_HOST, port=GMAIL_PORT, timeout=20):
    """Send via Gmail SMTP using an app password — no Proton bridge required.

    Password from ``$GMAIL_APP_PW`` or ``pw_file`` (default ~/.key/gmail_app).
    Unlike the bridge, this uses implicit TLS with full cert verification.
    """
    pw = secrets.load_secret("GMAIL_APP_PW", pw_file, what="Gmail app password")
    msg = build_message(subject, body, to=to, sender=sender, html=html)
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=ctx, timeout=timeout) as s:
        s.login(sender, pw)
        s.send_message(msg)


def send(subject, body, to=DEFAULT_SENDER, sender=GMAIL_SENDER, html=None, **kwargs):
    """Default fleet email — reboot-proof Gmail SMTP transport, but delivered to
    Craig's **Proton** inbox by default (``to=DEFAULT_SENDER``), sent **From** his
    Gmail.

    Replaced the old Proton-bridge ``send()`` on 2026-06-10: the bridge dies on
    reboot (GUI + keyring dependency — see [[proton-bridge]]), so every unattended
    job that called ``mail.send()`` was silently failing after a reboot. Call
    sites are unchanged; only the transport and From-address differ, so the ~12
    ranch/monitoring jobs keep landing in Proton exactly as before, now reliably.

    Override ``to=`` to change destination; use :func:`send_gmail` to also land in
    the Gmail inbox (work mail does this), or :func:`send_proton_bridge` for the
    legacy bridge path.
    """
    return send_gmail(subject, body, to=to, sender=sender, html=html, **kwargs)
