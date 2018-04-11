from datetime import datetime


class Email:
    def __init__(self, sender: str, recipient: str, sender_name: str,
                 subject='', text='') -> None:
        self.date = datetime.strftime(datetime.now(), '%a, %d %b %Y %H:%M:%S')
        self.sender = sender
        self.sender_name = sender_name
        self.subject = subject
        self.recipient = recipient
        self.text = text

    def __repr__(self):
        return 'Date: {}\nFrom: {} <{}>\n' \
               'Subject: {}\nTo: {}\n\n{}\r\n'.format(self.date,
                                                      self.sender_name,
                                                      self.sender, self.subject,
                                                      self.recipient, self.text)
