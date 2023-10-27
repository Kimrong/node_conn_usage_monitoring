import socket
import threading
import time
import tkinter as tk
from tqdm import tqdm
import psutil
import shutil

#parameters
HOST = "210.110.39.168"
PORT = 9999
SIZE = 2048
THR = 5
TIMEOUT = 5
HEART_BIT = "Are you alive?"
APPLY = "Yes I am alive"
node_sockets = []
CPU_THR = 70.
RAM_THR = 80.
DISK_THR = 80.

#monitor_socket config
monitor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
monitor_socket.bind((HOST,PORT))
monitor_socket.listen()

def time_stamp():
    lt = time.localtime(time.time())
    formatted = str(time.strftime("%Y.%m.%d %H:%M:%S ", lt))
    return formatted

def pop_up_warning(addr,count):
    window = tk.Tk()
    window.title("Node not applied!")
    window.geometry("400x200")
    
    text=f"{addr[0]}:{addr[1]} doesn't apply HEARTBIT {count} times"
    label1 = tk.Label(window,text=text,borderwidth=100)
    label1.pack()
    
    window.mainloop()
    return text

def usage_warning(cpu,ram,disk):
    global CPU_THR
    global RAM_THR
    global DISK_THR
    result = []
    
    if cpu>=CPU_THR:
        wanrning = f"CPU Usage Warning! {cpu}%"
        print(wanrning)
        result.append(wanrning)
    elif ram>=RAM_THR:
        wanrning = f"RAM Usage Warning! {cpu}%"
        print(wanrning)
        result.append(wanrning)
    elif disk>=DISK_THR:
        wanrning = f"DISK Usage Warning! {cpu}%"
        print(wanrning)
        result.append(wanrning)
    
    return result 

def node_call_back(node_socket,node_addr):
    global node_sockets
    global HEART_BIT
    global TIMEOUT
    global APPLY
    global SIZE
    global THR
    count=0
    print(f">> Connected by : {node_addr[0]}:{node_addr[1]}")
    loc = f"./log.{node_addr[0]}({node_addr[1]}).txt"
    node_socket.settimeout(TIMEOUT)
    with open(loc,'a') as f:
        while True:
            try:
                node_socket.send(HEART_BIT.encode())
                msg = node_socket.recv(SIZE).decode()
                count=0
                if msg[:len(APPLY)] != APPLY:
                    continue
                
                info = msg.split(',')
                cpu,ram,disk = info[1],info[2],info[3]
                lines=usage_warning(float(cpu),float(ram),float(disk))
                log = time_stamp()+f"CPU:{cpu}%,RAM:{ram}%,DISK:{disk}%\n"
                f.write(log)
                f.writelines(lines)
                                
            except TimeoutError as e:
                count+=1
                print(f"{count} Exception : {e} / {node_addr[0]}:{node_addr[1]}")
                log = time_stamp()+f"{node_addr[0]}:{node_addr[1]} doesn't apply HEARTBIT {count} times\n"
                f.write(log)
                if count == THR:
                    print(f">> Disconnected by : {node_addr[0]}:{node_addr[1]}")
                    log = time_stamp()+f"Disconnected by {node_addr[0]}:{node_addr[1]} (doesn't apply HEARTBIT {count} times)\n"
                    f.write(log)
                    break
            except ConnectionError as e:
                count+=1
                print(f"{count} Exception : {e} / {node_addr[0]}:{node_addr[1]}")
                log = time_stamp()+f"{node_addr[0]}:{node_addr[1]} doesn't apply HEARTBIT {count} times\n"
                f.write(log)
                if count == THR:
                    print(f">> Disconnected by : {node_addr[0]}:{node_addr[1]}")
                    log = time_stamp()+f"Disconnected by {node_addr[0]}:{node_addr[1]} (doesn't apply HEARTBIT {count} times)\n"
                    f.write(log)
                    break
            finally:
                time.sleep(1)
        
    if node_socket in node_sockets:
        node_sockets.remove(node_socket)
    node_socket.close()
    print(f"{node_addr[0]}:{node_addr[1]} Monitoring shutdown")

#connecting
if __name__ == "__main__":
    try:
        while True:
            node_socket, node_addr = monitor_socket.accept()
            node_sockets.append(node_socket)
            t = threading.Thread(target=node_call_back,args=(node_socket,node_addr))
            t.start()
    except Exception as e:
        print("Exception : ",e)
    finally:
        monitor_socket.close()