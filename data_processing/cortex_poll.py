from concurrent.futures import thread
from re import L
from signal import signal
from time import sleep
from cortex import Cortex
from pydispatch import Dispatcher
from sklearn.linear_model import LogisticRegression
from queue import Queue
import random
import threading
import joblib
import json
import numpy as np
import keyboard_temp
import pandas
from featurize import FEATURE_LIBRARY

# get sklearn to stop printing warnings
import warnings
warnings.filterwarnings(action='ignore')

# this file is responsible for using Cortex to startup and poll data from headset


HEADSET_ID = "INSIGHT-A2D2029A"
CREDS_LOC = "/Users/jonathanke/Documents/CMU/18500/credentials/neurocontroller_creds"
DEBUG = False

MODEL_LOC_BASELINE_EVENT = "/Users/jonathanke/Documents/CMU/18500/modeling/sandbox/rf_model_var_peaks.joblib"
MODEL_LOC_RIGHT_WINK = "/Users/jonathanke/Documents/CMU/18500/modeling/sandbox/lr_model_right_wink.joblib"
MODEL_LOC_LEFT_WINK = "/Users/jonathanke/Documents/CMU/18500/modeling/sandbox/rf_model_left_wink.joblib"
SAMPLES_PER_SEC = 128
NUM_SAMPLES_IN_3_SEC = SAMPLES_PER_SEC * 3
EVENTS = ('left_wink', 'right_wink', 'double_blink', 'blink')

FEATURES = ['AF3_max', 'AF4_max',  
    'AF_adj_max_diff', 'AF_adj_max_ratio']
EEG_LABELS = [
  "Timestamp", "EEG.AF3","EEG.T7","EEG.Pz","EEG.T8","EEG.AF4"
]


data_queue = Queue()
samples = [0]

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


def forward_api_data(signalling_cond, data):
    if 'eeg' in data:
        eeg_data = [data['time']] + data['eeg'][2:7]
        samples[0] += 1
        data_queue.put(tuple(eeg_data))
        if DEBUG:
            print(data)
        #if samples[0] % NUM_SAMPLES_IN_3_SEC == 0:
        signalling_cond.acquire()
        signalling_cond.notify()
        signalling_cond.release()

def setup_data_polling(**kwargs):
    cortex_instance = kwargs['cortex']
    cond = kwargs['cond']
    def func(*args, **kwargs):
        data = kwargs.get('data')
        forward_api_data(cond, data)
    cortex_instance.bind(new_eeg_data=func)
    cortex_instance.sub_request(['eeg','dev','eq'])
    
def do_predict(**kwargs):
    model_predict = kwargs.get('model')
    signalling_cond = kwargs.get('cond')
    dispatch = kwargs.get('dispatch')

    window = pandas.DataFrame(columns=EEG_LABELS)

    while True:
        signalling_cond.acquire()
        signalling_cond.wait()
        signalling_cond.release()
        # begin model prediction

        # get data samples
        num_new_samples = data_queue.qsize()
        new_samples = []
        for _ in range(num_new_samples):
            d = data_queue.get()
            new_samples.append(d)
        # print(new_samples[0][0])
        new_samples = pandas.DataFrame(new_samples, columns=EEG_LABELS)
        
        window = pandas.concat([window, new_samples])
        if len(window.index) >= NUM_SAMPLES_IN_3_SEC:
            num_entries_to_drop = len(window.index) - NUM_SAMPLES_IN_3_SEC
            window = window.iloc[num_entries_to_drop:, :]

        # compute desired features
        vec1 = []
        for f in ['AF3_max', 'AF4_max']:
            vec1.append((FEATURE_LIBRARY[f])(window))

        vec2 = []
        for feature in FEATURES:
            vec2.append((FEATURE_LIBRARY[feature])(window))

        v1 = np.array(vec1).reshape(1, -1)
        v2 = np.array(vec2).reshape(1, -1)

        res = model_predict(v1, v2)
        print("Predicted: ", res)
        val = res[0]
        if val in EVENTS:
            dispatch.emit(val, val)
        else: 
            dispatch.emit('other', val)

def initiate_model():
    '''create the final model here'''
    base = joblib.load(MODEL_LOC_BASELINE_EVENT)
    right_wink = joblib.load(MODEL_LOC_RIGHT_WINK)
    left_wink = joblib.load(MODEL_LOC_LEFT_WINK)
    
    def model(vec1, vec2):
        res1 = base.predict(vec1)
        # print(res1)
        if res1[0] == 'event':
            # an event occured, check for right wink
            R = right_wink.predict(vec2)
            L = left_wink.predict(vec2)
            if R[0] == 'right_wink':
                return R[0]
            elif L[0] == 'left_wink':
                return L[0]
            return L[0]
        return 'none'

    return model

if __name__ == '__main__':
    model = initiate_model()
    instance = startup()

    dispatch = Dispatcher()
    
    for e in EVENTS:
        dispatch.register_event(e)
    dispatch.register_event('other')

    signalling_cond = threading.Condition()
    data_poll = threading.Thread(
        group=None, 
        target=setup_data_polling, 
        name='data_poll', 
        kwargs={'cortex':instance, 'cond':signalling_cond},
        daemon=True 
    )
    predictor = threading.Thread(
        group=None,
        target=do_predict, 
        name="predictor", 
        kwargs={'cond':signalling_cond, 'model':model, 'dispatch':dispatch},
        daemon=True
    )
    data_poll.start()
    predictor.start()

    keyboard_temp.main(dispatch)

    data_poll.join()
    print("Cortex polling has exited! Terminating program...")
    


    





