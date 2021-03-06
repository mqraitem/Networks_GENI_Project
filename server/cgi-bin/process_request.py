#!/usr/bin/python3

import cgi, os
import cgitb; cgitb.enable()
import socket
import time

workers_info = open('workers.txt', 'r') 
workers_info = workers_info.readlines() 
workers_info = [line.strip().split(',') for line in workers_info]

SLEEP_BETWEEN_REQUESTS = 2
MAX_ITERATIONS = 10

'''
recall: receive the message from the worker.
params: s: connection
'''
def recvall(s):
  End = '\n'
  data = ''
  while True:
    msg = s.recv(1024).decode()
    data += msg
    if End == msg[-1:]:
      break
  return data

'''
check_available: interpret the message from the worker.
params: resp_main: response message
'''
def check_available(resp_main): 
    msg = resp_main.strip('\n')
    if msg == '200 Busy': 
        return False
            
    if msg == '201 Free':
        return True 

form = cgi.FieldStorage()

fileitem = form['filename']
if fileitem.filename:
    
    fn = os.path.basename(fileitem.filename)
    open('images/' + fn, 'wb').write(fileitem.file.read())
    # Get the image from the client and store it in the local directory.
    connected_to_worker = False 
    iteration = 0
    # The server loop through workers to establish the connection with available worker.
    while (iteration < MAX_ITERATIONS) and (connected_to_worker == False):  
        for worker_idx, worker in enumerate(workers_info): 
            ip, port = worker 

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            connection = False 

            try: 
                s.connect((ip, int(port)))
                connection = True 
            except: 
                pass
            
            if connection: 
                msg_main = '100\n'
                s.sendall(msg_main.encode()) 
                resp_main = check_available(recvall(s))
                # The worker is available: send the image to the worker, and get the results back
                if resp_main:
                
                    imagepath = os.path.join('images', fileitem.filename)
                    image_to_send = open(imagepath, 'rb')    
                    image_to_send = image_to_send.read()
                    s.sendall(image_to_send)
                     
                    result = recvall(s) 
                    result = result.strip('\n')  
                    message = result + '\n,worker:%d'%(worker_idx)
                    connected_to_worker = True 
                
                s.shutdown(socket.SHUT_RDWR) 

            if connected_to_worker: 
                break

            time.sleep(SLEEP_BETWEEN_REQUESTS) 
        
        iteration += 1 

else:
    message = '<p>No file was uploaded<\p>'

if connected_to_worker == False: 
    message = '<p>Failure<\p>'

if len(message.split(',')) > 1: 
    message = message.split(',') 
    message = [line.split(':') for line in message]
    values = {item:key for item,key in message}
    message = '' 
    for item, key in values.items(): 
        message += '<p>%s: %s</p>\n'%(item, key)

# Return the result to the client.
print ("""\
      Content-Type: text/html\n
      <html>
      <body>
        <div style="text-align: center">
        <img src="http://pcvm4-3.instageni.colorado.edu:8080/images/%s">
        %s
        </div>
      </body>
      </html>
      """ % (fileitem.filename, message))
