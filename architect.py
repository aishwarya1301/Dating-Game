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
person.send_guess_and_get_update(matchmaker.weight_guess)
score = np.dot(matchmaker.weight_guess, person.weights)

for i in range(19):

    if np.isclose(score, 1):
        move_print('M won at round %d' % i)
        matchmaker.win()

    person.send_guess_and_get_update(matchmaker.weight_guess)
    score = np.dot(matchmaker.weight_guess, person.weights)
    best_score = max(best_score, score)
    matchmaker.send_score_and_get_candidate(score)

score = np.dot(matchmaker.weight_guess, person.weights)
matchmaker.send_score(score)
best_score = max(best_score, score)

move_print('Matchmacker score = %f' % best_score)
