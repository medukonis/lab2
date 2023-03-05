##################################################
# Name:         Michael Edukonis
# UIN:          677141300
# email:        meduk2@illinois.edu
# class:        CS437
# assignment:   Lab2
# date:         3/3/2023
##################################################

import socket
import sys
import car

HOST = "192.168.1.2"    # IP address of your Raspberry PI
PORT = 65432            # Port to listen on (non-privileged ports are > 1023)


#############################################################
#Reusing Car object from previous lab with some new functions
#added. (car.py) This line is setting up an instance of the
#car oobject.#
#############################################################
car1 = car.Car()


#############################################################
#Setup of tcp socket. AF_INET means socket will use 32 bit
#IPv4 addresses and SOCK_STREAM is tcp connection vs udp DGRAM
#It is set to continually receive up tinstantiateo 1024 Bytes TODO:
#(need to make this dynamic for other things that are bigger
#like photos) Depending on what is received, a decision is
#made on what function to run in the car object.
#############################################################
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    while True:
        client, clientInfo = s.accept()
        print("server recv from: ", clientInfo)
        data = client.recv(1024)      # receive 1024 Bytes of message in binary format
        if not data:
            break
        command = data.decode('utf-8')
        print(command)
        if command =='f':
            car1.move_forward()
        elif command =='l':
            car1.turn_left(90)
        elif command == 'r':
            car1.turn_right(90)
        elif command == 'b':
            car1.back_up()
        elif command == 's':
            car1.stop()
        elif command == 'p':
            car1.take_pic()
        elif command == 'q':
            car1.scan()
        elif command == 'u':                #should see this being called every 5 seconds in terminal window
            print("update data")
            client.sendall(bytes(car1.get_car_readings(), encoding="utf-8"))
        else:
            print("unknown command")
