import socket
import sys
import time
from datetime import datetime
import threading 
import random

def read_records(file_name):
    record_dict = {}
    with open(file_name,'r') as my_file:
         # convert the content in the file to the form of dictionary
         for line in my_file:
            line_each = line.strip().split()
            domain_name = line_each[0]
            type = line_each[1]
            data = line_each[2]
            if domain_name not in record_dict:
                record_dict[domain_name] = {}
            if type not in record_dict[domain_name]:
                record_dict[domain_name][type] = []
            if data not in record_dict[domain_name][type]:
                record_dict[domain_name][type].append(data)
    return record_dict

def get_other(qname,records):
    authority_part = []
    additional_part = []
    labels = qname.strip('.').split('.')
    domains = []
    for i in range(1, len(labels)):
        each_domain = '.'.join(labels[i:]) + '.'
        domains.append(each_domain)
    domains.append('.')
    # iterate all possible ancestor zone until find the closest one in records
    for every in domains:
        if every in records and "NS" in records[every]:
            # Copy all NS RRs for the zone into the authority section.
            for ns_record in records[every]["NS"]:
                authority_part.append(f"{every} NS {ns_record}\n")
                #copy known A records into the additional section for each ns 
                if ns_record in records and 'A' in records[ns_record]:
                    for a_record in records[ns_record]['A']:
                        additional_part.append(f"{ns_record} A {a_record}\n")
            return authority_part, additional_part
    return authority_part, additional_part


def response_msg(qid, qname, qtype, records):
    response_message = []
    response_message.append(f"ID: {qid}\n")
    response_message.append(f"QUESTION SECTION:\n{qname} {qtype}\n")
    find_CNAME = 0
    while True:
        find = False
        if qname in records:
            if "ANSWER SECTION:\n" not in response_message:
                 response_message.insert(2,"ANSWER SECTION:\n")
            for every_type in records[qname]:
                if every_type == qtype:
                    find = True
                    find_answer = records[qname][every_type]
                    for each_answer in find_answer:
                        response_message.append(f"{qname} {qtype} {each_answer}\n")
            #indicating qname is in records and have finished record all answers with corresponding required qtype
            if find :
                return  ''.join(response_message)
            # this case indicates using CNAME name to find the coresponding required answer
            for every_type in records[qname]:
                if every_type == 'CNAME':
                    find_CNAME = 1
                    # Each qname will map to a single CNAME 
                    response_message.append(f"{qname} {every_type} {records[qname][every_type][0]}\n")
                    qname = records[qname][every_type][0]
                    # start the new search using the cname name as the new qname
                    break
            # when qname is matched but qtype isn't matched, the current qtype is NS return None according to asmt specification
            if find_CNAME == 0 and 'NS' in records[qname]:
                return ''.join(['ID: 27795\n', 'QUESTION SECTION:\ncom. A\n'])
        else:
            # if match fails we have a referral.
            authority_part, additional_part = get_other(qname, records)
            if authority_part:
                response_message.append('AUTHORITY SECTION:\n')
                response_message.extend(authority_part)
            if additional_part:
                response_message.append('ADDITIONAL SECTION:\n')
                response_message.extend(additional_part)
            return ''.join(response_message)
            
def log_event(event, qid, qname, qtype, client_port, delay=0):
    # record on the server terminal
    if event == 'rcv':
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{current_time} {event} {client_port}: {qid} {qname} {qtype} (delay: {delay}s)"
        print(log_message)
    elif event == 'snd':
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"{current_time} {event} {client_port}: {qid} {qname} {qtype}"
        print(log_message)
    with open('server.log', 'a') as log_file:
        log_file.write(log_message + "\n")


def process_query(send_message, clientAddress, records, serverSocket):
    decoded_message = send_message.decode().strip().split()
    if len(decoded_message) != 4:
        return
    qname = decoded_message[1]
    qtype = decoded_message[2]
    qid = int(decoded_message[3])
    client_port = clientAddress[1]
    #simulate delay
    delay_time = random.randint(0, 4)
    log_event("rcv", qid, qname, qtype, client_port, delay_time)
    time.sleep(delay_time)
    response = response_msg(qid, qname, qtype, records)
    serverSocket.sendto(response.encode(), clientAddress)
    log_event("snd", qid, qname, qtype, client_port)


def server_main(port):
    records = read_records('master.txt')
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('localhost', port))
    while True:
        send_message, clientAddress = serverSocket.recvfrom(2048)
        threading.Thread(target=process_query, args=(send_message, clientAddress, records, serverSocket)).start()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Please enter: python server.py <port> ")
        sys.exit(1)
    
    port_num = int(sys.argv[1])
    server_main(port_num)
