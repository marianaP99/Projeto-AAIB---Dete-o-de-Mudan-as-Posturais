import time
import json
import socket
import numpy as np


print ('The begin ...')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    host = "192.168.1.135" #put here the ip address of your mobile
    port = 4242
    
    acq = input('Number of acquisition: ') 
    mov = input('Which movement is done in this acquisition? (f, b, l, r, o) ')
    ind = input('Number of individual: ')
    filename = 'acquisitions/acq_' + acq.zfill(3) + '_' + ind + '_' + mov 

    Tc = 60 # Período de aquisição 
    t0 = 5000 # Tempo de aquisição
    sample = t0 // Tc
    start = input("Start acquisition? y/n ")
    
    if start == 'y':
        print('Opening socket')
        s.connect((host, port))
        print('connected')
        f=open(filename+'.csv', 'w')
        for n in range(sample):
            #time.sleep(0.025)
            data = s.recv(256)
            if data:
                decoded_data = data.decode("utf-8").split("\n")
                for msg in decoded_data:
                    try:
                        package = json.loads(msg)
                        # print(package)
                        t=package["accelerometer"]["timestamp"]
                        acc=package["accelerometer"]["value"]
                        gyro=package["gyroscope"]["value"]
                        a = str(t)+','+str(acc[0])+','+str(acc[1])+','+str(acc[2])+','+str(gyro[0])+','+str(gyro[1])+','+str(gyro[2])
                        print(n)
                        f.write(a+'\n')
    
    
                    except:
                        continue
    
    
        f.close()
        s.close()   
        print('socket closed') 
        
print ('... end')
