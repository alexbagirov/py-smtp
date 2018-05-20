from simple import run
from argparse import Namespace
from smtp import SMTPException
import json
import re
import os


SAVE_DELAY = 10


class BatchSender:
    def __init__(self, recipients: str, args: Namespace):
        self.recipients = open(recipients, 'r')
        self.args = args

        self.position = 0
        self.retry = []
        self.backup = 'backup.json'
        self.temporary_file = 'temp.json'

        self.bcc_limit = 15
        self.before_save = SAVE_DELAY

        self.email = re.compile(r'\S+@\S+')

        self.load()

    def load(self):
        try:
            with open(self.backup, 'r') as f:
                state = json.loads(f.read())
                self.position = state['position']
                self.retry = state['retry']
        except (OSError, json.JSONDecodeError, FileNotFoundError):
            pass

    def save(self):
        try:
            with open(self.temporary_file, 'w') as f:
                state = {'position': self.position, 'retry': self.retry}
                f.write(json.dumps(state))
            os.rename(self.temporary_file, self.backup)
        except OSError:
            pass

    def broadcast(self):
        self.recipients.seek(self.position)

        while True:
            recipient = self.recipients.readline().rstrip()
            if not recipient:
                break
            if not self.email.match(recipient):
                continue

            recipients = [recipient]
            if self.args.batch_bcc:
                while True:
                    new = self.recipients.readline().rstrip()
                    if not new:
                        break
                    recipients.append(new)
                    if len(recipients) >= self.bcc_limit:
                        break

            self.args.recipient = recipient
            self.args.recipients = recipients
            try:
                run(self.args)
            except SMTPException:
                self.retry.append(recipient)
            self.position = self.recipients.tell()
            self.before_save -= 1

            if self.before_save == 0:
                self.before_save = SAVE_DELAY
                self.save()

        while self.retry:
            recipient = self.retry.pop()
            try:
                run(self.args)
            except SMTPException:
                self.retry.append(recipient)

        try:
            os.remove('backup.json')
        except OSError:
            pass
