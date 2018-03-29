import socket
import ssl
import base64


host, port = 'smtp.yandex.ru', 587

# CREATE SOCKET
sock = socket.socket()
sock.settimeout(10)

sock.connect((host, port))
sock.send(b'ehlo localhost\r\n')
print(sock.recv(1024))
sock.send(b'starttls\r\n')
print(sock.recv(1024))
print(sock.recv(1024))


# WRAP SOCKET
wrappedSocket = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv23)


wrappedSocket.send(b'auth login\r\n')
print(wrappedSocket.recv(1024))

wrappedSocket.send(base64.b64encode(b'pyt4on@yandex.ru') + b'\r\n')
print(wrappedSocket.recv(1024))

wrappedSocket.send(base64.b64encode(b'ylmqdrnndcwkesgz') + b'\r\n')
print(wrappedSocket.recv(1024))

wrappedSocket.send(b'mail from: pyt4on@yandex.ru\r\n')
print(wrappedSocket.recv(1024))

wrappedSocket.send(b'rcpt to: somebody@gmail.com\r\n')
print(wrappedSocket.recv(1024))

wrappedSocket.send(b'data\r\n')
print(wrappedSocket.recv(1024))

wrappedSocket.send(b'Date: Thu, 1 Apr 2048 05:33:29 -0700\nFrom: Sender <pyt4on@yandex.ru>\nSubject: New email'
                   b'\nTo: somebody@gmail.com\n\nText.\n.\r\n')
print(wrappedSocket.recv(1024))

wrappedSocket.close()
