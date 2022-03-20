import json
import time
import random
import socket
import pickle
import logging
import threading

from string import ascii_lowercase

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)

IP = "192.168.1.12"
PORT = 1234

SOLUTION_FILE = "solution_words.json"
SETTINGS_FILE = "settings.json"

HEADERSIZE = 10

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))
server_socket.listen(10)

clients = []


class PreGame:
    def __init__(self):
        self.participating_clients = list(clients)
        self.width = None
        self.height = None
        self.word = None

    def run_pregame(self):
        self.get_settings()
        self.get_word()
        self.send_data()

    def get_settings(self):
        settings = read_file(SETTINGS_FILE)

        self.width = settings["board_width"]
        self.height = settings["board_height"]

    def get_word(self):
        if self.width > 1:
            try:
                # Read the solution words file
                with open(f"words/{self.width}.txt") as f:
                    words = f.read().splitlines()

                self.word = random.choice(words)

            except FileNotFoundError:
                logging.critical(f"File words/{self.width}.txt not found.")
                exit()

        else:
            self.word = random.choice(ascii_lowercase)

    def send_data(self):
        for client in self.participating_clients:
            send(client, "game start")
            send(client, (self.width, self.height))
            send(client, self.word)


class Game:
    def __init__(self):
        self.participating_clients = list(clients)
        self.times = {}

    def run_game(self):
        self.generate_leaderboard()
        self.send_leaderboard()

    def generate_leaderboard(self):
        start_time = time.time()

        for client in self.participating_clients:
            finished = receive(client)

            if not finished:
                continue

            username = receive(client)

            if finished == "found word":
                self.times[username] = time.time() - start_time

            else:
                self.times[username] = "Incomplete"

    def send_leaderboard(self):
        for client in self.participating_clients:
            send(client, self.times)


def manage_clients():
    logging.info("Waiting for clients to connect")
    while True:
        clientsocket, address = server_socket.accept()

        clients.append(clientsocket)
        logging.info(f"Client connected. {len(clients)} clients connected.")


def send(client_socket, message):
    logging.debug(f"Sending message {message}")
    try:
        message = pickle.dumps(message)
        message = f"{len(message):<{HEADERSIZE}}".encode("utf-8") + message
        client_socket.send(message)

    except ConnectionResetError:
        clients.remove(client_socket)
        logging.info("ConnectionResetError: Client disconnected when attempting to send data.")


def receive(client_socket):
    logging.debug("Receiving message")
    message_header = b""

    try:
        while len(message_header) < HEADERSIZE:
            read = client_socket.recv(HEADERSIZE - len(message_header))
            if not read:
                clients.remove(client_socket)
                logging.info("Client disconnected when attempting to receive data.")
                return
            message_header += read

        message_length = int(message_header.decode('utf-8').strip())
        return pickle.loads(client_socket.recv(message_length))

    except ConnectionResetError:
        logging.info("ConnectionResetError: Client disconnected when attempting to receive data.")


def read_file(filename):
    with open(filename, "r") as f:
        return json.load(f)


def main():
    # Start manage clients thread
    t = threading.Thread(target=manage_clients)
    t.start()

    while True:
        while len(clients) >= 1:
            # Run pregame
            pg = PreGame()
            pg.run_pregame()

            # Run game
            g = Game()
            g.run_game()

            time.sleep(3)  # Wait 3 seconds inbetween games


if __name__ == "__main__":
    main()
