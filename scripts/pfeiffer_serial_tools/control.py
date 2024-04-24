#!/usr/bin/env python

"""
2013-09-26 Awallace
This script is used to change the RS485 address of Pfeiffer turbo pumps using a digi port.
See help for basic usage.
2024-04-24 roberttk
converted to py3.9
"""
import argparse
import socket
import time

TCP_IP = '172.21.37.29'
TCP_PORT = 2105
BUFFER_SIZE = 1024


def est_connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.settimeout(10)
    return s


def close_conn(connection):
    connection.close()
    return


def checksum(string):
    total = 0
    for char in string:
        total += ord(char)
    return format((total % 256), '03d')


def c_pmp(control_code, control_parameter, connection, address='1'):
    message = (format(int(address), '03d') + '10' + control_code
               + format(len(control_parameter), '02d') + control_parameter)
    print('Sending ' + message)
    connection.send(message + checksum(message) + '\r')
    try:
        response = connection.recv(BUFFER_SIZE)
    except socket.timeout:
        print('Timeout')
    return str(response)


def q_pmp(query_code, connection, address='1'):
    message = format(int(address), '03d') + '00' + str(query_code) + '02' + '=?'
    cs = checksum(message)

    message = message + cs + '\r'
    connection.send(message + checksum(message) + '\r')
    try:
        response = connection.recv(BUFFER_SIZE)
    except socket.timeout:
        print('Timeout')
    return response


def run_pmp(connection, address='1'):
    c_pmp('010', '111111', connection, address)


def stop_pmp(connection, address='1'):
    c_pmp('010', '000000', connection, address)


def pump_spd(connection, address='1'):
    s = q_pmp(309, connection, address)
    print(s[10:16] + ' Hz')


def pump_pwr(connection, address='1'):
    s = q_pmp(316, connection, address)
    print(s[10:16] + ' W')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--current_address", default='unknown',
                        required=True,
                        help="Address of the pump to control/ query",
                        metavar="Current Address",
                        dest='curr_addr')
    parser.add_argument('-v', action='store_true')
    parser.add_argument('-r', action='store_true')
    parser.add_argument('-s', action='store_true')
    parser.add_argument('-spd', action='store_true')
    parser.add_argument('-pwr', action='store_true')
    parser.add_argument('-mon', action='store_true')
    args = parser.parse_args()

    conn1 = est_connect()

    if args.s:
        stop_pmp(conn1, args.curr_addr)
    elif args.spd:
        pump_spd(conn1, args.curr_addr)
    elif args.pwr:
        pump_pwr(conn1, args.curr_addr)
    elif args.mon:
        while True:
            pump_spd(conn1, args.curr_addr)
            pump_pwr(conn1, args.curr_addr)
            time.sleep(1)
    elif args.r:
        run_pmp(conn1, args.curr_addr)

    close_conn(conn1)
