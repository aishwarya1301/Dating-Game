# Dating Game architecture
[Dating game](https://cs.nyu.edu/courses/fall20/CSCI-GA.2965-001/) architecture for the Heuristic Problem Solving course at NYU (Fall 2020)

# Running
The `architect.py` file is the main entry point for starting the game. Execute the following in a shell to start it.
```shell
python2 architect.py <PORT-NO>
```
Change the variable `ATTRIBUTES` which is defined inside `architect.py` file to change the number of attributes each candidate can have.
The test scripts can be executed by
```shell
python2 test_person.py <PORT-NO>
python2 test_matchmaker.py <PORT-NO>
```

# Sequence of actions
1. The architect communicates the number of attributs (`n`) to Person (P) via socket.
2. P responds with a vector `w`, of length `n` whose positive components sum to `1` and negative components sum to `-1` and
sends it to the architect who verifies it. P also sends 2 binary arrays indicating the ideal and anti-ideal candidate which
are also verified.
3. The architect communicates `n` via socket to Matchmacker (M).
4. The architect computes the dot product of the `s_i = (w.x_i)` for `1 <= i <= 20` where `x_i` is a binary random
vector. Architect then sends all 20 `s_i` and `x_i` to M.
5. For 20 turns
  1. M guesses some `x`, such that all components of `x` are between `0` and `1`.
  2. Architect computes `s = w.x`, and stores `s`. It then sends `x` to P.
  3. P modifies `w`, while not deviating more than 20% from the initial value of `w` and changing only 5% of the weights.
  4. Architect sends `s` to M and requests for a new `x`.
The architect records the best score `s`, and if it was ever 1, it records the number of turns taken.


# Communication
TCP/IP communication is not guaranteed to be atomic. To resolve this issue we have fixed the message length of every message
over the socket, so that every `read` call is guaranteed to contain the entire message sent. We use `,` to seperate values
and `\n` to denote end of a message.

## Person (P)
1. At the start receives exactly 4 characters. The last character is `\n` and the first 3 characters are digits which denote
`n`, the number of attributes.  For example

  ```
  056\n
  ```

2. The architect then expects a response containing exactly, `6n` characters, denoting the initial set of weights. Each
component of the weight vector should contain, a +/- sign, followed by one digit before the decimal and 2 digits after
the decimal. If you are not using any digits, you should set them to `0`. Components are separated by `,` and `\n` denotes
the end of the message. For example, for `n=5`.

  ```
  +0.20,+0.80,-0.68,-0.00,-0.32\n
  ```
You can use the `dating/utils.py:floats_to_msg2` function to do so.
3. The architect then expects the ideal and anti-ideal candidates, with the ideal candidate expected first. Each candidate
is exactly `2n` characters of 0 or 1. For example

  ```
  0,1,1,0,0\n
  ```
4. Subsequently the Person will receive 20 guesses made by Matchmaker over time, each of which will contain `8n` characters.
Each component will have a +/- sign, followed by one digit before the decimal and 4 digits after the decimal. For example

  ```
  +0.2303,+0.8095,+0.1366,+0.9295,+0.4915\n
  ```
5. For each of the 20 candidate proposed by the matchmaker, the person has to reply with modified weights with 20% of the
original weights from step 2 and only 5% of them changed. Once again, the weights should be communicated by exactly `6n` characters.

## Matchmaker (M)
1. Same as person, receives n, via exactly 4 characters.
2. Immediately after that, M receives 20 binary vectors along with their scores. Each (score, vector) tuple is exactly
(2n + 8) characters long. The first 8 characters are the score, followed by a `:`, followed by a comma separated binary vector. For example

  ```
  +0.9900:1,1,0,0,1\n
  ```
3. M is expected to give an estimate of weights during each of the 20 iterations. The architect expects a message of exactly
`8n` characters, where each component contains one digit before the decimal and 4 digits after the decimal. For example

  ```
  +0.3038,+0.1525,+0.9334,+0.6368,+0.4921\n
  ```
  See function `dating/utils.py:floats_to_msg4`
4. After sending an estimate, M will receive a score, of exactly 8 characters. For example

  ```
  +0.1356\n
  ```

# Submission Format

Compress all your files into a single zip archive called `teamname.zip`. Make sure it has 2 bash files `teamname_player.sh` and
`teamname_matchmaker.sh`. Please load all your modules you need in your bash files. The bash files will be called as follows
```shell
bash teamname_player.sh <PORT-NO>
bash teamname_matchmaker.sh <PORT-NO>
```
Send all your submissions to `arajan@nyu.edu`
You can also send in any queries to `pg1899@nyu.edu`