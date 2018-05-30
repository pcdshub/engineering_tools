#!/usr/bin/env python

"""
2013-09-26 Awallace
This script is used to change the RS485 address of Pfeiffer turbo pumps using a digi port.
See help for basic usage.
"""




import argparse, socket

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--current_address", default='unknown', 
                    required=True, 
                    help="Required, current address number, type unknown and the script will attempt to find the pump and change it.",
                    metavar="Current Address",
                    dest='curr_addr')
parser.add_argument('-n', '--new_address', default='1',
                    required=True,
                    help="Required, new address number",
                    metavar="New Address",
                    dest='new_addr')
parser.add_argument('-v', action='store_true')



args = parser.parse_args()

def checksum(string):
    total = 0
    for char in string:
        total += ord(char)
    return format((total % 256),'03d')

def change_addr(curr, new, connection):
    message = format(int(curr), '03d')+'1079706000'+ format(int(new), '03d')
    cs = checksum(message)
    
    message = message + cs + '\r'
    if args.v:
        print 'Sending '+message
    connection.send(message)
    
    response = connection.recv(BUFFER_SIZE)
    if args.v:
        print response
    return response
    

def find_pump(connection):
    print "Searching for a pump, shouldn't take more than 5 minutes..."
    for i in range(1,256):
        message = format(i, '03d')+'0031202=?' 
        connection.send(message+checksum(message)+'\r')
        if args.v:
            print i
        try:
            received = connection.recv(BUFFER_SIZE) 
            if received:
                if args.v:
                    print "Found something"
                    print received
                break
        except socket.timeout:
            if args.v:
                print 'Timed out'
    if i == 256:
        print "Wasn't able to find a pump. Check your connections"
    else:
        print 'Found a pump @ '+str(i)
        
    return str(i)


TCP_IP = '172.21.37.29'
TCP_PORT = 2105
BUFFER_SIZE = 1024


if args.v:
    print args.curr_addr, args.new_addr

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.settimeout(10)

if args.curr_addr == 'unknown':
     args.curr_addr = find_pump(s)
     if args.v:
         print 'Found a pump at address: '+args.curr_addr


print 'Changing address from: '+args.curr_addr + ' to: ' + args.new_addr

change_addr(args.curr_addr, args.new_addr, s)

s.close()

