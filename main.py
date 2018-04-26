from smtp import SMTP, SMTPException
from email_builder import Email, EmailException
from argparser import Parser


def run() -> None:
    parser = Parser()
    args = parser.parse()
    smtp = SMTP(args.verbose)
    args.attachments = []
    for f in args.attachment:
        try:
            args.attachments.append(open(f, 'rb'))
        except OSError:
            continue

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
    except SMTPException as e:
        smtp.client.warning('Возникла ошибка '
                            'при выполнении программы: {}'.format(e.message))


if __name__ == '__main__':
    run()
