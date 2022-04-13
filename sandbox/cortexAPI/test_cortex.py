from cortex.cortex import Cortex

if __name__ == '__main__':

    creds = open("neurocontroller_creds", 'r')
    license = None
    for line in creds.readlines():
        data = line.strip('\n').split()
        print(data)
        if 'client_id' in data:
            client_id = data[1]
        if 'client_secret' in data:
            client_secret = data[1]
        if 'license' in data:
            license = data[1]
    creds.close()

    print(client_id, client_secret, license)

    if (license == None):
        user = {
            "license" : "",
            "client_id" : client_id,
            "client_secret" : client_secret,
            "debit" : 100
        }
    else:
        user = {
            "license" : license,
            "client_id" : client_id,
            "client_secret" : client_secret,
            "debit" : 100
        }

    cortex_instance = Cortex(user, debug_mode=True)
    cortex_instance.get_cortex_info()
    cortex_instance.request_access()
    cortex_instance.authorize()

    cortex_instance.do_prepare_steps()
    
    info = cortex_instance.query_headset()
    print(info)

    # prepare_info = cortex_instance.do_prepare_steps()
    # print(prepare_info)


    
    #v = cortex_instance.connect_headset(42)
    # print("v:", v)

    # cortex_instance.create_session(user)
    cortex_instance.setup_profile('jon', 'load')
    cortex_instance.sub_request(["eeg", "mot", "dev", "eq", "pow", "met", "com",  "fac", "sys"])
    