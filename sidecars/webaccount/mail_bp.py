import mailbox
import os

from flask import Blueprint, session
from flask import current_app as app
from login import login_required

mail_bp: Blueprint = Blueprint("mail", __name__, url_prefix="/mail")


@mail_bp.route("/")
@login_required
def inbox() -> str:
    messages = []
    mailpath = f"/var/mail/{session.get('username')}"
    app.logger.info(f"Mail path: {mailpath}")
    for message in mailbox.mbox(mailpath):
        subject = message["subject"]
        from_ = message["from"]
        date = message["date"]
        messages.append(f"From: {from_}")
        messages.append(f"Subject: {subject}")
        messages.append(f"Date: {date}")
        messages.append("")

    return f"Welcome to your inbox. {session.get('username')}<br><br>{'<br>'.join(messages)}"
