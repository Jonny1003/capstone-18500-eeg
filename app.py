from cortex.cortex import Cortex
from pydispatch import Dispatcher
from queue import Queue
import random
import threading
import joblib
import json
import numpy as np
import pandas
import time
from modeling.featurize import FEATURE_LIBRARY
import frontend.sandbox.keyboard as keyboard
import EMG.emg_combined

# get sklearn to stop printing warnings
import warnings
warnings.filterwarnings(action='ignore')

# this file is responsible for using Cortex to startup and poll data from headset


HEADSET_ID = "INSIGHT-A2D2029A"
CREDS_LOC = "/Users/jonathanke/Documents/CMU/18500/credentials/neurocontroller_creds"
DEBUG = False

MODEL_LOC_BASELINE_EVENT = "/Users/jonathanke/Documents/CMU/18500/modeling/event_kurtosis_lr.json"
MODEL_LOC_RIGHT_WINK = "/Users/jonathanke/Documents/CMU/18500/modeling/right_wink_lr.json"
MODEL_LOC_LEFT_WINK = "/Users/jonathanke/Documents/CMU/18500/modeling/left_wink_lr.json"
MODEL_LOC_NOISE_BASE = "/Users/jonathanke/Documents/CMU/18500/modeling/noise_vs_baseline_lr.json"
MODEL_LOC_NOISE_EVENT = "/Users/jonathanke/Documents/CMU/18500/modeling/detect_noise_lr.json"
MODEL_LOC_BLINK = "/Users/jonathanke/Documents/CMU/18500/modeling/detect_blink_lr.json"
MODEL_LOC_DOUBLE_BLINK = "/Users/jonathanke/Documents/CMU/18500/modeling/detect_double_blink_rf.json"

SAMPLES_PER_SEC = 128
NUM_SAMPLES_IN_3_SEC = SAMPLES_PER_SEC * 3
EVENTS = ('left_wink', 'right_wink', 'double_blink', 'blink', 'left_emg', 'right_emg')
EEG_LABELS = [
  "Timestamp", "EEG.AF3","EEG.T7","EEG.Pz","EEG.T8","EEG.AF4"
]

BLINKED_STATUS = 'blinked'
MODEL_STATUSES = [BLINKED_STATUS]


data_queue = Queue()
samples = [0]

event_queue = Queue()

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
    prev_val = None

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
        new_samples = pandas.DataFrame(new_samples, columns=EEG_LABELS)
        
        window = pandas.concat([window, new_samples])
        if len(window.index) > NUM_SAMPLES_IN_3_SEC:
            # start = window.index - NUM_SAMPLES_IN_3_SEC
            window = window.tail(NUM_SAMPLES_IN_3_SEC)

        res = model_predict(window)
        # print("Predicted: ", res)

        val = res
        if val != prev_val:
            print(val)
        if val in EVENTS and val != prev_val:
            dispatch.emit(val, val)
        else: 
            dispatch.emit('other', val)
        prev_val = val

def compute_feature_vector(model_params, window):
    vec = []
    for f in model_params['features']:
        vec.append((FEATURE_LIBRARY[f])(window))
    return np.array(vec).reshape(1,-1)

model_status = None 
model_status_timestamp = None

