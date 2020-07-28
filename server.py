
#!/usr/bin/python3
import socket
import select
import sys

host_name = socket.gethostname()
ip = socket.gethostbyname(host_name)
print("serveur chat room sur la machine", host_name, '({})'.format(ip))

IP="localhost"
PORT = 1459
HEADER_LENGTH = 2024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', PORT))
s.listen()
l = []
#dictionnaire de clients
Addr = {}
canaux = ["AA","BB","CC","DD"]
canaux2 = {"AA":[],"BB":[],"CC":[],"DD":[]}
Admin = {}
client_canal= {}
fichier={}
# pour ne pas bloquer la recv méthode
s.setblocking (False)

def QuelCanal(s2):#Cherche le canal actuel du client
    try:
        return client_canal.get(s2)
    except : s2.send("Not in a canal".encode())

def IsAdmin(canal, s2):
    return s2 in Admin.get(canal)
        
        
def SocketFromNick(Nick):
    for ii in Addr:
        if Addr.get(ii) == Nick:
            return ii

def LeaveCanal(s2,msg,uncanal):
    trouve = False
    if uncanal == "ALL":  #/LEAVE utilisateur quitte tous les c  
        Canal = []
        for i in canaux2:
            if s2 in canaux2.get(i):
                (canaux2.get(i)).remove(s2)
                if IsAdmin(i,s2):
                    Admin[i].remove(s2)
                    if Admin[i] == [] and canaux2.get(i) != []:
                        Admin[i] = [canaux2.get(i)[0]]
                        canaux2.get(i)[0].send("You are the new admin".encode()) #previent new admin   
                Canal += [i]
                trouve = True
        if trouve == True:
            for ii in Canal:
                if not canaux2.get(ii): 
                    canaux2.pop(ii)
                    canaux.remove(ii)
            s2.send("Canaux quitter".encode())        
            client_canal.pop(s2)
        else:
            s2.send("Vous devez d'abord rejoindre un canal".encode())
    else:#AVEC un nom de canal
        if canal in canaux:# verif au cas ou canal inexistant
            if IsAdmin(uncanal,s2):
                Admin[uncanal].remove(s2)
            canaux2.get(uncanal).remove(s2)
            client_canal.pop(s2)
            if Admin[uncanal] == [] and canaux2.get(uncanal) != []: #si la liste d'admin du canal est vide et que le canal est pas vide
                Admin[uncanal]=[canaux2.get(uncanal)[0]]
                canaux2.get(uncanal)[0].send("You are the new admin".encode()) #previent le nouvel admin
            if canaux2.get(uncanal) == []: #si le  canal est vide
                canaux2.pop(uncanal)
                canaux.remove(uncanal)
            s2.send(msg.encode())
            for i in canaux2:
                if s2 in canaux2.get(i):
                    client_canal[s2] = i			
                    break
        else:s2.send("Canal inexistant".encode())

def GestionNickName(string):
    Nick_Name1 = string[:-1]
    Nick_Name = Nick_Name1.replace("0","",1)
    trouve = False
    if Nick_Name != "None" and Nick_Name1[0] != "1" and Nick_Name!="" and Nick_Name[0]!=" ":
        if not (Addr):
            Addr[s2]=Nick_Name
            s2.send('Nick Name valide\n'.encode())		
        else:
            for i in list(Addr):				
                if Addr[i] == Nick_Name :
                    s2.send('Nick Name existe\n'.encode())
                    s2.send("Enter votre NICK Name: ".encode())
                    trouve = True
                    break	
            if trouve == False:				
                Addr[s2]=Nick_Name
                s2.send('Nick Name valide\n'.encode())											
    else:
        s2.send('Nick Name interdit\n'.encode())
        s2.send("Enter votre NICK Name: ".encode())			

def GestionAdmin(string,s2,action):#action : Grant ou revoke
    try:
        string_decode = string.split(" ",2) #Coupe message en 2
        client_priv = (string_decode[1])
        client_priv = client_priv[:len(client_priv)-1]
        if IsAdmin(QuelCanal(s2),s2) == True: #Si tu est admin
            sock = SocketFromNick(client_priv) #Alors tu recuperer le socket du nom donné
            CanalAdmin = QuelCanal(s2)#et tu recup le canal de l'admin pour plus tard donné ou enlevé le droit sur ce canal
            if CanalAdmin == QuelCanal(sock):
                if action == "REVOKE" and sock in Admin.get(CanalAdmin) and len(Admin.get(CanalAdmin)) != 1:
                    Admin.get(CanalAdmin).remove(sock)
                    msg = "You are not an admin anymore"
                    s2.send("Success".encode())
                    sock.send(msg.encode())
                elif action == "REVOKE": s2.send("Not an admin or last admin".encode())

                if action == "GRANT" and sock not in Admin.get(CanalAdmin):
                    Admin.get(CanalAdmin).append(sock)
                    msg = "You are an admin"
                    s2.send("Success".encode())
                    sock.send(msg.encode())
                elif action == "GRANT": s2.send("Already an admin".encode())		
                
            else:
                s2.send("Wrong canal / introuvable".encode())
    except:s2.send("Vous avez oublié un argument ou vous n'ête pas dans un canal".encode())
                
        
    
