# wordle-racer
Race your friends in wordle!

How to run the client:
1. Download the latest release
2. Download and extract client.zip
3. Run client_console.exe
4. Input the server IP, port (defualt is 1234), and your username

How to run the server:
1. Download Python (if there are any issues, download 3.9.10)
2. Open server.py in an IDE and edit the IP constant (at the top of the code) to your local ip
3. Run server.py (if you want others to join from the internet, you need to port forward)

How to configure game settings (server side only)
1. Open settings.json
2. Change the board width or height. If the board width is 1, it will automatically choose a random letter of the alphabet as a word.
3. If the width is not recognized as a key in solution_words.json, the server will crash.

How to configure solution words (server side only):
1. Add a key (if not already added) of the length of words you want to add
2. Create a list of all the words of that length
3. Add or remove words as you please