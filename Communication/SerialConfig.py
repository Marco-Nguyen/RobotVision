import time

import serial


class SerialConfig():
    def __init__(self, com):
        super(SerialConfig, self).__init__()
        self.com = com
        self.available = True
        self.msg = "x: get\n"
        try:
            self.terminal = serial.Serial(self.com, baudrate=9600)
        except Exception as msg:
            print('[ERROR]', msg)
            try:
                print("[W] Serial have been opened in another app, try to restart...")
                self.terminal.close()
                self.terminal.open()
                print("[I] Done restarting")
            except Exception:
                print("[E] Can not restart serial, please close all relating app")
                self.available = False

    def get_data(self):
        '''send signal to arduino and get the line of value'''
        def is_float(x):
            try:
                float(x)
                return True
            except ValueError:
                return False
        if self.available:
            self.send_data("x: manual\n")

            self.send_data(self.msg)
            data = ""
            decode_data = " "
            t = time.time()
            cont = False
            while True:
                print('[I] Start reading...')
                # self.delay(2)
                try:
                    data = self.terminal.readline()
                    decode_data = str(data.decode("utf-8"))
                    print(decode_data)
                    if "y:" in decode_data or cont:
                        print('[I] Receive: ' + decode_data)
                        break
                    elif (time.time() - t >= 10):  # count 10s, if no response set time out
                        print('[I] Timeout...')
                        break
                    else:
                        self.send_data("x: manual\n")

                        self.send_data(self.msg)
                        pass
                except Exception:
                    self.send_data(self.msg)

            values = list(decode_data[3:].split(' '))
            try:
                values = list(
                    map(lambda x: None if not is_float(x) else float(x), values))
            except Exception:
                values = list(map(lambda x: str(x), values))

            return values[:6]
        else:
            return ['nan'] * 6

    def send_data(self, data):
        '''send signal to arduino'''
        if self.available:
            print("[I] Sent: ", end=' ')
            data = bytearray(data, 'utf-8')
            print(data)
            self.terminal.write(data)
            return True
        else:
            return False

    def delay(self, t):
        time.sleep(t)

    def stop(self):
        if self.available:
            print("Done sending")
            self.terminal.close()
