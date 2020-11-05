from __future__ import print_function
import time
from .base import error_print, info_print, move_print, warn_print
import numpy as np
from .utils import floats_to_msg4


def float_formatter(x):
    return "%.4f" % x

np.set_printoptions(formatter={'float_kind': float_formatter})


class Person(object):
    def __init__(self, num_attr, connect_sock):
        """ Initilize Person (P).

        num_attr - The number of attributes of candidates.
        port - port on which to accept connections.
        connect_sock - socket used for incoming connections.
        """

        self.time_taken = 0
        self.num_attr = num_attr

        self.connect_sock = connect_sock

        info_print('Waiting for Person (P) to connect')

        self.data_sock, _ = self.connect_sock.accept()

        info_print('Sent number of attributes to P')
        self.data_sock.sendall('%03d\n' % num_attr)

        # Sent the msg to Person, start clocking them.
        start_time = time.time()

        self.initial_weights = self.recv_weights()
        self.initial_weights = self.handle_zeros(self.initial_weights)
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
            self.lose()

    def check_weight_and_candidates(self):
        ideal_mask = self.ideal_candidate.astype(np.bool)
        ideal_sum = np.sum(self.weights[ideal_mask])

        if not np.isclose(ideal_sum, 1):
            error_print('Ideal sum is not 1, but %f' % ideal_sum)
            self.lose()

        anti_ideal_mask = self.anti_ideal_candidate.astype(np.bool)
        anti_ideal_sum = np.sum(self.weights[anti_ideal_mask])

        if not np.isclose(anti_ideal_sum, -1):
            error_print('Anti-Ideal sum is not -1, but %f' % anti_ideal_sum)
            self.lose()

    def socket_recv(self, length):
        data = self.data_sock.recv(length)

        if len(data) != length:
            error_print('Weights received are ' + str(data)
                        + ' length (' + str(len(data))
                        + '), but expected ' + str(length))
            return None

        return data

    def recv_weights(self):

        info_print('Reading weights from P')
        # 6 chars for each weight: [+|-][0|1][.][0..9][0..9][,|\n]
        weight_string = self.socket_recv(6 * self.num_attr)

        info_print('Weights recieved are: %r' % weight_string)

        if weight_string is None: #Empty weights
            self.lose()

        if not weight_string.endswith('\n'): #Weights ntot terminated with \n
            error_print("Weights sent by P not truncated by '\\n'")
            self.lose()

        weight_string = weight_string[:-1]

        if ',' not in weight_string: #Weights not delimited by comma
            error_print('Weights not delimited by comma')
            self.lose()

        weights = weight_string.split(',')

        for weight in weights: #Each weight is a decimal with precion =2 and is signed
            if len(weight) != 5:
                error_print('Each weight should be exactly 5 characters')
                error_print('Recevied a weight: %s' % weight)
                self.lose()

        try: #Convert string weight to float weight
            weights = map(float, weights)
        except ValueError as e:
            error_print(e.args[0])
            self.lose()

        if len(weights) != self.num_attr: # num of Weights should be same as num of attributes 
            error_print('Expected %d weights but received %d' %
                        (self.num_attr, len(weights)))
            self.lose()

        weights = np.array(weights)
        positive_mask = weights > 0

        #All pos weights and neg weights should sum to 1 separately
        positive_sum = np.sum(weights[positive_mask])
        negative_sum = np.sum(weights[~positive_mask])

        if not np.isclose(positive_sum, 1):
            error_print('Sum of +ve weights should be 1, but is %f' %
                        positive_sum)
            self.lose()

        if not np.isclose(negative_sum, -1):
            error_print('Sum of -ve weights should be -1, but is %f' %
                        negative_sum)
            self.lose()

        return np.array(weights)

    def recv_candidate(self):

        info_print('Reading candidate from P')
        # 1 char per attribute, commas and \n
        cand_string = self.socket_recv(2 * self.num_attr)
        info_print('Candidate received is: %r' % cand_string)

        if cand_string is None:
            self.lose()

        if not cand_string.endswith('\n'):
            error_print("Weights sent by P not truncated by '\\n'")
            self.lose()

        cand_string = cand_string[:-1]

        if ',' not in cand_string:
            error_print('Candidate attributes not delimited by comma')
            self.lose()

        candidate = cand_string.split(',')

        for attribute in candidate:
            if attribute not in ['0', '1']:
                error_print('Each attribute should be either 0 or 1')
                error_print('Recevied an attribute: %s' % attribute)
                self.lose()

        try:
            candidate = map(int, candidate)
        except ValueError as e:
            error_print(e.args[0])
            self.lose()

        if len(candidate) != self.num_attr:
            error_print('Expected %d attributes but received %d' %
                        (self.num_attr, len(candidate)))
            self.lose()

        return np.array(candidate)

    def send_guess_and_get_update(self, weight_guess):
        info_print('Sending Ms guess to P')
        self.data_sock.send(floats_to_msg4(weight_guess))

        # Latest guess is sent. Time the Person to update weights
        start_time = time.time()
        weights = self.recv_weights()
        t = time.time()
        self.time_taken += t - start_time

        weights = self.handle_zeros(weights)
        delta_wegiths = weights - self.initial_weights
        percent_change = np.abs(delta_wegiths/self.initial_weights)
        # The result can contain only 2 significant digits.
        percent_change = (percent_change*100).astype(np.int)

        if np.any(percent_change > 20):
            error_print('Perecentage change cannot be more than 20%')
            self.lose()

        changed = ~np.isclose(delta_wegiths, 0)
        if np.count_nonzero(changed) > 0.05*self.num_attr:
            error_print('Only 5% of the weights can be changed.')
            self.lose()

        self.weights = weights
        move_print('P updated weights to %r' % self.weights)
        self.report_time()

    def lose(self):
        error_print('P loses due to their mistake')
        exit(0)

    def handle_zeros(self, arr):
        "replace 0s with a small number"
        zero_weights_idx = np.isclose(arr, 0)
        arr[zero_weights_idx] = 1e-8
        return arr
