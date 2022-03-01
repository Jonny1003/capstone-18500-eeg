import json
import websocket
import ssl
import logging

EMOTIV_SOCKET_URL = "wss://localhost:6868"
CREDS_LOC = "/Users/jonathanke/Documents/CMU/18500/credentials/neurocontroller_creds"
DEBUG = True
# TODO: find headset id
HEADSET_ID = "INSIGHT-A2D2029A"

# set of IDs for each cortex call
REQUEST_ACCESS_ID = 1
FIND_HEADSET_ID = 2
CONNECT_HEADSET_ID = 3
AUTHORIZE_ID = 4

# this file polls from the Emotiv CortexAPI and stores the relevant data into a buffer

class DataAcquirer(object):

    def __init__(self):
        # create a connection through sockets I/O to Emotiv API
        url = EMOTIV_SOCKET_URL
        self.connection = websocket.create_connection(url, sslopt={"cert_reqs": ssl.CERT_NONE})

        # application credentials
        self.id = None
        self.secret = None

    def do_api_call(self, req):
        self.connection.send(json.dumps(req))
        return json.loads(self.connection.recv())

    def requestAccess(self, creds_loc):
        '''
        creds_loc is the file location of creds
        '''
        if DEBUG:
            print("\nRequesting access to Emotiv API...\n")

        with open(creds_loc, 'r') as creds: 
            for line in creds.readlines():
                lineL  = line.split()
                if len(lineL) == 2:
                    name, value = lineL[0], lineL[1]
                    if name == 'client_id':
                        self.id = value
                    if name == 'client_secret':
                        self.secret = value 
            if not self.id:
                print("No client id found!")
                return 
            if not self.secret:
                print("No client secret found!")
                return 
            
            reqAccess = {
                "id": REQUEST_ACCESS_ID,
                "jsonrpc": "2.0",
                "method": "requestAccess",
                "params": {
                    "clientId": self.id,
                    "clientSecret": self.secret 
                }
            }
            resultDict = self.do_api_call(reqAccess)
            print(resultDict)
            if 'error' in resultDict:
                print("An error occured while requesting access...")
                print("Error:", resultDict['error'])
                return False
            else:
                if DEBUG:
                    print(resultDict['result']['message'])
                return resultDict['result']['accessGranted']

    def findHeadset(self):
        '''finds the particular headset we will be using'''
        if DEBUG:
            print("\nSearching and returning headset information...\n")

        req = {
            "id": FIND_HEADSET_ID,
            "jsonrpc": "2.0",
            "method": "queryHeadsets",
            "params": {
                "id": HEADSET_ID
            }
        }
        result = self.do_api_call(req)
        if 'error' in result:
            print("Error:", result['error'])
            return None
        elif len(result['result']) > 1 or len(result['result']) == 0:
            return None
        else:
            # the result should be there
            return result['result'][0]

    def connectHeadset(self):
        '''links to headset, returns true if successfully connected'''
        if DEBUG:
            print("\nConnect to headset...\n")
        req = {
            "id": CONNECT_HEADSET_ID,
            "jsonrpc": "2.0",
            "method": "controlDevice",
            "params": {
                "command": "connect",
                "headset": HEADSET_ID
            }
        }
        res = self.do_api_call(req)
        if 'error' in res:
            print("Error:", res['error'])
            return False
        elif 'warning' not in res:
            print("No connection information...")
            return False
        elif res['warning']['code'] != 104:
            print("Did not recieve code 104 in warning... Headset is not connected!")
            print("Warning:", res['warning'])
            return False
        else:
            if DEBUG:
                print(res['warning'])
            return True
    
    def authorize(self):
        '''
        authorizes this object to begin polling data,
        returns the cortex token if authorized, else None
        '''
        if DEBUG:
            print("\nAuthorizing...\n")
        if not self.id or not self.secret:
            print("No credentials sourced for this session... Please run requestAccess!")
            return None 
        req = {
            "id": AUTHORIZE_ID,
            "jsonrpc": "2.0",
            "method": "authorize",
            "params": {
                "clientId": self.id,
                "clientSecret": self.secret
            }
        } 
        res = self.do_api_call(req)
        if 'error' in res:
            print("Error:", res['error'])
            return None 
        elif 'result' not in res:
            print("Bad result:", res)
            return None
        else:
            if DEBUG and 'warning' in res['result']:
                print('Warning:', res['result']['warning'])
            return res['result']['cortexToken']

    







if DEBUG:
    logger = logging.getLogger('websockets')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
d = DataAcquirer()
print(d.requestAccess(CREDS_LOC))
print(d.findHeadset())
print(d.connectHeadset())
print(d.authorize())



