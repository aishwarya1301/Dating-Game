from __future__ import print_function
import socket
import time
from base import error_print, info_print, move_print, warn_print
import numpy as np


MAX_RECV = 4096


class Person(object):
    def __init__(self, num_attr, port):
        """ Initilize Person (P).

        num_attr - The number of attributes of candidates.
        port - port on which to accept connections.
        """

        self.time_taken = 0
        self.num_attr = num_attr
        self.connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_sock.bind(('localhost', port))
        self.connect_sock.listen(1)

        info_print('Waiting for Person (P) to connect on port %d' % port)
        self.data_sock, _ = self.connect_sock.accept()

        info_print('Sent number of attributes to P')
        self.data_sock.sendall('%03d!' % num_attr)

        # Sent the msg to Person, start clocking them.
        start_time = time.time()

        self.initial_weights = self.recv_weights()
        self.weights = self.initial_weights
        move_print('Inital Weights by P: %r' % self.initial_weights)

        self.ideal_candidate = self.recv_candidate()
        self.anti_ideal_candidate = self.recv_candidate()

        # Person replied, stop clocking them.
        self.time_taken += time.time() - start_time

        self.check_weight_and_candidates()
        move_print('Ideal Candidate %r' % self.ideal_candidate)
        move_print('Anti-Ideal Candidate %r' % self.anti_ideal_candidate)
        self.report_time()

    def report_time(self):
        warn_print('Person (P) has %f seconds left' % (120 - self.time_taken))
        if self.time_taken > 120:
            error_print('Person (P) has exhausted his allotted time')
            self.loose()

    def check_weight_and_candidates(self):
        ideal_mask = self.ideal_candidate.astype(np.bool)
        ideal_sum = np.sum(self.weights[ideal_mask])

        if not np.isclose(ideal_sum, 1):
            error_print('Ideal sum is not 1, but %f' % ideal_sum)
            self.loose()

        anti_ideal_mask = self.anti_ideal_candidate.astype(np.bool)
        anti_ideal_sum = np.sum(self.weights[anti_ideal_mask])

        if not np.isclose(anti_ideal_sum, -1):
            error_print('Anti-Ideal sum is not -1, but %f' % anti_ideal_sum)
            self.loose()

    def recv_weights(self):

        info_print('Reading weights from P')
        # 5 chars for each weight, commas and one ! mark
        weight_string = self.data_sock.recv(5*self.num_attr +
                                            self.num_attr)
        info_print('Weights recieved are: %r' % weight_string)

        if not weight_string.endswith('!'):
            error_print("Weights sent by P not truncated by '!'")
            self.loose()

        weight_string = weight_string[:-1]

        if ',' not in weight_string:
            error_print('Weights not delimited by comma')
            self.loose()

        weights = weight_string.split(',')

        for weight in weights:
            if len(weight) != 5:
                error_print('Each weight should be exactly 5 characters')
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
        positive_mask = weights > 0

        positive_sum = np.sum(weights[positive_mask])
        negative_sum = np.sum(weights[~positive_mask])

        if not np.isclose(positive_sum, 1):
            error_print('Sum of +ve weights should be 1, but is %f' %
                        positive_sum)
            self.loose()

        if not np.isclose(negative_sum, -1):
            error_print('Sum of -ve weights should be -1, but is %f' %
                        negative_sum)
            self.loose()

        return np.array(weights)

    def recv_candidate(self):

        info_print('Reading candidate from P')
        # 1 char per attribute, commas and !
        cand_string = self.data_sock.recv(2*self.num_attr)
        info_print('Candidate received is: %r' % cand_string)

        if not cand_string.endswith('!'):
            error_print("Weights sent by P not truncated by '!'")
            self.loose()

        cand_string = cand_string[:-1]

        if ',' not in cand_string:
            error_print('Candidate attributes not delimited by comma')
            self.loose()

        candidate = cand_string.split(',')

        for attribute in candidate:
            if attribute not in ['0', '1']:
                error_print('Each attribute should be either 0 or 1')
                error_print('Recevied an attribute: %s' % attribute)
                self.loose()

        try:
            candidate = map(int, candidate)
        except ValueError as e:
            error_print(e.args[0])
            self.loose()

        if len(candidate) != self.num_attr:
            error_print('Expected %d attributes but received %d' %
                        (self.num_attr, len(candidate)))
            self.loose()

        return np.array(candidate)

    def loose(self):
        error_print('P looses due to their mistake')
        exit(0)