while True:
    r,_,_ = select.select(l + [s], [], [])
    for s2 in r:
        if s2 == s:
            s2, a = s.accept()
            print("nouveau client:", a)
            l = l + [s2]  #ajouter ce nouveau client_socket à notre sockets_list


            s2.send("Enter votre NICK Name: ".encode())		
                    

        else:
            string = s2.recv(HEADER_LENGTH).decode()            		

            if len(string) == 0 :
                print('le client {} déconnecté\n'.format(a))

                trouve = False       
                Canal = []
                for i in canaux2:
                    if s2 in canaux2.get(i):
                        (canaux2.get(i)).remove(s2)
                        if IsAdmin(i,s2):
                            Admin[i].remove(s2)
                            if Admin[i] == [] and canaux2.get(i) != []:
                                Admin[i] = [canaux2.get(i)[0]]
                                canaux2.get(i)[0].send("You are the new admin".encode()) #previent new admin   
                        Canal += [i]
                        trouve = True
                if trouve == True:
                    for ii in Canal:
                        if not canaux2.get(ii): 
                            canaux2.pop(ii)
                            canaux.remove(ii)
                      
                    client_canal.pop(s2)

                s2.close()
                l.remove(s2)
                Addr.pop(s2)		


            elif s2 not in Addr:
                GestionNickName(string)
                

            elif string[0:4] == "1BYE":
                trouve = False
                for i in canaux2: # On parcour les listes des canaux à la recherche de la personne
                    if s2 in canaux2.get(i):
                        trouve = True
                if trouve == True:#si on la trouve alors elle est dans un canal
                    s2.send("Vous ne pouvez pas utiliser cette commande il faut quitter le canal ".encode())
                    break
                else:#Elle n'est pas dans un canal elle peut partir		    
                    s2.close()
                    l.remove(s2)
                    Addr.pop(s2)
                    print('le client {} déconnecté\n'.format(a))		


            elif string[:len(string)-1] == "1HELP":
                string = ('/LIST: list all available channels on server\n/JOIN <channel>: join (or create) a channel\n/LEAVE: leave current channel\n/LEAVE <canal>: channel\n/LEAVE ALL: leave all channels\n/WHO: list users in current channel\n<message>: send a message in current channel\n/MSG <nick1;nick2;...> <message>: send a private message to several users in current channel\n/BYE: disconnect from server\n/KICK <nick>: kick user from current channel [admin]\n/REN <channel>: change the current channel name [admin]\n/NICK <nick>: change user nickname on server\n/GRANT <nick>: grant admin privileges to a user [admin]\n/REVOKE <nick>: revoke admin privileges [admin]\n')
                s2.send(string.encode())


            elif string[:len(string)-1] == "1LIST": 
                string = "Canaux disponibles : " 
                for canal in canaux: 
                    string += "\"" + canal + "\" " 
                s2.send(string.encode())	


            elif string[0:5] == "1JOIN":
                try:				
                    string_decode = string.split(" ",1)
                    can = (string_decode[1])
                    can = can[:len(can)-1]
                    InsideCanal = False
                    if can != "None" and can != "" and can !="ALL": #None et vide sont interdit      
                        if can in canaux :#le canal existe 
                            if s2 not in canaux2.get(can):#on verifie qu'elle n'est pas déja dans ce canal
                                (canaux2.get(can)).append(s2)#Ajout au canal
                                client_canal[s2]=can#mise à jour du canal actuel	
                            else: 
                                s2.send("Already in the canal".encode())		  
                        else:#le canal n'existe pas on le crée
                            canaux.append(can)#création canal
                            canaux2[can]=[s2] #insertion client dans canal
                            client_canal[s2]=can#mise à jour du canal actuel	                
                        if len(canaux2.get(can)) ==1:# si 1 seul personne dans le canal (nouveau canal)	il devient admin
                            Admin[can] = [s2]
                            s2.send("You are the admin".encode())								
                    else:
                        s2.send("None, ALL et nom vide interdit".encode())
                except:s2.send("Argument Vide".encode())
                

            elif string[:6] == "1LEAVE":#peut être utiliser avec ou sans parametres ex: /LEAVE ou /LEAVE AA	
                if len(string) > 7:#l'utilisateur à ecrit /LEAVE uncanal
                    string_decode = (string[:len(string)-1]).split(" ",1)
                    canal = string_decode[1]
                    if canal != "" and (canal in canaux or canal == "ALL") :
                        if canal != "ALL" and s2 in canaux2.get(canal):
                            LeaveCanal(s2,("Quitte le canal "+ canal),canal)
                        elif canal == "ALL":

                            LeaveCanal(s2,"Quitte les canaux","ALL")    
                        else:
                            msg= "Vous n'etes pas membre de ce canal!\n".encode()
                            s2.sendall(msg)
                    else:s2.send("Paramètre vide ou canal inexistant".encode())
                
                else:
                    try:
                        canal = QuelCanal(s2)
                        LeaveCanal(s2,("Quitte le canal "+ canal),canal)
                    except:s2.sendall("Vous devez être dans un canal".encode())
                    
                        

            elif string[:len(string)-1] == "1WHO":              
                    LeCanal = QuelCanal(s2)
                    if LeCanal != None:#Utilisateur dans un canal (None est interdit)
                        string='Liste des membres du canal : '
                        for sock in canaux2.get(LeCanal):
                            if IsAdmin(LeCanal, sock) == True:
                                string+=("\"@"+Addr.get(sock)+"@\" ")
                            else:	
                                string+=("\""+Addr.get(sock)+"\" ")
                        s2.send(string.encode())	
                    else: s2.send("Rejoindre un canal".encode())
                                
 
            elif string[0:5] == "1KICK":
                try:
                    string_decode = string.split(" ",2)
                    client_priv = (string_decode[1])
                    client_priv = client_priv[:len(client_priv)-1]
                    canal = QuelCanal(s2)
                    if IsAdmin(canal,s2) == True:
                        sock = SocketFromNick(client_priv)	
                        if sock in canaux2.get(canal):
                                msg = "You were kicked from " + canal
                                LeaveCanal(sock,msg,canal)                                  
                        else: s2.send("Introuvable".encode())	
                    else:	
                        s2.send("you are not an admin".encode())
                except:s2.send("You must be in a channel / you might have forgotten an argument".encode())		
                                   

            elif string[0:4] == "1REN":
                try:
                    string_decode = string.split(" ",1) 
                    NameNewChannel = (string_decode[1])
                    NameNewChannel = NameNewChannel[:len(NameNewChannel)-1] 
                    cann = QuelCanal(s2)
                    if IsAdmin(cann,s2) == True and NameNewChannel != "" and NameNewChannel != "None":
                        for ii in canaux:
                            if NameNewChannel == ii:
                                s2.send("ne pas renommer un canal si le nom existe déja\n".encode())
                                break
                        i = canaux.index(cann)
                        canaux[i]=NameNewChannel
                        for i in list(canaux2):
                            if s2 in canaux2.get(i) :
                                canaux2[NameNewChannel] = canaux2.pop(i)
                        for x in client_canal:#changer le nom du canal actuel
                            if client_canal.get(x) == cann:
                                client_canal[x] = NameNewChannel
                        Admin[NameNewChannel]=Admin.pop(cann)		#Renommer le dic d'admin		
                    else:
                        s2.send("you are not an admin or you used a forbiden name".encode())
                except:s2.send("You must be in a channel / you might have forgotten an argument".encode())	


            elif string[:len(string)-1] == "1ADMIN":
                    try : 
                        if IsAdmin((QuelCanal(s2)),s2) == True:
                            s2.send("you are an admin".encode())
                        else:
                            s2.send("you are not an admin\n".encode())
                    except : 
                        s2.send("Vous devez etre dans un canal\n".encode())


            elif string[0:4] == "1MSG":
                try:
                    string_decode = string.split(" ")
                    del string_decode[0]	
                    les_clients=string_decode[0]
                    string_decode2 = les_clients.split(";")
                    array_length = len(string_decode2)
                    del string_decode[0]
                    array_length2 = len(string_decode)
                    msg=''
                    for iii in range(array_length2):
                        msg += string_decode[iii] + " "#recupérer le msg
                    for ii in range(array_length) :
                        client_priv = (string_decode2[ii]) #recupérer le nom du client
                        trouve = False
                        Nicktrouve = False
                        for g in Addr:
                            if Addr.get(g) == client_priv:
                                Nicktrouve = True
                                for i in canaux2:
                                    if (s2 in canaux2.get(i)) == (g in canaux2.get(i)): #si les 2 sont dans le même canal
                                        trouve = True	
                                if trouve == True :
                                    g.send("{} >> {}".format(Addr.get(s2),msg).encode())
                                else:
                                    s2.send("Nickname pas dans votre canal / Vous devez etre dans un canal\n".encode()) 
                        if Nicktrouve == False :
                            s2.send("Nickname introuvable".encode())
                except:
                    s2.send("Erreur commande".encode())


            elif string[0:6] == "1GRANT":
                GestionAdmin(string,s2,"GRANT")


            elif string[0:7] == "1REVOKE":
                GestionAdmin(string,s2,"REVOKE")


            elif string[:8]=="1CURRENT":
                if len(string) > 9:
                    string_decode = (string[:len(string)-1]).split(" ",1)
                    canal = string_decode[1]
                    if canal != "" and canal in canaux:
                        if s2 in canaux2.get(canal):
                            client_canal[s2]=canal
                        else:
                            msg= "Vous n'etes pas membre de ce canal!\n".encode()
                            s2.sendall(msg)
                    else:s2.send("Parametre vide ou canal introuvable".encode())
                else:                   
                        if s2 in client_canal:
                            msg="Your current channel is: " + client_canal.get(s2)
                            s2.sendall(msg.encode())
                        
                        else:
                            msg= "Vous n'êtes pas membre d'un canal!\n".encode()
                            s2.sendall(msg)


            elif string[0:5] == "1SEND":
                try:
                    string_decode = string.split(" ",2)
                    client_priv = string_decode[1]
                    chemin = string_decode[2]
                    chemin = chemin[:len(chemin)-1] 	
                    for k in chemin:
                        chemin2 = chemin.replace("1", "/")				
                    trouve = False
                    Nicktrouve = False 
                    for g in Addr:
                        if Addr.get(g) == client_priv:
                            Nicktrouve = True
                            for i in canaux2:
                                if (s2 in canaux2.get(i)) == (g in canaux2.get(i)): #si les 2 sont dans le même canal
                                    trouve = True	
                            if trouve == True :
                                g.send("{} >> vous avez un fichier, pour le recevoir /RECV </path/to/file>\n".format(Addr.get(s2)).encode())
                                file = open(chemin2,'rb')
                                file_data = file.read(HEADER_LENGTH)
                                fichier[g] = file_data
                                file.close()
                            else:
                                s2.send("Nickname pas dans votre canal / Vous devez etre dans un canal\n".encode()) 
                    if Nicktrouve == False :
                        s2.send("Nickname introuvable".encode())
                except:			
                    s2.send("Erreur commande /SEND <nick> </path/to/file>\n".encode())	


            elif string[0:5] == "1RECV":
                #try:
                    string_decode = string.split(" ",1)
                    chemin = string_decode[1]
                    chemin = chemin[:len(chemin)-1] 
                    for k in chemin:
                        chemin2 = chemin.replace("1", "/")	
                    if s2 in fichier:
                        file_data = fichier[s2]
                        file = open(chemin2,'wb')
                        file.write(file_data)
                        #s2.send("fichier bien reçu\n".encode())		
                        file.close()
                        del fichier[s2]
                    else:
                        s2.send("vous n'avez pas un fichier".encode())    	
                #except:			
                #	s2.send("Erreur commande /RECV </path/to/file>\n".encode())	


            elif string[0:5] == "1NICK":
                try:
                    string_decode = string.split(" ",1) 
                    NewNick = (string_decode[1])
                    NewNick = NewNick[:len(NewNick)-1]
                    for g in Addr:
                        if Addr.get(g) == NewNick or NewNick == "None" or NewNick[0]==" " or NewNick[0] == "1":
                            s2.send("Nick_Name n'est pas bon".encode())                     
                        else:Addr[s2]=NewNick     
                                                   
                except:
                    s2.send("commande incomplet".encode())                  
    

            elif string[0]=="1":
                s2.send("Commande inconnu\n".encode())
                                    

            else:
                if s2 not in client_canal:
                    s2.send("voulez Vous rejoindre un canal: /HELP pour plus d'infos ".encode())
                else:
                    for s3 in canaux2.get(client_canal.get(s2)):
                        if s3 != s2:
                            Message = string.replace("0","",1)
                            s3.send("{}:{} >> {}".format(QuelCanal(s2),Addr.get(s2),Message[:len(Message)-1]).encode())

