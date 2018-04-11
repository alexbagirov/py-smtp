import argparse as ap
from getpass import getpass


class Parser:
    def __init__(self) -> None:
        self.parser = ap.ArgumentParser(description='Send email via SMTP.',
                                        epilog='Author: Alexandr Bagirov')
        self.parser.add_argument('--host', help='SMTP server address',
                                 required=True)
        self.parser.add_argument('-p', '--port', help='SMTP server port',
                                 type=int, default=587)
        self.parser.add_argument('-l', '--login', help='mailbox name',
                                 required=True)
        self.parser.add_argument('--password', help='mailbox password',
                                 default=None)
        self.parser.add_argument('-s', '--sender', help='sender address',
                                 required=True)
        self.parser.add_argument('-n', '--name', help='sender name',
                                 default=None)
        self.parser.add_argument('-r', '--recipient', help='recipient address',
                                 required=True)
        self.parser.add_argument('--subject', help='letter subject')
        self.parser.add_argument('-t', '--text', help='full letter content',
                                 default='')
        self.parser.add_argument('--no-ssl', help='disable secure connection',
                                 action='store_true')

    def parse(self) -> ap.Namespace:
        args = self.parser.parse_args()
        if args.password is None:
            args.password = getpass()
        if args.name is None:
            args.name = args.sender
        return args
