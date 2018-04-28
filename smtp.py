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
        self.encoding = 'ascii'

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

        self.client.info('Client initialized.')

    def __del__(self) -> None:
        self.sock.close()
        if self.enc_sock is not None:
            self.enc_sock.close()

    def connect(self, host: str, port: int) -> None:
        """Подключаемся к серверу."""
        self.client.info('Connecting to server.')
        for i in range(self.retries):
            try:
                self.sock.connect((host, port))
                self.client.info('Connected successfully.')
            except (socket.timeout, OSError):
                self.client.info('Attempt {} unsuccessful, '
                                 'retrying.'.format(i))
                continue
            else:
                return
        raise SMTPException('Server unavailable.')

    def send(self, content: (str, bytes), b64=False) -> None:
        """Отправляем серверу данное содержимое."""
        if b64:
            content = content + b'\r\n'
        else:
            content = self.to_bytes(content + '\r\n')

        if self.encrypted:
            self.enc_sock.sendall(content)
        else:
            self.sock.sendall(content)

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
        raise SMTPException('Server didn\'t send any response.')

    def hello(self) -> None:
        """Отправляем команду приветствия."""
        self.client.info('Sending greeting to server.')
        self.send('ehlo localhost')
        self.check_code(b'220')

    def start_tls(self) -> None:
        """Начинаем передачу по защищённому соединению."""
        self.client.info('Sending TLS connection request.')
        self.send('starttls')
        while True:
            resp = self.receive()
            if b'SMTPUTF8' in resp:
                self.encoding = 'utf-8'
            if not resp.startswith(b'250'):
                raise SMTPException('Unable to establish a secure connection.')
            if resp.startswith(b'250 '):
                break
        resp = self.receive()
        if not resp.startswith(b'220'):
            raise SMTPException('Unable to establish a secure connection.')

    def wrap_socket(self) -> None:
        """Оборачиваем сокет в зашифрованный формат."""
        self.client.info('Secure socket ready.')
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
        self.client.info('Sending auth request.')
        self.send('auth login')
        self.check_code(b'334')

    def login(self, login: str) -> None:
        """Отправляем логин для сервера."""
        self.client.info('Sending login.')
        self.send(base64.b64encode(self.to_bytes(login)), b64=True)
        self.check_code(b'334')

    def password(self, password: str) -> None:
        """Отправляем пароль для сервера."""
        self.client.info('Sending password.')
        self.send(base64.b64encode(self.to_bytes(password)), b64=True)
        self.check_code(b'235')

    def authorize(self, login: str, password: str) -> None:
        """Авторизуемся на севрере."""
        self.auth()
        self.login(login)
        self.password(password)
        self.client.info('Authorized successfully.')

    def mail_from(self, sender: str) -> None:
        """Отправляем серверу адрес отправителя."""
        self.client.info('Sending sender name.')
        self.send('mail from: <{}>'.format(sender))
        resp = self.receive()

        if not resp.startswith(b'250'):
            raise SMTPException(resp)

    def mail_to(self, recipient: str) -> None:
        """Отправляем серверу адрес получателя."""
        self.client.info('Sending recipient name')
        self.send('rcpt to: <{}>'.format(recipient))
        self.check_code(b'250')

    def data(self) -> None:
        """Начинаем передачу содержимого письма."""
        self.client.info('Starting data transfer.')
        self.send('data')
        self.check_code(b'354')

    def letter(self, content: str) -> None:
        """Передаём серверу содержимое письма."""
        self.client.info('Sending the letter.')
        self.send(content)
        self.send('.\r\n')
        self.check_code(b'250')

    def send_letter(self, content: str) -> None:
        """Отправляем письмо."""
        self.data()
        self.letter(content)
        self.client.info('Mail sent successfully.')

    def disconnect(self) -> None:
        """Закрываем соединение."""
        self.client.info('Closing connection.')
        self.send('quit')
        self.sock.close()

    def check_code(self, ok_code: bytes) -> None:
        resp = self.receive()
        if not resp.startswith(ok_code):
            raise SMTPException(resp)

    def to_bytes(self, s: str) -> bytes:
        return s.encode(self.encoding)
