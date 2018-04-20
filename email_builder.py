from datetime import datetime
from mimetypes import guess_type
from base64 import b64encode


class EmailException(Exception):
    def __init__(self, message, file: str) -> None:
        self.message = message
        self.file = file


class Email:
    def __init__(self, sender: str, recipient: str, sender_name: str, cc: list,
                 attachments: list, subject: str, text='') -> None:
        self.date = datetime.strftime(datetime.now(), '%a, %d %b %Y %H:%M:%S')
        self.sender = sender
        self.sender_name = sender_name
        self.subject = subject
        self.recipient = recipient
        self.cc = cc
        self.text = text
        self.attachments = attachments

    def __repr__(self):
        template = 'From: {} <{}>\nTo: {}\n{}{}' \
                   'MIME-Version: 1.0\nDate: {}\n' \
                   'Content-Type: multipart/mixed; boundary=frontier\n' \
                   'Return-Path: {}\n\n\n--frontier\n' \
                   'Content-Transfer-Encoding: 8bit\n' \
                   'Content-Type: text/plain; ' \
                   'charset=utf-8\n\n{}\n--frontier\n'
        attachment = 'Content-Disposition: attachment; filename="{}"\n' \
                     'Content-Transfer-Encoding: base64\n' \
                     'Content-Type: {}; name="{}"\n\n\n{}\n--frontier\n'
        email = template.format(self.sender_name, self.sender, self.recipient,
                                self.format_cc(), self.format_subject(),
                                self.date, self.sender, self.text)

        for file in self.attachments:
            try:
                with open(file, 'rb') as f:
                    email += attachment.format(file, guess_type(file)[0], file,
                                               b64encode(
                                                   f.read()
                                               ).decode('utf-8'))
            except OSError:
                raise EmailException('Не удалось '
                                     'открыть файл: {}'.format(file), file)

        return email

    def format_cc(self) -> str:
        if len(self.cc) == 0:
            return ''
        return 'CC: {}\n'.format(', '.join(self.cc))

    def format_subject(self) -> str:
        if not self.subject:
            return ''
        return 'Subject: {}\n'.format(self.subject)

    def to_string(self) -> str:
        return repr(self)
