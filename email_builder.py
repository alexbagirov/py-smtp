from datetime import datetime


class Email:
    def __init__(self, sender: str, recipient: str, sender_name: str, cc: list,
                 subject='', text='') -> None:
        self.date = datetime.strftime(datetime.now(), '%a, %d %b %Y %H:%M:%S')
        self.sender = sender
        self.sender_name = sender_name
        self.subject = subject
        self.recipient = recipient
        self.cc = cc
        self.text = text

    def __repr__(self):
        email = 'Date: {}\n' \
               'From: {} <{}>\n' \
               'Subject: {}\n' \
               'To: {}\n'.format(self.date, self.sender_name, self.sender,
                                 self.subject, self.recipient)
        if len(self.cc) > 0:
            email += 'CC: {}\n\n'.format(', '.join(self.cc))

        email += '{}\r\n'.format(self.text)
        return email

    def to_string(self) -> str:
        return repr(self)
