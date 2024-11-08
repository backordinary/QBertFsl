# https://github.com/ncitron/qiskit-hack/blob/d09ccf91e763621a6cb39b63bf58017d79d0b431/server.py
import os
import json
import asyncio
import websockets
import threading
from random import randint
from qiskit import *
from flask import Flask, send_from_directory

class Board:
    def place(self):
        arr = []
        for i in range(100):
            arr.append(0)
        arr = self.ship(arr, 5)
        arr = self.ship(arr, 4)
        arr = self.ship(arr, 3)
        arr = self.ship(arr, 3)
        arr = self.ship(arr, 2)        
        return arr
        
    def ship(self, array, length):
        nope = True
        while nope:
            head = randint(0, 99)
            orient = randint(0, 3)
            truf = self.check(head, length, orient, array)
            nope = not truf
        array = self.put(head, length, orient, array)
        return array
        
    def check(self, h, l, o, a):
        if a[h] != 0:
            return False
        if o == 0:
            end = h+(l-1)
            if (h - (h%10)) != (end - (end%10)):
                return False
            for i in range(l):
                if a[h+i] != 0:
                    return False
        elif o == 1:
            end = h - 10*(l-1)
            if end < 0:
                return False
            for i in range(l):
                if a[h - 10*i] != 0:
                    return False
        elif o == 2:
            end = h-(l-1)
            if (h - (h%10)) != (end - (end%10)):
                return False
            for i in range(l):
                if a[h-i] != 0:
                    return False
        elif o == 3:
            end = h + 10*(l-1)
            if end > 99:
                return False
            for i in range(l):
                if a[h + 10*i] != 0:
                    return False
        return True
    
    def put(self, h, l, o, a):
        if o == 0:
            for i in range(l):
                a[h+i] = 1
        elif o == 1:
            for i in range(l):
                a[h-10*i] = 1
        elif o == 2:
            for i in range(l):
                a[h-i] = 1
        elif o == 3:
            for i in range(l):
                a[h+10*i] = 1
        return a


class QuantComp:
    def __init__(self):
        print('created board')

    def setBoard(self, classical):
        self.classical = classical
        
    def convert(self, cboard):
        ret = []
        for i in range(len(cboard)):
            if cboard[i] == 1:
                hold = str(bin(i).replace("0b",""))
                while(len(hold) < 7):
                    hold = '0' + hold
                ret.append(hold)
        return ret
    
    def setup(self, array):
        tot = len(array)
        n = 7
        s = []
        for i in range(n-1):
            s.append(i)
        if tot > 8:
            rep = 2
        elif tot > 4:
            rep = 3
        elif tot == 4:
            rep = 4
        elif tot == 3:
            rep = 5
        elif tot == 2:
            rep = 6
        else:
            rep = 8
        return rep, n, tot, s
        
    def build_oracle(self, circuit, solutions, n, tot, s):
        for i in range(tot):
            temp = solutions[i]
            for j, yesno in enumerate(reversed(temp)):
                if yesno == '0':
                    circuit.x(j)
            circuit.h(n-1)
            circuit.mct(s, n-1)
            circuit.h(n-1)
            for k, noyes in enumerate(reversed(temp)):
                if noyes == '0':
                    circuit.x(k)
                    
    def amplify(self, circuit, n, s):
        circuit.h(range(n))
        circuit.x(range(n))
        circuit.h(n-1)
        circuit.mct(s, n-1)
        circuit.h(n-1)
        circuit.x(range(n))
        circuit.h(range(n))
        
    def guess(self):
        sol = self.convert(self.classical)
        rep, n, tot, s = self.setup(sol)
        qc = QuantumCircuit(n)
        qc.h(range(n))
        for i in range(rep):
            self.build_oracle(qc, sol, n, tot, s)
            self.amplify(qc, n, s)
        qc.measure_all()
        simulator = Aer.get_backend('qasm_simulator')
        stng = list(execute(qc, backend = simulator, shots = 1).result().get_counts().keys())[0]
        return int(stng, 2)

app = Flask(__name__, static_folder="./QuantumBattleship/build")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

q = QuantComp()
async def websocket_server(websocket, path):
    async for cmd in websocket:
        cmdDict = json.loads(cmd)
        print(cmdDict)
        #quantum bot
        if cmdDict['event'] == 'start':
            sep = ', '
            await websocket.send('{"event": "q-board", "quantumBoard": ' + str(Board().place()) + '}')
        if cmdDict['event'] == 'p-board':
            board = cmdDict['playerBoard']
            for i in range(0, len(board)):
                if board[i] == 3:
                    board[i] = 1
                else:
                    board[i] = 0
            q.setBoard(board)
        if cmdDict['event'] == 'turn':
            guess = q.guess()
            q.classical[guess] = 0
            await websocket.send('{"event": "guess", "target": ' + str(guess) + '}')


def thread():
    app.run(use_reloader=False, port=8080, threaded=True)

if __name__ == '__main__':
    threading.Thread(target=thread).start()
    start_server = websockets.serve(websocket_server, "localhost", 8081)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()