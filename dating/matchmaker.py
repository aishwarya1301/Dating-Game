from __future__ import print_function
import socket
import time
from base import error_print, info_print, move_print, warn_print
import numpy as np


class MatchMaker(object):
    def __init__(self, num_attr, port):
        self.num_attr = num_attr
        self.time_taken = 0
        self.connect_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect_sock.bind(('localhost', port))
        self.connect_sock.listen(1)

        info_print('Waiting for Matchmaker (M) to connect on port %d' % port)
        self.data_sock, _ = self.connect_sock.accept()

        info_print('Sent number of attributes to M')
        self.data_sock.sendall('%03d!' % num_attr)

        # Sent the msg to Matchmaker, start clocking them.
        start_time = time.time()

    def send_initial_sample(self, sample, score):
