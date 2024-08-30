import socket
import sys
import random
def print_decoded(message):
    response_lines = message.splitlines()
    for each in response_lines:
        print(each)

def client_main(server_port, qname, qtype, timeout):
    server_address = 'localhost'
    server_addr = (server_address, server_port)
    #create an UDP socket
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientsocket.settimeout(timeout)
    try:
        qid = random.randint(0, 65535)
        query_message =  f'{server_port} {qname} {qtype} {qid} '
        clientsocket.sendto(query_message.encode(), server_addr)
        received_msg, addr = clientsocket.recvfrom(2048)
        decoded_msg = received_msg.decode()
        print_decoded(decoded_msg)
    except socket.timeout:
        print('timed out')
    finally:
        clientsocket.close()

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Please enter: python3 client.py <server_port> <qname> <qtype> <timeout>")
        sys.exit(1)
    server_port = int(sys.argv[1])
    qname  = str(sys.argv[2])
    qtype = str(sys.argv[3])
    timeout = int(sys.argv[4])

    client_main(server_port, qname, qtype, timeout)

