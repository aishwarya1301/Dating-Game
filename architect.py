from dating import Person, MatchMaker
import sys
import numpy as np
import socket
from dating.base import move_print, score_print


ATTRIBUTES = 10
port = int(sys.argv[1])

connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
connect_sock.bind(('localhost', port))
connect_sock.listen(2)

best_score = -np.inf
person = Person(ATTRIBUTES, connect_sock)

# #Round 1
# Matchmaker is given the training data and one guess is taken.
matchmaker = MatchMaker(ATTRIBUTES, person.weights, connect_sock)
score = np.dot(matchmaker.weight_guess, person.weights) #Matchmaker's 1st guess /dot Person's initial weights
best_score = max(best_score, score)
best_round = 1
#If matchmaker wins, declare winner -> send the guess to Person -> exit
if np.isclose(score, 1):
    matchmaker.send_score(score)
    move_print('Matchmacker Wins with score = %f at %dth guess' % (score, best_round))
    person.send_guess(matchmaker.weight_guess)
    matchmaker.win()
#else, send matchmaker's guess to Person and get updated weight for round 2
person.send_guess_and_get_update(matchmaker.weight_guess) #get person's updated weigths

#Round 2 begins
for i in range(2,21):
    matchmaker.send_score_and_get_candidate(score)
    #Calculate score : #Matchmaker's (2..20)th guess /dot Person's updated weights
    score = np.dot(matchmaker.weight_guess, person.weights)
    score_print("Matchmaker's %dth guess got %f score. " %(matchmaker.guess_num,score))
    if score > best_score:
        best_score = score
        best_round = i 
        score_print("Matchmacker's NEW best score = (%f, %d)" % (best_score, best_round))
    #Checking if Matchmaker has won
    if np.isclose(score, 1):
        matchmaker.send_score(score)
        move_print('Matchmacker Wins with score = %f at %dth guess' % (score, i))
        person.send_guess(matchmaker.weight_guess)
        matchmaker.win() #Exit
    #send matchmaker's guess to Person and get updated weight for next round
    person.send_guess_and_get_update(matchmaker.weight_guess)

#Send final score
matchmaker.send_score(score)
score_print("Matchmacker's best score = (%f, %d)" % (best_score, best_round))

