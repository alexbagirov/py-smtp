from simple import run
from argparse import Namespace
from smtp import SMTPException
import json
import re
import os


class BatchSender:
    def __init__(self, recipients: str, args: Namespace):
        self.recipients = open(recipients, 'r')
        self.args = args

        self.position = 0
        self.retry = []
        self.backup = 'backup.json'

        self.bcc_limit = 15

        self.email = re.compile('^[A-Za-z0-9\.\+_-]+'
                                '@[A-Za-z0-9\._-]+\.[a-zA-Z]*$')

        self.load()

    def load(self):
        try:
            f = open(self.backup, 'r')
            state = json.loads(f.read())
            self.position = state['position']
            self.retry = state['retry']
        except (OSError, json.JSONDecodeError):
            return

    def save(self):
        try:
            f = open(self.backup, 'w')
            state = {'position': self.position, 'retry': self.retry}
            f.write(json.dumps(state))
        except OSError:
            return

    def broadcast(self):
        try:
            self.recipients.seek(self.position)

            while True:
                recipient = self.recipients.readline().rstrip()
                if recipient == '':
                    break
                if not self.email.match(recipient):
                    continue

                recipients = [recipient]
                if self.args.batch_bcc:
                    while True:
                        new = self.recipients.readline().rstrip()
                        if new == '':
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
        except KeyboardInterrupt:
            self.save()
            return
