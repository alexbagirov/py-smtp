from datetime import datetime
from mimetypes import guess_type
from base64 import b64encode


class EmailException(Exception):
    def __init__(self, message, file: str) -> None:
        self.message = message
        self.file = file


class Email:
    def __init__(self, sender: str, recipient: str, sender_name: str,
                 cc: set = (), attachments: set = (), subject: str = None,
                 text: str = None, encoding: str = 'utf-8',
                 attch_part: tuple = None) -> None:
        self.date = datetime.strftime(datetime.now(), '%a, %d %b %Y %H:%M:%S')
        self.sender = sender
        self.sender_name = sender_name
        self.subject = subject
        self.recipient = recipient
        self.cc = cc
        self.text = text
        self.attachments = attachments
        self.attch_part = attch_part
        self.encoding = encoding
        self.subject_text = self.format_subject()
        self.cc_text = self.format_cc()
        self.attachments_text = self.format_attachments()

    def format_cc(self) -> str:
        if not self.cc:
            return ''
        return 'Cc: {}\n'.format(', '.join(self.cc))

    def format_subject(self) -> str:
        if not self.subject:
            return ''
        return 'Subject: {}\n'.format(self.subject)

    def format_attachments(self):
        if self.attch_part:
            return self.format_attachment_part()

        text = []
        attachment = ('Content-Disposition: attachment; filename="{}"\n'
                      'Content-Transfer-Encoding: base64\n'
                      'Content-Type: {}; name="{}"\n\n\n{}\n--frontier\n')

        for fname, new_name in self.attachments:
            file_name = new_name if new_name else fname[0].name
            text.append(attachment.format(
                file_name,
                guess_type(fname[0].name)[0],
                fname[0].name,
                b64encode(fname[0].read()).decode(self.encoding)))
        return ' '.join(text)

    def format_attachment_part(self):
        attachment = ('Content-Disposition: attachment; filename="{}"\n'
                      'Content-Transfer-Encoding: base64\n'
                      'Content-Type: {}; name="{}"\n\n\n{}\n--frontier\n')
        return attachment.format(
            self.attch_part[0],
            guess_type(self.attch_part[0]),
            self.attch_part[0],
            b64encode(self.attch_part[1]).decode(self.encoding))

    def to_string(self) -> str:
        template = ('From: {} <{}>\nTo: {}\n{}{}'
                    'MIME-Version: 1.0\nDate: {}\n'
                    'Content-Type: multipart/mixed; boundary=frontier\n'
                    'Return-Path: {}\n\n\n--frontier\n'
                    'Content-Transfer-Encoding: 8bit\n'
                    'Content-Type: text/plain; '
                    'charset=utf-8\n\n{}\n--frontier\n')

        return template.format(self.sender_name, self.sender, self.recipient,
                               self.cc_text, self.subject_text,
                               self.date, self.sender,
                               self.text) + self.attachments_text
