from smtp import SMTP, SMTPException
from email_builder import Email
from argparser import Parser


def run() -> None:
    parser = Parser()
    args = parser.parse()
    smtp = SMTP()
    email = Email(args.sender, args.recipient, args.name,
                  args.subject, args.text)

    try:
        smtp.connect(args.host, args.port)
        smtp.hello()
        if args.no_ssl is not True:
            smtp.encrypt()
        smtp.authorize(args.login, args.password)
        smtp.mail_from(args.sender)
        smtp.mail_to(args.recipient)
        smtp.send_letter(repr(email))
        smtp.disconnect()
    except SMTPException as e:
        smtp.client.warning('Возникла ошибка '
                            'при выполнении программы: {}'.format(e.message))


if __name__ == '__main__':
    run()
