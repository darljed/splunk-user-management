from datetime import datetime
import http.client
import os, sys, csv, json, ssl
import base64
from getpass import getpass


# add users -  completed
# update roles of existing Users - completed


class Users:
    def __init__(self,filename):
        self.config_file = 'config.json'
        self.location = os.path.dirname(__file__)
        self.getConfig()
        
        self.filename = filename
        self.logger('',begin=True)
        self.conn = self.connection()

        self.headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': self.auth
        }

        self.main()

    def getListFile(self):
        userslist = os.path.join(self.location,self.filename)
        if( os.path.exists(userslist)):
            
            f = open(userslist,"r")
            csvReader = csv.DictReader(f)
            return csvReader
        else:
            self.logger(f'file {userslist} doesn\'t exists.')
            return False
    
    def deleteUser(self,user):
        # @user => string
        self.logger(str("Delete user: "+user))
        endpoint = f"/services/authentication/users/{user}"
        
        res = self.make_request('DELETE', endpoint,None)
        if res:
            self.logger(f"user {user} has been deleted.")
        else:
            self.logger('unable to process request.')



    def createUser(self,data):
        # @data => Dict
        self.logger(json.dumps(data))
        endpoint = "/services/authentication/users"
        roles = data.get('roles').split(",")
        default_app = data.get('default_app')
        temp_pass = data.get('temp_pass')
        id = data.get('id')
        rolelist = ""
        for role in roles:
            rolelist += f"&roles={role}"
        payload = f'force-change-pass=true&name={id}&password={temp_pass}{rolelist}&defaultApp={default_app}'

        res = self.make_request('POST',endpoint,payload)
        if res:
            self.logger(f"user {id} has been created.")
        else:
            self.logger(f"unable to process request")

    def updateUser(self,data):
        self.logger(json.dumps(data))
        # @data => Dict

        id = data.get('id')
        endpoint = f"/services/authentication/users/{data.get('id')}"
        roles = data.get('roles').split(",")
        rolelist = ""
        for role in roles:
            rolelist += f"&roles={role}"
        temp_pass = "force-change-pass=true&password=" + data.get('temp_pass') if data.get('temp_pass') else ''
        default_app = '&defaultApp='+data.get('default_app') if data.get('default_app') else ''
        payload = f'{temp_pass}{rolelist}{default_app}'

        res = self.make_request('POST',endpoint,payload)
        if res:
            self.logger(f"user {id} has been updated.")
        else:
            self.logger(f"unable to process request")
        

    def getUser(self,user):
        # @user => string
        endpoint = f"/services/authentication/users/{user}"
        payload = None
        res = self.make_request("GET",endpoint,payload)
        if res:
            return res
        else:
            self.logger(f"user {user} not found.")
            return False

                
    def make_request(self,method,endpoint,payload):
        headers = self.headers
        conn = self.conn
        if(conn):
            try:
                payload = f'{payload}&output_mode=json' if payload is not None else "output_mode=json"
                conn.request(method, endpoint, payload, headers)
                res = conn.getresponse()
                data = res.read()
                
                jsondata = json.loads(data.decode())
            
                if("messages" in jsondata and len(jsondata['messages']) > 0):
                    r = jsondata
                    for message in jsondata.get('messages'):
                        if message.get('type') == "ERROR":
                            self.logger(json.dumps(message))
                            r = False
                    return r
                else:
                    return jsondata
                    
            except Exception as e:
                self.logger("unable to process request." + str(e))

    def connection(self):
        try:
            host = self.host
            mgmt_port = self.splunkd_port
            conn = None
            if(self.scheme == "https"):
                context = ssl._create_unverified_context() if self.skip_ssl_verify else None
                conn = http.client.HTTPSConnection(host, mgmt_port, context = context)
            else:
                conn = http.client.HTTPConnection(host, mgmt_port)
            self.logger(f'Connection successful. [{self.scheme}://{host}:{mgmt_port}]')
            
            if not self.auth_credentials:
                username = input("Enter your Splunk Username:")
                password = getpass()
                self.auth_credentials = self.encryptAuth(username,password)
            self.auth = f'Basic {self.auth_credentials}'
            return conn
        except Exception as e:
            self.logger("Unable to connect to host. "+str(e))
            return False
    
    def encryptAuth(self,username,password):
  
        credential = f"{username}:{password}"
        strbytes = credential.encode("ascii")
        
        base64_bytes = base64.b64encode(strbytes)
        base64_string = base64_bytes.decode("ascii")
        return base64_string
        

    def logger(self,log,**kwargs):
        with open(os.path.join(self.location,"activity.log"),"a") as f:
            if kwargs.get('begin'):
                f.writelines(["\n",f"====== activity started - ({datetime.now()}) =======","\n",log,"\n"])
            elif kwargs.get('end'):
                f.writelines([log,"\n",f"====== activity completed ({datetime.now()}) ======="])
            else:
                f.writelines([log,"\n"])
                print(log)
            

    def getConfig(self):
        config_file = os.path.join(self.location,self.config_file)
        # check if exists 
        if(not os.path.exists(config_file)):
            self.logger('Error: Config file not found')
            exit(1)
        file = open(config_file,'r')
        f = file.read()
        f = json.loads(f)
        file.close()

        # check for auth credentials 
        if f.get('splunk_username') and f.get('splunk_password'):
            u = f.get('splunk_username')
            p = f.get('splunk_password')
            b = self.encryptAuth(u,p)
            f['splunk_username'] = None
            f['splunk_password'] = None
            f['auth_credentials'] = b
            self.auth_credentials = b
            self.logger("auth_credentials created.")
            with open(config_file,"w") as file:
                f_str = json.dumps(f,indent=4)
                file.write(f_str)
        elif f.get('auth_credentials'):
            self.auth_credentials = f.get('auth_credentials')

        if f.get('host'):
            self.host = f.get('host')
        else:
            self.logger("No host value found from config.")
            exit(1)

        if f.get('splunkd_port'):
            self.splunkd_port = f.get('splunkd_port')
        else:
            self.logger("No splunkd_port found from config. Setting to default port: 8089")
            self.splunkd_port = 8089

        if f.get('scheme'):
            self.scheme = f.get('scheme')
        else:
            self.logger("No scheme found from config. Setting to default : https")
            self.scheme = 'https'

        if f.get('skip_ssl_verify'):
            self.skip_ssl_verify = f.get('skip_ssl_verify')
        else:
            self.skip_ssl_verify = True
        


    def mainProcess(self):
        csvReader = self.getListFile()
        if csvReader:
            for row in csvReader:
                action = row.get('action')
                
                if(action == "add" or action == "create"):
                    self.createUser(row)
                if(action == "update"):
                    self.updateUser(row)
                if(action == "delete"):
                    self.deleteUser(row.get('id'))
        
        
        


    def main(self):
        self.mainProcess()
        self.logger('',end=True)

if __name__ == "__main__":
    filename = sys.argv[1]
    user = Users(filename)