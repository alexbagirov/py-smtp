from enum import Enum
import socket
import ssl
import base64


class State(Enum):
    """Возможные состояние клиента."""
    HELLO = 0


class SMTP(object):
    """Класс для общения с сервером и отправки писем."""
    def __init__(self, host: int, port: int) -> None:
        """Инициализируем клиент."""
        self.host = host
        self.port = port
        self.sock = socket.socket()
        self.sock.settimeout(10)
        self.retries = 3
        self.state = State.HELLO

    def connect(self) -> None:
        """Подключаемся к серверу."""
        for i in range(self.retries):
            try:
                self.sock.connect((self.host, self.port))
            except socket.timeout:
                continue
            else:
                return

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
        self.send(b'ehlo localhost')
        resp = self.receive().split()

        if int(resp[0]) != 250:
            raise Exception

    def start_tls(self) -> None:
        """Начинаем передачу по защищённому соединению."""
        self.send(b'starttls')
        resp = self.receive().split()
        resp2 = self.receive().split()

        if int(resp[0]) != 250 or not resp2:
            raise Exception

    def wrap_socket(self) -> None:
        """Оборачиваем сокет в зашифрованный формат."""
        self.sock = ssl.wrap_socket(self.sock, ssl_version=ssl.PROTOCOL_SSLv23)

    def auth(self) -> None:
        """Запускаем процесс авторизации."""
        self.send(b'auth login')
        resp = self.receive().split()

        if int(resp[0]) != 334:
            raise Exception

    def login(self, login: bytes) -> None:
        """Отправляем логин для сервера."""
        self.send(base64.b64encode(login))

        resp = self.receive().split()

        if int(resp[0]) != 334:
            raise Exception

    def password(self, password: bytes) -> None:
        """Отправляем логин для сервера."""
        self.send(base64.b64encode(password))

        resp = self.receive().split()

        if int(resp[0]) != 334:
            raise Exception

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
