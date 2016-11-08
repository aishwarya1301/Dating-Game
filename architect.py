from dating import Person, MatchMaker
import sys
import numpy as np
import socket


ATTRIBUTES = 10
port = int(sys.argv[1])

connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#connect_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
connect_sock.bind(('localhost', port))
connect_sock.listen(2)

best_score = -np.inf
person = Person(ATTRIBUTES, connect_sock)

# Matchmaker is given training data and one guess is taken.
matchmaker = MatchMaker(ATTRIBUTES, person.weights, connect_sock)
person.send_guess_and_get_update(matchmaker.weight_guess)
score = np.dot(matchmaker.weight_guess, person.weights)

for i in range(19):

    if np.isclose(score, 1):
        matchmaker.win()

    person.send_guess_and_get_update(matchmaker.weight_guess)
    score = np.dot(matchmaker.weight_guess, person.weights)
    matchmaker.send_score_and_get_candidate(score)

matchmaker.send_score(score)
