import socket
import threading


class ServerTerminal:
    to_send = True
    to_receive = True

    def __init__(self):
        self.sock = socket.socket()

    def send(self, message):
        self.conn.send(message.encode('utf-8'))

    def accept(self):
        self.sock.bind(('', 9090))
        self.sock.listen(1)
        self.conn, addr = self.sock.accept()
        print('connected:', addr)

    def receive(self):
        while self.to_receive:
            data = self.conn.recv(1024)
            print(data)

    def receiving(self):
        thread = threading.Thread(target=self.receive)
        self.to_receive = True
        thread.start()

    def sending(self):

        def ils():
            while self.to_send:
                self.send(input())

        thread = threading.Thread(target=ils)
        self.to_send = True
        thread.start()

    def start(self):
        self.receiving()
        self.sending()

    def close(self):
        self.conn.close()
        self.sock.close()


class ClientTerminal(ServerTerminal):

    def connect(self):
        self.sock.connect(('localhost', 9090))

    def send(self, message):
        self.sock.send(message.encode('utf-8'))

    def receive(self):
        # while self.to_receive:
        data = self.sock.recv(1024)
        print(data)

    def close(self):
        self.sock.close()


def main():
    ans = input('Server or client: ')
    while ans.lower() != 's' and ans.lower() != 'c':
        ans = input('Server or client: ')

    if ans.lower() == 's':
        terminal = ServerTerminal()
        terminal.accept()

    else:
        terminal = ClientTerminal()
        terminal.connect()

    terminal.start()


if __name__ == '__main__':
    main()
