from smtp import SMTP, SMTPException
from email_builder import Email
from argparser import Parser


def run() -> None:
    parser = Parser()
    args = parser.parse()
    smtp = SMTP(args.verbose)
    email = Email(args.sender, args.recipient, args.name, args.cc,
                  args.subject, args.text)

    try:
        smtp.connect(args.host, args.port)
        smtp.hello()
        if args.no_ssl is not True:
            smtp.encrypt()
        smtp.authorize(args.login, args.password)
        smtp.mail_from(args.sender)
        for recipient in args.recipients:
            smtp.mail_to(recipient)
        smtp.send_letter(email.to_string())
        smtp.disconnect()
    except SMTPException as e:
        smtp.client.warning('Возникла ошибка '
                            'при выполнении программы: {}'.format(e.message))


if __name__ == '__main__':
    run()
