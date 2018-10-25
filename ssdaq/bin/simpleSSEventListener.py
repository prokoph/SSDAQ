from ssdaq.core import SSEventListener
import numpy as np
from matplotlib import pyplot as plt
import argparse

import signal
import sys


parser = argparse.ArgumentParser(description='Start a simple event data listener.',
                                formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument('-l', dest='listen_port', type=str,
                    default='5555',
                    help='port for incoming event data')

args = parser.parse_args()

ev_list = SSEventListener.SSEventListener(args.listen_port)
ev_list.start()

# def signal_handler(sig, frame):
        
#         ctrc_count +=1
    
#         ev_list.running=False
#         print('\npressed ctrl-C')
#         ev_list.CloseThread()
#         print("Closing listener")
#         raise RuntimeError

# signal.signal(signal.SIGINT, signal_handler)

event_counter = np.zeros(32)
n_modules_per_event =[]
n = 0
signal.alarm(0)
ctrc_count = 0
while(True):
    try:
        event = ev_list.GetEvent()
    except :
        print("\nClosing listener")
        ev_list.CloseThread()
        break

    print("Event number %d run number %d"%(event.event_number,event.run_number))
    m = event.timestamps[:,0]>0
    print(np.sum(m))
    print(np.where(m)[0])
    n_modules_per_event.append(np.sum(m))
    print((event.timestamps[m][0,0]*1e-9-event.timestamps[m][:,0]*1e-9))
    event_counter[m] += 1
    m = event_counter>0
    print(list(zip(np.where(m)[0],event_counter[m])))
    if(n>2000):
        break
    n +=1
plt.figure()
plt.hist(n_modules_per_event, 10,  facecolor='g', alpha=0.75)
plt.show()
ev_list.CloseThread()
ev_list.join()