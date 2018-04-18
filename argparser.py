from getpass import getpass
import argparse as ap
import fileinput
import sys


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
        self.text = self.parser.add_mutually_exclusive_group()
        self.text.add_argument('-t', '--text', help='letter text content',
                               default=None)
        self.text.add_argument('-f', '--file', help='letter text file',
                               default=None)
        self.parser.add_argument('--no-ssl', help='disable secure connection',
                                 action='store_true')
        self.parser.add_argument('-v', '--verbose', help='provide all program'
                                                         'logs to console',
                                 action='store_true')

    def parse(self) -> ap.Namespace:
        args = self.parser.parse_args()

        if args.password is None:
            args.password = getpass()
        if args.name is None:
            args.name = args.sender
        if args.text is None:
            f = sys.stdin if args.file is None \
                else fileinput.input(args.file)
            text = ''

            for line in f:
                text += line

            args.text = text

        return args
