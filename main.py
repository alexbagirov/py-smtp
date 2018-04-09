from smtp import SMTP
import argparse as ap


class Parser(object):
    def __init__(self) -> None:
        self.parser = ap.ArgumentParser(description='Send email via SMTP.',
                                        epilog='Author: Alexandr Bagirov')
        self.parser.add_argument('host', help='SMTP server address')
        self.parser.add_argument('port', help='SMTP server port', type=int)
        self.parser.add_argument('login', help='mailbox name')
        self.parser.add_argument('password', help='mailbox password')
        self.parser.add_argument('sender', help='sender address')
        self.parser.add_argument('recipient', help='recipient address')
        self.parser.add_argument('text', help='full letter content')

    def parse(self) -> ap.Namespace:
        return self.parser.parse_args()

    def run(self) -> None:
        args = self.parser.parse_args()
        smtp = SMTP()
        smtp.connect(args.host, args.port)
        smtp.hello()
        smtp.encrypt()
        smtp.authorize(args.login, args.password)
        smtp.mail_from(args.sender)
        smtp.mail_to(args.recipient)
        smtp.send_letter(args.text)
        smtp.disconnect()


if __name__ == '__main__':
    parser = Parser()
    parser.run()
