from __future__ import print_function
import time
from base import error_print, info_print, move_print, warn_print
import numpy as np
from .utils import binary_candidate_score_to_msg


def sample_candidate(weights):
    """Sample a candidate such that their score is not 1. Otherwise we would
    have solved the problem for the matchmaker.
    """

    n = len(weights)
    candidate = np.random.randint(0, 2, size=n)
    while np.isclose(np.dot(weights, candidate), 1):
        candidate = np.random.randint(0, 2, size=n)

    return candidate


class MatchMaker(object):
    def __init__(self, num_attr, true_weights, connect_sock):
        '''
        Send the initial set of 20 samples to M along with scores.
        This method also gets one guess from M and passes it along to P.

        num_attr - The number of attributes of candidates.
        true_weights - The true weights from the person.
        connect_sock - socket used for incoming connections.
        '''
        self.num_attr = num_attr
        self.time_taken = 0

        self.true_weights = true_weights

        self.connect_sock = connect_sock

        info_print('Waiting for Matchmaker (M) to connect')

        self.data_sock, _ = self.connect_sock.accept()

        info_print('Sent number of attributes to M')
        self.data_sock.sendall('%03d\n' % num_attr)

        # Msg sent to M, start clocking them
        start_time = time.time()

        info_print('Sending initial sample to M')
        self.send_initial_sample_set()
        self.weight_guess = self.recv_weights()

        move_print('Received weight guess %r' % self.weight_guess)
        t = time.time()
        self.time_taken += t - start_time
        self.report_time()

    def send_initial_sample_set(self):

        for i in range(20):
            candidate = sample_candidate(self.true_weights)
            score = np.dot(candidate, self.true_weights)
            msg = binary_candidate_score_to_msg(score, candidate)
            self.data_sock.sendall(msg)

    def report_time(self):
        warn_print('Matchmacker (M) has %f seconds left' %
                   (120 - self.time_taken))
        if self.time_taken > 120:
            error_print('Matchmaker (M) has exhausted his allotted time')
            self.loose()

    def recv_weights(self):
        info_print('Reading weights from M')
        # 7 chars for each weight, commas and one \n mark
        weight_string = self.data_sock.recv(7*self.num_attr +
                                            self.num_attr)
        info_print('Weights recieved are: %r' % weight_string)

        if not weight_string.endswith('\n'):
            error_print("Weights sent by M not truncated by '\\n'")
            self.loose()

        weight_string = weight_string[:-1]

        if ',' not in weight_string:
            error_print('Weights not delimited by comma')
            self.loose()

        weights = weight_string.split(',')

        for weight in weights:
            if len(weight) != 7:
                error_print('Each weight should be exactly 7 characters')
                error_print('Recevied a weight: %s' % weight)
                self.loose()

        try:
            weights = map(float, weights)
        except ValueError as e:
            error_print(e.args[0])
            self.loose()

        if len(weights) != self.num_attr:
            error_print('Expected %d weights but received %d' %
                        (self.num_attr, len(weights)))
            self.loose()

        weights = np.array(weights)
        if not np.all((0 <= weights) & (weights <= 1)):
            error_print('Weights have to be between 0 and 1')
            self.loose()

        weights = np.array(weights)
        return np.array(weights)

    def send_score(self, score):
        msg = '%+1.4f\n' % score
        self.data_sock.sendall(msg)

    def send_score_and_get_candidate(self, score):
        msg = '%+1.4f\n' % score
        self.data_sock.sendall(msg)
        move_print('Mathmacker got score %f' % score)
        start_time = time.time()

        self.weight_guess = self.recv_weights()
        move_print('Received weight guess %r' % self.weight_guess)
        t = time.time()
        self.time_taken += t - start_time
        self.report_time()

    def loose(self):
        error_print('M looses due to their mistake')
        exit(0)

    def win(self):
        move_print('Matchmacker Wins!')
        exit(0)
