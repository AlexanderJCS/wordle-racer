# Import packages
import copy
import pickle
import socket
from string import ascii_lowercase

import enchant
from colorama import Fore, init

init(autoreset=True)
d = enchant.Dict("en_US")

# Read config file
SOLUTION_FILE = "solution_words.json"
SETTINGS_FILE = "settings.json"

EMPTY = "—"
HEADERSIZE = 10

# Connect to server
while True:
    IP = input("IP: ")
    PORT = int(input("PORT: "))
    USERNAME = input("USRENAME: ")

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        print("Successfully connected. Waiting for round to end.")
        break

    except (IOError, ValueError):
        print("Could not connect to server.")


# Class game
class Game:
    def __init__(self, width, height, solution_word):
        self.width = width
        self.board = [[EMPTY for _ in range(self.width)] for _ in range(height)]
        self.solution_word = solution_word

        self.correct_places = set()
        self.incorrect_places = set()
        self.wrong_letter = set()

        self.colored_board = []

    def run_game(self):  # Logic of the game
        while True:
            self.color_board()
            self.print_board()
            self.print_letters()
            self.input_word()

            # Check if won
            if won := self.win_check() is not None:
                if not won:
                    send("incomplete")
                    print(f"{Fore.RED}You lose!\n"*3)

                else:
                    send("found word")

                self.color_board()
                self.print_board()

                send(USERNAME)
                self.share()
                self.print_leaderboard()
                break

    def input_word(self):
        while True:
            # Allow the user to input a word
            user_word = input("Enter a word: ").lower()

            # Check if the word is valid
            if len(user_word) != self.width:
                print(f"{Fore.RED}Incorrect length")
                continue

            if not d.check(user_word):
                print(f"{Fore.RED}Not a real word")
                continue

            if list(user_word) in self.board:
                print(f"{Fore.RED}Word already given")
                continue
            break

        # Put user's guess in board
        for i, word in enumerate(self.board):
            if word[0] == EMPTY:
                self.board[i] = list(user_word)
                break

    def color_board(self):
        self.colored_board = copy.deepcopy(self.board)

        for y, word in enumerate(self.colored_board):
            solution_word_list = list(self.solution_word)

            # Check for letters in correct places
            for x, letter in enumerate(word):
                if solution_word_list[x] == letter:
                    self.colored_board[y][x] = Fore.GREEN + word[x]
                    solution_word_list[x] = ""

                    self.correct_places.add(letter)

                    if letter in self.incorrect_places:
                        self.incorrect_places.remove(letter)

            # Check for letters in incorrect places but still in the word
            for x, letter in enumerate(word):
                if letter in solution_word_list:
                    self.colored_board[y][x] = Fore.YELLOW + word[x]
                    solution_word_list[solution_word_list.index(letter)] = ""

            # Check for letters in incorrect places and not in the word
            for letter in word:
                condition1 = letter not in self.correct_places
                condition2 = letter not in self.incorrect_places
                condition3 = letter not in solution_word_list
                condition4 = letter != EMPTY

                if condition1 and condition2 and condition3 and condition4:
                    self.wrong_letter.add(letter)

    def print_board(self):  # Print the board
        print()
        for word in self.colored_board:
            for letter in word:
                print(letter, end=" ")
            print()

    def print_letters(self):
        # Print correct, incorrect, and wrong letters
        for letter in ascii_lowercase:
            color = ""
            if letter in self.correct_places:
                color = Fore.GREEN

            elif letter in self.incorrect_places:
                color = Fore.YELLOW

            elif letter in self.wrong_letter:
                color = Fore.RED

            print(f"{color}{letter.upper()}", end=" ")
        print()

    def win_check(self):
        for word in self.board:
            solution_list = list(self.solution_word)

            if word == solution_list:
                self.print_board()
                print(f"{Fore.GREEN}You win!\n"*3)
                return True

        return False if self.board[-1][-1] != EMPTY else None

    def share(self):
        print("Shareable emojis:")
        for word in self.colored_board:
            if word[0] == EMPTY:
                break

            for letter in word:
                if letter[:-1] == Fore.GREEN:
                    print("\N{Large Green Square}", end="")

                elif letter[:-1] == Fore.YELLOW:
                    print("\N{Large Yellow Square}", end="")

                else:
                    print("\N{Black Large Square}", end="")
            print()

    def print_leaderboard(self):
        print("Waiting for others to finish the wordle.")
        leaderboard = receive()
        print(f"The word was {self.solution_word}")
        leaderboard = dict((sorted(leaderboard.items(), key=lambda item: item[1])))  # Sort the dict

        for place, username in enumerate(leaderboard):
            print(f"#{place + 1}: {username} {round(leaderboard[username], 2)}")


def wait_for_gamestart():
    while True:
        if receive() == "game start":
            break

    dimensions = receive()
    solution_word = receive()

    return dimensions, solution_word


def receive():
    message_header = client_socket.recv(HEADERSIZE)
    message_length = int(message_header.decode('utf-8').strip())
    return pickle.loads(client_socket.recv(message_length))


def send(message):
    message = pickle.dumps(message)
    message = f"{len(message):<{HEADERSIZE}}".encode("utf-8") + message
    client_socket.send(message)


# Functions
def main():
    try:
        while True:
            dimensions, solution_word = wait_for_gamestart()

            g = Game(*dimensions, solution_word)
            g.run_game()

    except ConnectionResetError:
        print("Connection to server closed.")


if __name__ == "__main__":
    main()
