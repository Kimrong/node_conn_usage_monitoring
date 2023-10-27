import socket
import _thread
import time
import psutil
import shutil

#parameters
IP = "210.110.39.168"
PORT = 9999
SIZE = 2048
TIMEOUT=5
HEART_BIT = "Are you alive?"
APPLY = "Yes I am alive"
DISK_PATH = "c:\\"

#node_socket config
node_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
node_socket.connect((IP,PORT))
node_socket.settimeout(TIMEOUT)
print(f">> Connected to : {IP}:{PORT}")

try:
    while True:
        msg = node_socket.recv(SIZE).decode()
        if msg != HEART_BIT:
            continue

        #create info
        cpu = str(psutil.cpu_percent())
        ram = str(psutil.virtual_memory().percent)
        tot, use, free = shutil.disk_usage(DISK_PATH)
        disk_percent=str(round(use/tot*100,1))
        info = ""+APPLY+","+cpu+","+ram+","+disk_percent

        node_socket.send(info.encode())
        time.sleep(1)
except TimeoutError as e:
    print(f">> Disconnected to : {IP}:{PORT}")
except ConnectionError as e:
    print(f">> Disconnected to : {IP}:{PORT}")
except KeyboardInterrupt as e:
    print(f">> Disconnected to : {IP}:{PORT}")
finally:
    node_socket.close()
    print("Monitoring client shutdown")