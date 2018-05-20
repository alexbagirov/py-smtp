from getpass import getpass
import argparse as ap
import sys

MAX_LETTER_SIZE = 52428800


class Parser:
    def __init__(self) -> None:
        self.parser = ap.ArgumentParser(description='Send email via SMTP.',
                                        epilog='Author: Alexandr Bagirov')
        self.cred = self.parser.add_argument_group(
            'Server Details',
            'Enter your mailbox credentials')
        self.cred.add_argument('--host', help='SMTP server address',
                               required=True)
        self.cred.add_argument('-p', '--port', help='SMTP server port',
                               type=int, default=587)
        self.cred.add_argument('-l', '--login', help='mailbox name',
                               required=True)
        self.cred.add_argument('--password', help='mailbox password',
                               default=None)

        self.to = self.parser.add_argument_group(
            'Simple Delivery',
            'Provide program with email recipients')
        self.to.add_argument('-r', '--recipient', help='recipient address')
        self.to.add_argument('-c', '--cc', help='carbon copy',
                             default=[], action='append')
        self.to.add_argument('-b', '--bcc', help='blind carbon copy',
                             default=[], action='append')

        self.file = self.parser.add_argument_group(
            'Batch Delivery',
            'Provide program with recipients list')
        self.file.add_argument('--batch',
                               help='file for batch message delivery',
                               default=None)
        self.file.add_argument('--batch-bcc',
                               help='send email to multiple '
                                    'recipients at once',
                               action='store_true')

        self.data = self.parser.add_argument_group(
            'Email',
            'Enter your message')
        self.data.add_argument('-s', '--sender', help='sender address',
                               default=None)
        self.data.add_argument('-n', '--name', help='sender name',
                               default=None)
        self.data.add_argument('--subject', help='letter subject',
                               default=None)

        self.text = self.data.add_mutually_exclusive_group()
        self.text.add_argument('-t', '--text', help='letter text content',
                               default=None)
        self.text.add_argument('-f', '--file', help='letter text file',
                               default=None)

        self.data.add_argument('-a', '--attachment', help='file to attach',
                               action='append', default=[])
        self.data.add_argument('--named-attachment',
                               help='specify attachment with '
                                    'specific name in the letter', nargs=2,
                               action='append', default=[])

        self.other = self.parser.add_argument_group('Other Options')
        self.other.add_argument('-z', '--zip',
                                help='zip all attachments into one archive',
                                action='store_true')
        self.other.add_argument('--no-ssl', help='disable secure connection',
                                action='store_true')
        self.other.add_argument('-v', '--verbose',
                                help='provide all program logs to console',
                                action='store_true')
        self.other.add_argument('-e', '--encoding', default=None)
        self.other.add_argument('-m', '--max-file-size',
                                help='max file size in MB', type=int,
                                default=0)

    def parse(self) -> ap.Namespace:
        args = self.parser.parse_args()

        if args.password is None:
            args.password = getpass()
        if args.sender is None:
            args.sender = args.login
        if args.name is None:
            args.name = args.sender
        if args.text is None:
            if args.file is not None:
                with open(args.file, 'rb') as f:
                    text = f.read(MAX_LETTER_SIZE)
            else:
                text = sys.stdin.read(MAX_LETTER_SIZE)

            args.text = text if text else None

        args.recipients = [args.recipient] + args.bcc
        args.max_file_size *= 1048576

        return args
