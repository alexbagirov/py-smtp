from smtp import SMTP, SMTPException
from email_builder import Email
from argparser import Parser
from zipfile import ZipFile
import os


def run() -> None:
    parser = Parser()
    args = parser.parse()
    smtp = SMTP(args.verbose)
    args.attachments = []
    for f in args.attachment:
        try:
            args.attachments.append((open(f, 'rb'), None))
        except OSError:
            continue
    for f, name in args.named_attachment:
        try:
            args.attachments.append((open(f, 'rb'), name))
        except OSError:
            continue

    if args.zip:
        with ZipFile('attachments.zip', 'w') as zip_file:
            for f, _ in args.attachments:
                zip_file.write(f.name)

        args.attachments.clear()
        args.attachments.append((open('attachments.zip', 'rb'), None))

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
                      attachments=set(args.attachments),
                      subject=args.subject,
                      text=args.text,
                      encoding=smtp.encoding)
        smtp.send_letter(email.to_string())
        smtp.disconnect()
        if args.zip:
            os.remove('attachments.zip')
    except (SMTPException, OSError) as e:
        smtp.client.warning('Возникла ошибка '
                            'при выполнении программы: {}'.format(e.message))


if __name__ == '__main__':
    run()
