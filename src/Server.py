import json
import threading

import requests


class Server:
    def __init__(self, infocollector, ip_list):
        self.infocollector = infocollector
        self.isConnectible = False
        self.isConnEstablish = False
        self.computerID = None

        self.serverThreads = []
        self.serverIP = ""
        self.infocollector.debug_info("Information", "Server Variables Initialized")
        if not ip_list:
            ip_list = ['http://192.168.0.1:8000/',
                       'http://192.168.8.254:8000/',
                       'http://192.168.8.9:8000/']
        self.create_threads(ip_list)

    def create_threads(self, ip_list):
        self.infocollector.debug_info("Information", "Threads will be created for " + str(ip_list))
        if not self.infocollector.isSingleThread:
            for ip in ip_list:
                try:
                    if not self.serverIP:
                        thread = threading.Thread(name=ip, target=self.find_server, args=(ip, ip_list,))
                        thread.start()
                        self.serverThreads.append(thread)
                    else:
                        self.infocollector.debug_info("Information",
                                                      "Skipping" + str(ip) + ", because Server IP already defined")
                        break
                except Exception as e:
                    self.infocollector.debug_info("Exception", e)
        else:
            for ip in ip_list:
                try:
                    if not self.serverIP:
                        self.find_server(ip)
                    else:
                        self.infocollector.debug_info("Information",
                                                      "Skipping " + str(ip) + ", because Server IP already defined")
                        break
                except Exception as e:
                    self.infocollector.debug_info("Exception", e)

    def find_server(self, ip):
        self.infocollector.debug_info("Information", "Establishing communication with server at " + str(ip))
        try:
            response = requests.get(ip + 'if/aux_data2/', timeout=3)
            if response and not self.serverIP:
                aux_data = response.json()
                self.serverIP = ip
                self.infocollector.debug_info("Notice", "Connection was established with server at " + str(ip))
                self.infocollector.observations["Server"] = aux_data['Observations']
                self.infocollector.avail_Batches = sorted(aux_data['Received batches'])
                self.get_data_from_server()
                if self.isConnEstablish:
                    if self.infocollector.isOrdered:
                        self.infocollector.avail_Categories = self.infocollector.assignedCategory.split('!@#$^')
                    else:
                        self.infocollector.avail_Categories = sorted(aux_data['Categories'])
                        self.infocollector.avail_testers = sorted(aux_data['Testers'])
            elif response and self.serverIP:
                self.infocollector.debug_info("Warning", "Communication aborted with " + str(ip) +
                                              ", because there is already established connection")
            elif not response:
                self.infocollector.debug_info("Warning", "Failed to communicate with server at " + str(ip))
            else:
                self.infocollector.debug_info("Error", "Communicating with " + str(ip) +
                                              " was unsuccessfully, reasons unknown")
        except AttributeError as e:
            self.infocollector.debug_info("Critical", "Communication unsuccessful, because of Attribute Error")
            self.infocollector.debug_info("Error", e)
        except requests.exceptions.ConnectionError as e:
            self.infocollector.debug_info("Critical", "Communication unsuccessful, because of Connection error")
            self.infocollector.debug_info("Error", e)
        except Exception as e:
            self.infocollector.debug_info("Warning", "Server at " + str(ip) + " hasn't answered")
            self.infocollector.debug_info("Error", e)
        self.is_unsuccessful_connection()

    def get_data_from_server(self):
        if not self.infocollector.id_Dict:
            self.infocollector._MainSysThread.join()
        request_dict = dict()
        request_dict["Serial"] = self.infocollector.id_Dict["Collected"]["Serial"]
        try:
            self.infocollector.debug_info("Information", "Searching device record in " + str(self.serverIP))
            json_dump = json.dumps(request_dict)
            response = requests.get(self.serverIP + 'if/data2/', json_dump, timeout=3)
            content = response.content.decode('UTF-8')
            status = response.status_code
        except Exception as e:
            response = content = status = ''
            self.isConnectible = False
            self.isConnEstablish = False
            self.infocollector.debug_info("Critical", "Couldn't comm. with server at " + str(self.serverIP))
            self.infocollector.debug_info("Error", e)

        try:
            # If computer wasn't found, but everything works
            if status == 404:
                self.isConnectible = True
                self.isConnEstablish = True
                self.infocollector.debug_info("Notice", "Record wasn't found for this device")

            # If computer was found, push all information to GUI
            elif status == 200:
                json_data = response.json()
                self.infocollector.debug_info("Notice", "Record has been found, trying to fill data to GUI")
                if 'Observations' in json_data:
                    self.get_recorded_observations(json_data)
                if 'Others' in json_data:
                    if 'Box number' in json_data["Others"]:
                        self.infocollector.boxNumber = json_data["Others"]["Box number"]
                    if 'License' in json_data["Others"]:
                        self.infocollector.deviceLicense = json_data["Others"]["License"]
                    if 'Previous tester' in json_data["Others"]:
                        self.infocollector.previousTester = json_data["Others"]["Previous tester"]
                    if 'Category' in json_data["Others"]:
                        self.infocollector.assignedCategory = json_data["Others"]["Category"]
                    if 'Other' in json_data["Others"]:
                        self.infocollector.obsAddNotes = json_data["Others"]["Other"]
                    if 'isSold' in json_data["Others"]:
                        self.infocollector.isSold = json_data["Others"]["isSold"]
                    if 'Received batch' in json_data["Others"]:
                        self.infocollector.avail_Batches = []
                        self.infocollector.assignedBatch = json_data['Others']['Received batch'].split('!@#$%^&*()')
                    self.infocollector.debug_info("Information", "Loading Other Information")
                if 'Order' in json_data:
                    if 'Client' in json_data["Order"]:
                        self.infocollector.order_Client = json_data["Order"]["Client"]
                    if 'Order name' in json_data["Order"]:
                        self.infocollector.order_Name = json_data["Order"]["Order name"]
                    if 'Testers' in json_data["Order"]:
                        self.infocollector.avail_testers = json_data["Order"]["Testers"]
                    if 'Current status' in json_data["Order"]:
                        self.infocollector.order_Status = json_data["Order"]["Current status"]
                    if 'Statuses' in json_data["Order"]:
                        self.infocollector.order_AvailStatus = ','.join(json_data["Order"]["Statuses"]).split(',')
                    self.infocollector.isOrdered = True
                    self.infocollector.debug_info("Information", "Loading Order Information")
                self.isConnectible = True
                self.isConnEstablish = True
                self.infocollector.debug_info("Notice", "Existing record info was successfully loaded to GUI")
            # If unforeseen condition happened, hail
            else:
                self.isConnectible = True
                self.isConnEstablish = False
                self.infocollector.debug_info("Critical", "Failure on the server side: " + content)
        except Exception as e:
            self.infocollector.debug_info("Critical", "Error while trying to handle status code: " + str(status))
            self.infocollector.debug_info("Error", e)
            self.isConnectible = False
            self.isConnEstablish = False
        self.infocollector.debug_info("Information", "Communication done with server at " + str(self.serverIP))

    def get_recorded_observations(self, recorded_data):
        try:
            recorded_obs = self.infocollector.observations["Recorded"]
            for _category_key, _category_val in recorded_data["Observations"].items():
                # If Category doesn't exist, create it
                if _category_key not in recorded_obs:
                    recorded_obs[_category_key] = {}

                for _code_key, _code_val in _category_val.items():
                    # Now lets find in which type each code goes
                    if _code_val[3].lower() == "a":
                        code_type = 'Appearance'
                    elif _code_val[3].lower() == "f":
                        code_type = 'Function'
                    elif _code_val[3].lower() == "m":
                        code_type = 'Missing'
                    else:
                        continue

                    # If SubCategory(type) doesn't exist, create it
                    if code_type not in recorded_obs[_category_key]:
                        recorded_obs[_category_key][code_type] = {}
                    # And finally push code {key} and {val} to dict
                    recorded_obs[_category_key][code_type].update({_code_key: _code_val})
        except Exception as e:
            self.infocollector.debug_info("Critical", "Recorded observation couldn't be loaded")
            self.infocollector.debug_info("Exception", e)

    def is_unsuccessful_connection(self):
        if not self.isConnEstablish:
            self.infocollector.avail_testers = []
            self.infocollector.avail_Batches = []
            self.infocollector.avail_Categories = []

    def record_exists(self):
        request_dict = dict()
        request_dict["Serial"] = self.infocollector.id_Dict["GUI"]["Serial"].get_text()
        try:
            json_dump = json.dumps(request_dict)
            response = requests.get(self.serverIP + 'if/exists/', json_dump, timeout=3)
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            self.infocollector.debug_info("Exception", e)
            return True

    def send_json(self, post_dict):
        json_data = json.dumps(post_dict)
        response = requests.post(self.serverIP + 'if/data2/', data=json_data, timeout=3)
        if response.status_code == 200:
            json_data = response.json()
            self.computerID = json_data['Index']

            self.infocollector.debug_info("Information", "Code: " + str(response.status_code))
            self.infocollector.debug_info("Information", "Reason: " + str(response.reason))
            self.infocollector.debug_info("Information", "Content: " + str(response.content.decode('utf-8')))
            self.infocollector.debug_info("Notice", json.dumps(post_dict, indent=4, sort_keys=True))
            return True
        else:
            self.infocollector.debug_info("Error", "Error occurred! [ " + str(response.status_code) + " ] - " +
                                          str(response.reason) + "\n" + str(response.content.decode('utf-8')))
            return False

    #       picture = self.infocollector.manage_Photos()
    #       if picture:
    #           pictureTar = {'tarFile': open(picture,'rb')}
    #           rP = requests.post(self.serverIP + 'if/pictures/' + str(self.computerID) + '/', files=pictureTar)

    def request_print_qr(self, _printer):
        requests.post(self.serverIP + "website/edit/" + str(self.computerID) + "/print_qr/" + _printer + "/")
        self.infocollector.debug_info("Information", "QR Printed, Computer Index: " + str(self.computerID))
