#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import smtplib
import argparse

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

reload(sys)

sys.setdefaultencoding('utf8')


from Interfaces.Config import Config


config = Config()


def parse_args():
    """Настройка argparse"""


    arg_parser = argparse.ArgumentParser(description='Photo sender, each photo per email.')

    arg_parser.add_argument('-e', '--email', type=str, help='EMail получателя', default=config.get("destination", "account", "username", ""))

    arg_parser.add_argument('-u', '--username', type=str, help='EMail отправителя', default=config.get("sender", "account", "username", ""))
    arg_parser.add_argument('-p', '--password', type=str, help='Пароль отправителя', default=config.get("sender", "account", "password", ""))
    arg_parser.add_argument('-s', '--server', type=str, help='Сервер, через который пойдетпочта', default=config.get("sender", "account", "server", ""))
    arg_parser.add_argument('-n', '--name', type=str, help='Имя отправителя', default=config.get("sender", "account","name", ""))

    arg_parser.add_argument('-d', '--directory', type=str, help='Папка с фотографиями в формате JPG', default=config.get("sender", "directory", "path", ""))

    return arg_parser.parse_args()


def send_mail(subject, text, files, args):
    msg = MIMEMultipart()
    msg['From'] = args.username
    msg['To'] = args.email
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=os.path.basename(f)
            )
            part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(f)
            msg.attach(part)

    server = smtplib.SMTP(host=args.server, port=587)
    server.starttls()
    server.login(args.username, args.password)

    server.sendmail(args.username, args.email, msg.as_string())
    server.close()

if __name__ == "__main__":

    args = parse_args()
    if os.path.isdir(args.directory):
        photo_extenstions = ['jpg', 'bmp', 'png', 'gif']
        photo_files = [fn for fn in os.listdir(args.directory) if any(fn.lower().endswith(ext) for ext in photo_extenstions)]
        photo_index = 1

        for photo_file in photo_files:
            print "Send photo {0} of {1} [{2}]".format(photo_index, len(photo_files), photo_file)

            photo_subject = config.get("sender", "message", "subject", "").format(photo_index=photo_index, photo_count=len(photo_files))
            photo_messadge = "{} {}".format(config.get("sender", "message", "body", ""), config.get("sender", "message", "footer", ""))
            send_mail(photo_subject, photo_messadge, ["{0}/{1}".format(args.directory, photo_file)], args)

            photo_index += 1

        print "Send photos complate."