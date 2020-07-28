
#!/usr/bin/python3
import socket
import select
import sys
import errno
import tty

IP="localhost"
PORT = 1459
HEADER_LENGTH = 1500

#création du socket :
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#envoi d'une requête de connexion au serveur :
try:
    client_socket.connect((IP, PORT))
except socket.error:
    print("La connexion a échoué.")
    sys.exit()        
print("<<<<<<<<<<<<<<<<<<<Bienvenu sur ce serveur chat room>>>>>>>>>>>>>>>>>>>")   

#sys.setraw(sys.stdin)

while True:

    r,_,_ =select.select([client_socket,sys.stdin] , [], [])
    
    for s2 in r:
        if s2 == sys.stdin:
            msg = sys.stdin.readline()
            if msg[0]=='/':
                msg2 = msg.replace("/", "1")       
            else:
                msg2 ='0'+msg    
            client_socket.send(msg2.encode())
            
        else:   
            string = s2.recv(HEADER_LENGTH).decode()
            print(string)
            if len(string) == 0:
                s2.close()
                sys.exit()
                break    
            
client_socket.close()

