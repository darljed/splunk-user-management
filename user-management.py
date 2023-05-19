from datetime import datetime
import http.client
import os, sys, csv, json, ssl
import base64
from getpass import getpass


# add users -  completed
# update roles of existing Users - completed


class Users:
    def __init__(self,filename,action):
        self.location = os.path.dirname(__file__)
        self.filename = filename
        self.action = action
        self.logger('',begin=True)
        self.conn = self.connection()
        self.main(action)

    def connection(self):
        try:
            host = "localhost"
            mgmt_port = 8089
            conn = http.client.HTTPSConnection(host, mgmt_port, context = ssl._create_unverified_context())
            self.logger('connection successful...')
            
            username = input("Enter your Splunk Username:")
            password = getpass()
            self.auth = f'Basic {self.encryptAuth(username,password)}'
            return conn
        except Exception as e:
            self.logger("Unable to connect to host. "+str(e))
            print("Unable to connect to host. "+str(e))
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
                f.writelines(["\n",f"====== activity started - action: {self.action} ({datetime.now()}) =======","\n",log,"\n"])
            elif kwargs.get('end'):
                f.writelines([log,"\n",f"====== activity completed ({datetime.now()}) ======="])
            else:
                f.writelines([log,"\n"])
            



    def main(self,action):
        if(action == "add"):
            csvReader = self.getListFile()
            if csvReader:
                for row in csvReader:
                    self.createUser(row)
        elif action == "delete":
            csvReader = self.getListFile()  
            if csvReader:
                for row in csvReader:
                    roleslist = row.get('roles').split(",")
                    self.deleteUsers(row.get('id'))
        elif action == "update":
            csvReader = self.getListFile()  
            if csvReader:
                for row in csvReader:
                    self.updateUser(row)

        self.logger('',end=True)

    def getListFile(self):
        userslist = os.path.join(self.location,self.filename)
        if( os.path.exists(userslist)):
            
            f = open(userslist,"r")
            csvReader = csv.DictReader(f)
            return csvReader
        else:
            self.logger(f'file {userslist} doesn\'t exists.')
            print(f'file {userslist} doesn\'t exists.')
            return False
    
    def deleteUsers(self,user):
        # @user => string
        endpoint = f"/services/authentication/users/{user}"
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': self.auth
        }
        conn = self.conn
        try:
            conn.request('DELETE',endpoint,"output_mode=json",headers)
            res = conn.getresponse()
            data = res.read()
            jsondata = json.loads(data.decode())
            # print(jsondata)
            if("messages" in jsondata):
                self.logger(json.dumps(jsondata))
            else:
                self.logger(f"user {user} has been deleted.")
        except Exception as e:
            msg = f"Unable to process request. {str(e)}"
            self.logger(msg)
            print(msg)



    def createUser(self,data):
        # @user => string
        # @roles => list
        endpoint = "/services/authentication/users"
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': self.auth
        }
        user = data.get('id')
        roles = data.get('roles').split(",")
        temp_pass = data.get('temp_pass')
        default_app = data.get('default_app')
        rolelist = ""
        for role in roles:
            rolelist += f"&roles={role}"
        conn = self.conn
        if(conn):
            try:
                payload = f'force-change-pass=true&name={user}&password={temp_pass}{rolelist}&defaultApp={default_app}&output_mode=json'
                conn.request("POST", endpoint, payload, headers)
                res = conn.getresponse()
                data = res.read()
                
                jsondata = json.loads(data.decode())
                if("messages" in jsondata):
                    self.logger(json.dumps(jsondata))
                else:
                    self.logger(f"user {user} has been created.")
                
            except Exception as e:
                self.logger("unable to process request." + str(e))
                print("unable to process request." + str(e))

    def updateUser(self,data):
        # @user => string
        # @roles => list
        endpoint = f"/services/authentication/users/{data.get('id')}"
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': self.auth
        }
        roles = data.get('roles').split(",")
        default_app = data.get('default_app')
        rolelist = ""
        for role in roles:
            rolelist += f"&roles={role}"
        conn = self.conn
        if(conn):
            try:
                payload = f'output_mode=json{rolelist}&defaultApp={default_app}'
                conn.request("POST", endpoint, payload, headers)
                res = conn.getresponse()
                data = res.read()
                
                jsondata = json.loads(data.decode())
                if("messages" in jsondata):
                    self.logger(json.dumps(jsondata))
                else:
                    self.logger(f"user {user} has been updated.")
                
            except Exception as e:
                self.logger("unable to process request." + str(e))
                print("unable to process request." + str(e))

    # def collectUser(self):
        # @user => string
        # @roles => list
        # endpoint = f"/services/authentication/users/{data.get('id')}"
        # headers = {
        # 'Content-Type': 'application/x-www-form-urlencoded',
        # 'Authorization': self.auth
        # }
        # roles = data.get('roles').split(",")
        # default_app = data.get('default_app')
        # rolelist = ""
        # for role in roles:
        #     rolelist += f"&roles={role}"
        # conn = self.conn
        # if(conn):
        #     try:
        #         payload = f'output_mode=json{rolelist}&defaultApp={default_app}'
        #         conn.request("POST", endpoint, payload, headers)
        #         res = conn.getresponse()
        #         data = res.read()
                
        #         jsondata = json.loads(data.decode())
        #         if("messages" in jsondata):
        #             self.logger(json.dumps(jsondata))
        #         else:
        #             self.logger(f"user {user} has been updated.")
                
        #     except Exception as e:
        #         self.logger("unable to process request." + str(e))
        #         print("unable to process request." + str(e))

if __name__ == "__main__":
    filename = sys.argv[1]
    action = sys.argv[2]
    user = Users(filename,action)