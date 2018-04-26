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
        self.parser.add_argument('-c', '--cc', help='carbon copy',
                                 default=[], action='append')
        self.parser.add_argument('-b', '--bcc', help='blind carbon copy',
                                 default=[], action='append')
        self.parser.add_argument('--subject', help='letter subject',
                                 default=None)
        self.text = self.parser.add_mutually_exclusive_group()
        self.text.add_argument('-t', '--text', help='letter text content',
                               default=None)
        self.text.add_argument('-f', '--file', help='letter text file',
                               default=None)
        self.parser.add_argument('-a', '--attachment', help='file to attach',
                                 action='append', default=[])
        self.parser.add_argument('--named-attachment',
                                 help='specify attachment with '
                                      'specific name in the letter', nargs=2,
                                 action='append', default=[])
        self.parser.add_argument('-z', '--zip', help='zip all attachments'
                                                     'into one archive',
                                 action='store_true')
        self.parser.add_argument('--no-ssl', help='disable secure connection',
                                 action='store_true')
        self.parser.add_argument('-v', '--verbose', help='provide all program'
                                                         'logs to console',
                                 action='store_true')
        self.parser.add_argument('-e', '--encoding', default=None)

    def parse(self) -> ap.Namespace:
        args = self.parser.parse_args()

        if args.password is None:
            args.password = getpass()
        if args.name is None:
            args.name = args.sender
        if args.text is None:
            text = ''

            if args.file is not None:
                with open(args.file, 'r') as f:
                    text = f.read(51200)
            else:
                for line in sys.stdin:
                    text += line

            args.text = text if text else None
        args.recipients = [args.recipient] + args.bcc

        return args
