import base64
import socket
import ssl
import logging


class SMTPException(Exception):
    """Основной класс исключений."""
    def __init__(self, message) -> None:
        self.message = message


class SMTP:
    """Класс для общения с сервером и отправки писем."""
    def __init__(self, verbose=False) -> None:
        """Инициализируем клиент."""
        self.sock = socket.socket()
        self.enc_sock = None
        self.encrypted = False
        self.sock.settimeout(10)
        self.retries = 3

        self.client = logging.getLogger('Client')
        self.server = logging.getLogger('Server')
        self.client.setLevel(logging.INFO)
        self.server.setLevel(logging.INFO)

        log_handler = logging.StreamHandler()
        if verbose:
            log_handler.setLevel(logging.INFO)
        else:
            log_handler.setLevel(logging.WARN)
        log_fmt = logging.Formatter('[{name}]: {message}\n',
                                    style='{')
        log_handler.setFormatter(log_fmt)
        self.client.addHandler(log_handler)
        self.server.addHandler(log_handler)

        self.client.info('Клиент инициализирован.')

    def connect(self, host: str, port: int) -> None:
        """Подключаемся к серверу."""
        self.client.info('Подключаемся к серверу.')
        for i in range(self.retries):
            try:
                self.sock.connect((host, port))
                self.client.info('Установлено соединение с сервером.')
            except (socket.timeout, OSError):
                self.client.info('Попытка {} не удалась, '
                                 'пробуем ещё раз.'.format(i))
                continue
            else:
                return
        raise SMTPException('Не удалось подключиться к серверу.')

    def send(self, content: bytes) -> None:
        """Отправляем серверу данное содержимое."""
        if self.encrypted:
            self.enc_sock.sendall(content + b'\r\n')
        else:
            self.sock.sendall(content + b'\r\n')

    def receive(self) -> bytes:
        """Получаем ответ сервера на отправленную команду."""
        for i in range(self.retries):
            try:
                answer = b''
                while not answer.endswith(b'\r\n'):
                    part = self.enc_sock.recv(1) if self.encrypted \
                        else self.sock.recv(1)
                    answer += part
                self.server.info(answer)
                return answer
            except socket.timeout:
                continue
        raise SMTPException('Не удалось получить ответ от сервера.')

    def hello(self) -> None:
        """Отправляем команду приветствия."""
        self.client.info('Отправляем приветствие серверу.')
        self.send(b'ehlo localhost')
        self.check_code(b'220')

    def start_tls(self) -> None:
        """Начинаем передачу по защищённому соединению."""
        self.client.info('Отправляем запрос на TLS-соединение.')
        self.send(b'starttls')
        while True:
            resp = self.receive()
            if not resp.startswith(b'250'):
                raise SMTPException('Возникла ошибка при установке '
                                    'защищённого соединения.')
            if resp.startswith(b'250 '):
                break
        resp = self.receive()
        if not resp.startswith(b'220'):
            raise SMTPException('Возникла ошибка при установке '
                                'защищённого соединения.')

    def wrap_socket(self) -> None:
        """Оборачиваем сокет в зашифрованный формат."""
        self.client.info('Сокет для защищённого соединения готов.')
        self.enc_sock = ssl.wrap_socket(self.sock,
                                        ssl_version=ssl.PROTOCOL_SSLv23)
        self.encrypted = True

    def encrypt(self) -> None:
        """
        Запрашиваем передачу данных по защищённому соединению и
        оборачиваем сокет.
        """
        self.start_tls()
        self.wrap_socket()

    def auth(self) -> None:
        """Запускаем процесс авторизации."""
        self.client.info('Отправляем запрос на авторизацию.')
        self.send(b'auth login')
        self.check_code(b'334')

    def login(self, login: str) -> None:
        """Отправляем логин для сервера."""
        self.client.info('Отправляем логин.')
        self.send(base64.b64encode(self.to_bytes(login)))
        self.check_code(b'334')

    def password(self, password: str) -> None:
        """Отправляем пароль для сервера."""
        self.client.info('Отправляем пароль.')
        self.send(base64.b64encode(self.to_bytes(password)))
        self.check_code(b'235')

    def authorize(self, login: str, password: str) -> None:
        """Авторизуемся на севрере."""
        self.auth()
        self.login(login)
        self.password(password)
        self.client.info('Авторизация на сервере успешна.')

    def mail_from(self, sender: str) -> None:
        """Отправляем серверу адрес отправителя."""
        self.client.info('Передаём адрес отправителя.')
        self.send(b'mail from: <' + self.to_bytes(sender) + b'>')
        resp = self.receive()

        if not resp.startswith(b'250'):
            raise SMTPException(resp)

    def mail_to(self, recipient: str) -> None:
        """Отправляем серверу адрес получателя."""
        self.client.info('Передаём адрес получателя')
        self.send(b'rcpt to: <' + self.to_bytes(recipient) + b'>')
        self.check_code(b'250')

    def data(self) -> None:
        """Начинаем передачу содержимого письма."""
        self.client.info('Сообщаем о начале передачи письма.')
        self.send(b'data')
        self.check_code(b'354')

    def letter(self, content: str) -> None:
        """Передаём серверу содержимое письма."""
        self.client.info('Передаём письмо.')
        self.send(self.to_bytes(content))
        self.send(b'.\r\n')
        self.check_code(b'250')

    def send_letter(self, content: str) -> None:
        """Отправляем письмо."""
        self.data()
        self.letter(content)
        self.client.info('Письмо отправлено.')

    def disconnect(self) -> None:
        """Закрываем соединение."""
        self.client.info('Закрываем соединение.')
        self.send(b'quit')
        self.sock.close()

    def check_code(self, ok_code: bytes) -> None:
        resp = self.receive()
        if not resp.startswith(ok_code):
            raise SMTPException(resp)

    @staticmethod
    def to_bytes(s: str) -> bytes:
        return s.encode('ascii')
