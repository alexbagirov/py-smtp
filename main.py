from smtp import SMTP, SMTPException
from argparser import Parser


def run() -> None:
    parser = Parser()
    args = parser.parse()
    smtp = SMTP()

    try:
        smtp.connect(args.host, args.port)
        smtp.hello()
        smtp.encrypt()
        smtp.authorize(args.login, args.password)
        smtp.mail_from(args.sender)
        smtp.mail_to(args.recipient)
        smtp.send_letter(args.text)
        smtp.disconnect()
    except SMTPException as e:
        smtp.client.warning('Возникла ошибка при выполнении программы: '
                            + e.message)


if __name__ == '__main__':
    run()