def initiate_model():
    '''create the final model here'''

    base = joblib.load(MODEL_LOC_BASELINE_EVENT.replace('.json', '.joblib'))
    right_wink = joblib.load(MODEL_LOC_RIGHT_WINK.replace('.json', '.joblib'))
    left_wink = joblib.load(MODEL_LOC_LEFT_WINK.replace('.json', '.joblib'))
    noise_base = joblib.load(MODEL_LOC_NOISE_BASE.replace('.json', '.joblib'))
    noise_event = joblib.load(MODEL_LOC_NOISE_EVENT.replace('.json', '.joblib'))
    blink = joblib.load(MODEL_LOC_BLINK.replace('.json', '.joblib'))
    double_blink =  joblib.load(MODEL_LOC_DOUBLE_BLINK.replace('.json', '.joblib'))



    base_F = open(MODEL_LOC_BASELINE_EVENT)
    right_wink_F = open(MODEL_LOC_RIGHT_WINK)
    left_wink_F = open(MODEL_LOC_LEFT_WINK)
    noise_base_F = open(MODEL_LOC_NOISE_BASE)
    noise_event_F = open(MODEL_LOC_NOISE_EVENT)
    blink_F = open(MODEL_LOC_BLINK)
    double_blink_F = open(MODEL_LOC_DOUBLE_BLINK)

    base_params = json.load(base_F)
    right_wink_params = json.load(right_wink_F)
    left_wink_params = json.load(left_wink_F)
    noise_base_params = json.load(noise_base_F)
    noise_event_params = json.load(noise_event_F)
    blink_params = json.load(blink_F)
    double_blink_params = json.load(double_blink_F)

    
    def model(window):
        # compute desired features
        v_base = compute_feature_vector(base_params, window)
        v_right = compute_feature_vector(right_wink_params, window)
        v_left = compute_feature_vector(left_wink_params, window)
        v_noise_event = compute_feature_vector(noise_event_params, window)
        v_blink = compute_feature_vector(blink_params, window)
        v_double_blink = compute_feature_vector(double_blink_params, window)

        # print(v_base)
        # print(v_right)
        # print(v_left)

        pred_noise_event = noise_event.predict(v_noise_event)
        if pred_noise_event[0] == 'noise':
            # too much noise to differentiate signals
            return 'noisy'
        elif model_status == BLINKED_STATUS:
            if time.time() > model_status_timestamp + 1:
                # over a second has passed we do not care about 
                # double blink anymore
                model_status = None 
                model_status_timestamp = None 
                return 'none'
            elif double_blink.predict(v_blink)[0] == 'double_blink':
                # double blink occured
                return 'double_blink'
        else:
            res1 = base.predict(v_base)
            # print(res1)
            if res1[0] == 'event':
                # an event occured, check for right wink
                R = right_wink.predict(v_right)
                L = left_wink.predict(v_left)
                single = blink.predict(v_blink)
                double = double_blink.predict(v_double_blink)
                print(R, L, double)
                if R[0] == 'right_wink':
                    return R[0]
                elif L[0] == 'left_wink':
                    return L[0]
                elif single[0] == 'blink':
                    model_status = BLINKED_STATUS
                    model_status_timestamp = time.time()
                    return 'none'

            return 'none'

    return model

def detectEMGThread(**kwargs):
    dispatch = kwargs.get('dispatch')
    bt = kwargs.get('bt')
    emg_params = kwargs.get('emg_params')
    stdR = emg_params[0]
    stdL = emg_params[1]
    aveR = emg_params[2]
    aveL = emg_params[3]
    EMG.emg_combined.detectEMG(dispatch, bt, stdR, stdL, aveR, aveL)


if __name__ == '__main__':

    # startup eeg
    model = initiate_model()
    cortex_instance = startup()

    # startup emg
    bt = EMG.emg_combined.start_bluetooth()
    emg_params = EMG.emg_combined.emgCalib(bt)

    # begin application
    dispatch = Dispatcher()
    
    for e in EVENTS:
        dispatch.register_event(e)
    dispatch.register_event('other')

    signalling_cond = threading.Condition()
    data_poll = threading.Thread(
        group=None, 
        target=setup_data_polling, 
        name='data_poll', 
        kwargs={'cortex':cortex_instance, 'cond':signalling_cond},
        daemon=True 
    )
    predictor = threading.Thread(
        group=None,
        target=do_predict, 
        name="predictor", 
        kwargs={'cond':signalling_cond, 'model':model, 'dispatch':dispatch},
        daemon=True
    )
    emg_detector = threading.Thread(
        group=None,
        target=detectEMGThread,
        name='emg detector',
        kwargs={'dispatch':dispatch, 'bt':bt, 'emg_params':emg_params},
        daemon=True
    )

    # begin executing threads
    data_poll.start()
    predictor.start()
    emg_detector.start()

    keyboard.main(dispatch, event_queue)

    data_poll.join()
    print("Cortex polling has exited! Terminating program...")