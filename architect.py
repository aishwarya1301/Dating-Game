from dating import Person, MatchMaker
import sys
import numpy as np
import socket
from dating.base import move_print


ATTRIBUTES = 10
port = int(sys.argv[1])

connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect_sock.bind(('localhost', port))
connect_sock.listen(2)

best_score = -np.inf
person = Person(ATTRIBUTES, connect_sock)

# Matchmaker is given training data and one guess is taken.
matchmaker = MatchMaker(ATTRIBUTES, person.weights, connect_sock)
score = np.dot(matchmaker.weight_guess, person.weights)
best_score = max(best_score, score)
best_round = 0
person.send_guess_and_get_update(matchmaker.weight_guess)

for i in range(19):
    if np.isclose(score, 1):
        matchmaker.send_score(score)
        move_print('Matchmacker score = (%f, %d)' % (score, i + 1))
        matchmaker.win()
    else:
        score = np.dot(matchmaker.weight_guess, person.weights)
        if score > best_score:
            best_score = score
            best_round = i + 1
        matchmaker.send_score_and_get_candidate(score)
        person.send_guess_and_get_update(matchmaker.weight_guess)


matchmaker.send_score(score)
move_print('Matchmacker score = (%f, %d)' % (best_score, best_round + 1))
