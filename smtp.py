import base64
import socket
import ssl
import logging


class SMTP(object):
    """Класс для общения с сервером и отправки писем."""
    def __init__(self, host: str, port: int) -> None:
        """Инициализируем клиент."""
        self.host = host
        self.port = port
        self.sock = socket.socket()
        self.sock.settimeout(10)
        self.retries = 3

        self.log = logging.Logger('SMTP')
        self.log.setLevel(logging.INFO)

        log_handler = logging.StreamHandler()
        log_handler.setLevel(logging.INFO)
        log_fmt = logging.Formatter('[{name}]: {message}\n',
                                    style='{')
        log_handler.setFormatter(log_fmt)
        self.log.addHandler(log_handler)

        self.log.info('Клиент инициализирован.')

    def connect(self) -> None:
        """Подключаемся к серверу."""
        for i in range(self.retries):
            try:
                self.sock.connect((self.host, self.port))
                self.log.info('Установлено соединение с сервером.')
            except socket.timeout:
                self.log.info('Попытка {} не удалась, пробуем ещё раз.'.format(i))
                continue
            else:
                return
        self.log.warning('Не удалось установить соединение с сервером.')
        raise Exception

    def send(self, content: bytes) -> None:
        """Отправляем серверу данное содержимое."""
        self.sock.send(content + b'\r\n')

    def receive(self) -> bytes:
        """Получаем ответ сервера на отправленную команду."""
        for i in range(self.retries):
            try:
                return self.sock.recv(1024)
            except socket.timeout:
                continue

    def hello(self) -> None:
        """Отправляем команду приветствия."""
        self.log.info('Отправляем приветствие серверу.')
        self.send(b'ehlo localhost')
        resp = self.receive().split()

        if int(resp[0]) != 220:
            self.log.warning('Получен код ошибки при приветствии.')
            raise Exception(resp)

    def start_tls(self) -> None:
        """Начинаем передачу по защищённому соединению."""
        self.log.info('Отправляем запрос на TLS-соединение.')
        self.send(b'starttls')
        resp = self.receive().split()
        # resp2 = self.receive().split()
        print(resp)

        if not resp[0].startswith(b'250'):
            self.log.warning('Запрос на TLS не получил безошибочный ответ.')
            raise Exception(resp)

    def wrap_socket(self) -> None:
        """Оборачиваем сокет в зашифрованный формат."""
        self.log.info('Сокет для защищённого соединения готов.')
        self.sock = ssl.wrap_socket(self.sock, ssl_version=ssl.PROTOCOL_SSLv23)

    def auth(self) -> None:
        """Запускаем процесс авторизации."""
        self.log.info('Отправляем запрос на авторизацию.')
        self.send(b'auth login')
        print(self.receive())

    def login(self, login: bytes) -> None:
        """Отправляем логин для сервера."""
        self.send(base64.b64encode(login))
        self.receive()

    def password(self, password: bytes) -> None:
        """Отправляем логин для сервера."""
        self.send(base64.b64encode(password))
        print(self.receive().split())

    def mail_from(self, sender: bytes) -> None:
        """Отправляем серверу адрес отправителя."""
        self.send(b'mail from: <' + sender + b'>')

        resp = self.receive().split()

        if int(resp[0]) != 250:
            raise Exception

    def mail_to(self, recepient: bytes) -> None:
        """Отправляем серверу адрес получателя."""
        self.send(b'rcpt to: <' + recepient + b'>')

        resp = self.receive().split()

        if int(resp[0]) != 250:
            raise Exception

    def data(self) -> None:
        """Начинаем передачу содержимого письма."""
        self.send(b'data')

        resp = self.receive().split()

        if int(resp[0]) != 250:
            raise Exception

    def send_letter(self, content: bytes) -> None:
        """Передаём серверу содержимое письма."""
        self.send(content)
        self.send(b'.\r\n')

        resp = self.receive().split()

        if int(resp[0]) != 250:
            raise Exception

    def disconnect(self) -> None:
        """Закрываем соединение."""
        self.sock.close()


if __name__ == '__main__':
    smtp = SMTP('smtp.yandex.ru', 587)
    smtp.connect()
    smtp.hello()
    smtp.start_tls()
    smtp.auth()
    smtp.login(b'pyt4on@yandex.ru')
    smtp.password(b'17401725')
    smtp.mail_from(b'pyt4on@yandex.ru')
