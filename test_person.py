import socket
import sys
import numpy as np


PORT = int(sys.argv[1])


def get_valid_prob(n):
    alpha = np.random.random(n)
    p = np.random.dirichlet(alpha)
    p = np.round(p, 2)

    # ensure p sums to 1 after rounding
    p[-1] = 1 - np.sum(p[:-1])
    return p


def get_valid_weights(n):
    half = n/2

    a = np.zeros(n)
    a[:half] = get_valid_prob(half)
    a[half:] = -get_valid_prob(n - half)
    return np.around(a, 2)


def floats_to_msg(arr):
    'Convert float array to proper msg format'

    strings = []
    for a in arr:
        strings.append('%+01.2f' % a)
    msg = ','.join(strings) + '!'
    return msg


def candidate_to_msg(arr):
    'Convert a candidate to proper msg format'

    strings = []
    for a in arr:
        strings.append('%d' % a)
    msg = ','.join(strings) + '!'
    return msg


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', PORT))

num_string = sock.recv(4)
assert num_string.endswith('!')

num_attr = int(num_string[:-1])
initial_weights = get_valid_weights(num_attr)
ideal_candidate = initial_weights > 0
anti_ideal_candidate = initial_weights <= 0

sock.sendall(floats_to_msg(initial_weights))

sock.sendall(candidate_to_msg(ideal_candidate))
sock.sendall(candidate_to_msg(anti_ideal_candidate))
#data = sock.recv(1024)

sock.close()

