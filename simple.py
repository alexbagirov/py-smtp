from smtp import SMTP, SMTPException
from zipfile import ZipFile
from email_builder import Email
from argparse import Namespace
import os


def run(args) -> None:
    smtp = SMTP(args.verbose)
    args.attachments = []
    attch_parts = []

    open_attachments(args, smtp)
    open_named_attachments(args)

    if args.zip:
        zip_attachments(args)

    if args.max_file_size:
        split_attachments(args, attch_parts)

    i = 0
    without_attch = not args.attachments and not attch_parts
    while args.attachments or attch_parts or without_attch:
        try:
            smtp.connect(args.host, args.port)
            smtp.hello()
            if args.no_ssl is not True:
                smtp.encrypt()
            smtp.authorize(args.login, args.password)
            smtp.mail_from(args.sender)
            for recipient in args.recipients:
                smtp.mail_to(recipient)

            email = Email(args.sender, args.recipient, args.name,
                          cc=set(args.cc),
                          attachments=set(args.attachments)
                          if i == 0 else None,
                          attch_part=attch_parts[0]
                          if not without_attch else None,
                          subject=args.subject if i == 0 else
                          '{} - {}'.format(args.subject, i + 1),
                          text=args.text if i == 0 else 'Letter continuation.',
                          encoding=smtp.encoding)

            smtp.send_letter(email.to_string())
            smtp.disconnect()

            for file, _ in args.attachments:
                file.close()
            if args.zip:
                os.remove('attachments.zip')

            if without_attch:
                break

            i += 1
            args.attachments.clear()
            attch_parts.pop(0)

        except (SMTPException, OSError) as e:
            smtp.client.warning('An error occurred '
                                'during the runtime: {}'.format(e.message))
            smtp.close()


def open_attachments(args: Namespace, smtp: SMTP):
    for f in args.attachment:
        try:
            args.attachments.append((open(f, 'rb'), None))
        except OSError as e:
            smtp.client.warn('An error occurred while opening '
                             'the file {}: {}'.format(e.filename,
                                                      e.strerror))
            continue


def open_named_attachments(args: Namespace):
    for f, name in args.named_attachment:
        try:
            args.attachments.append((open(f, 'rb'), name))
        except OSError:
            continue


def zip_attachments(args: Namespace):
    with ZipFile('attachments.zip', 'w') as zip_file:
        for f, _ in args.attachments:
            zip_file.write(f.name)

    args.attachments.clear()
    args.attachments.append((open('attachments.zip', 'rb'), None))


def split_attachments(args: Namespace, attch_parts: list):
    big_files = []
    for file in args.attachments:
        if os.path.getsize(file[0].name) > args.max_file_size > 0:
            big_files.append(file)
            part = file[0].read(args.max_file_size)
            attch_parts.append((file[0].name, part))
            while part != b'':
                part = file[0].read(args.max_file_size)
                attch_parts.append((file[0].name, part))
            attch_parts.pop()

    for file in big_files:
        args.attachments.remove(file)
