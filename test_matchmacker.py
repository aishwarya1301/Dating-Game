import socket
import sys
import numpy as np
from dating.utils import floats_to_msg4


PORT = int(sys.argv[1])


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', PORT))

num_string = sock.recv(4)
assert num_string.endswith('\n')

num_attr = int(num_string[:-1])

for i in range(20):
    # score digits + binary labels + commas + exclamation
    data = sock.recv(8 + 2*num_attr)
    print('Score = %s' % data[:8])
    assert data[-1] == '\n'

for i in range(20):
    a = np.random.random(num_attr)
    sock.sendall(floats_to_msg4(a))

    data = sock.recv(8)
    assert data[-1] == '\n'
    score = float(data[:-1])
    print('i = %d score = %f' % (i, score))

sock.close()
