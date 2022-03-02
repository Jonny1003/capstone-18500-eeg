from time import sleep
from cortex import Cortex
from pydispatch import Dispatcher
from queue import Queue
import random

# this file is responsible for using Cortex to startup and poll data from headset


HEADSET_ID = "INSIGHT-A2D2029A"
CREDS_LOC = "/Users/jonathanke/Documents/CMU/18500/credentials/neurocontroller_creds"
DEBUG = True


def load_credentials(cred_loc):
    creds = dict()
    with open(cred_loc, 'r') as f:
        for line in f.readlines():
            L = line.split() 
            if len(L) == 2:
                creds[L[0]] = L[1]
    if 'client_id' not in creds or 'client_secret' not in creds or 'license' not in creds:
        print("Credentials incomplete!")
        return creds
    creds['debit'] = 0

    return creds 



def startup():
    print("starting up cortex ----------------------------")
    creds = load_credentials(CREDS_LOC)
    cortex_instance = Cortex(creds, debug_mode=DEBUG)
    if not cortex_instance.request_access():
        print("Cannot gain access to cortex API...")

    # TODO: fix this later...
    cortex_instance.do_prepare_steps()
    return cortex_instance

L = Queue()
ct = [0]


def forward_api_data(*args, **kwargs):
    data = kwargs.get('data')
    # if DEBUG:
    #     print(data)
    if ct[0] < 100:
        L.put(data)
    ct[0] += 1
    if ct[0] == 100:
        print('done!')
        while not L.empty():
            v = L.get()
            print(v)




def setup_data_polling(cortex_instance):
    cortex_instance.bind(new_eeg_data=forward_api_data)
    cortex_instance.sub_request(['eeg','dev','eq'])
    


instance = startup()
setup_data_polling(instance)




