import json
import threading

import requests


class Server:
    def __init__(self, _infocollector, _ip_list):
        self.infocollector = _infocollector
        self.is_connectible = False
        self.is_connection_established = False
        self.computer_id = None

        self.server_threads = []
        self.server_ip = ""
        self.infocollector.debug_info("Information", "Server Variables Initialized")

        if not _ip_list:
            _ip_list = ['http://192.168.0.1:8000/',
                        'http://192.168.8.254:8000/',
                        'http://192.168.8.9:8000/']
        self.create_threads(_ip_list)

    def create_threads(self, _ip_list):
        self.infocollector.debug_info("Information", "Threads will be created for " + str(_ip_list))
        if not self.infocollector.isSingleThread:
            for _ip in _ip_list:
                try:
                    if not self.server_ip:
                        thread = threading.Thread(name=_ip, target=self.find_server, args=(_ip, _ip_list,))
                        thread.start()
                        self.server_threads.append(thread)
                    else:
                        self.infocollector.debug_info("Notice",
                                                      "Skipping" + str(_ip) + ", because Server IP already defined")
                        break
                except Exception as e:
                    self.infocollector.debug_info("Exception", e)
        else:
            for _ip in _ip_list:
                try:
                    if not self.server_ip:
                        self.find_server(_ip)
                    else:
                        self.infocollector.debug_info("Notice",
                                                      "Skipping " + str(_ip) + ", because Server IP already defined")
                        break
                except Exception as e:
                    self.infocollector.debug_info("Exception", e)

    def find_server(self, _ip):
        self.infocollector.debug_info("Information", "Establishing communication with server at " + str(_ip))
        try:
            response = requests.get(_ip + 'if/aux_data/', timeout=3)
            if response and not self.server_ip:
                aux_data = response.json()
                self.server_ip = _ip
                self.infocollector.debug_info("Notice", "Connection was established with server at " + str(_ip))
                self.infocollector.available_batches = sorted(aux_data['Received batches'])
                self.infocollector.available_ffactor = aux_data['Form factors']
                self.infocollector.observations["Server"] = aux_data['Observations']
                self.get_data_from_server()
                if self.is_connection_established:
                    if self.infocollector.isOrdered:
                        self.infocollector.available_categories = self.infocollector.assigned_category.split('!@#$^')
                    else:
                        self.infocollector.available_categories = sorted(aux_data['Categories'])
                        self.infocollector.avail_testers = sorted(aux_data['Testers'])
            elif response and self.server_ip:
                self.infocollector.debug_info("Warning", "Communication aborted with " + str(_ip) +
                                              ", because there is already established connection")
            elif not response:
                self.infocollector.debug_info("Warning", "Failed to communicate with server at " + str(_ip))
            else:
                self.infocollector.debug_info("Error", "Communicating with " + str(_ip) +
                                              " was unsuccessfully, reasons unknown")
        except AttributeError as e:
            self.infocollector.debug_info("Critical", "Communication unsuccessful, because of Attribute Error")
            self.infocollector.debug_info("Error", e)
        except requests.exceptions.ConnectionError as e:
            self.infocollector.debug_info("Critical", "Communication unsuccessful, because of Connection error")
            self.infocollector.debug_info("Error", e)
        except Exception as e:
            self.infocollector.debug_info("Warning", "Server at " + str(_ip) + " hasn't answered")
            self.infocollector.debug_info("Error", e)
        self.is_unsuccessful_connection()

    def get_data_from_server(self):
        if not self.infocollector.id_Dict:
            self.infocollector.main_sys_thread.join()
        request_dict = dict()
        request_dict["Serial"] = self.infocollector.id_Dict["Collected"]["Serial"]
        try:
            self.infocollector.debug_info("Information", "Searching device record in " + str(self.server_ip))
            json_dump = json.dumps(request_dict)
            resp = requests.get(self.server_ip + 'if/data/', json_dump, timeout=3)
            content = resp.content.decode('UTF-8')
            status = resp.status_code
        except Exception as e:
            resp = content = status = ''
            self.is_connectible = False
            self.is_connection_established = False
            self.infocollector.debug_info("Critical", "Couldn't comm. with server at " + str(self.server_ip))
            self.infocollector.debug_info("Error", e)

        try:
            # If computer wasn't found, but everything works
            if status == 404:
                self.is_connectible = True
                self.is_connection_established = True
                self.infocollector.debug_info("Notice", "Record wasn't found for this device")

            # If computer was found, push all available information to GUI
            elif status == 200:
                json_data = resp.json()
                self.infocollector.debug_info("Notice", "Record has been found, trying to fill data to GUI")
                if 'Observations' in json_data:
                    self.get_recorded_observations(json_data)
                if 'System Info' in json_data:
                    self.infocollector.assigned_form_factor = json_data["System Info"].get("Form factor", '')
                if 'Others' in json_data:
                    self.infocollector.isSold = json_data["Others"].get("isSold", '')
                    self.infocollector.boxNumber = json_data["Others"].get("Box number", '')
                    self.infocollector.obsAddNotes = json_data["Others"].get("Other", '')
                    self.infocollector.deviceLicense = json_data["Others"].get("License", '')
                    self.infocollector.previousTester = json_data["Others"].get("Previous tester", '')
                    self.infocollector.assigned_category = json_data["Others"].get("Category", '')
                    if 'Received batch' in json_data["Others"]:
                        self.infocollector.available_batches.clear()
                        self.infocollector.assigned_batch = json_data['Others'].get('Received batch', '').split(
                            '!@#$%^&*()')
                    self.infocollector.debug_info("Information", "Other Information loaded")
                if 'Order' in json_data:
                    self.infocollector.order_Name = json_data["Order"].get("Order name", '')
                    self.infocollector.order_Client = json_data["Order"].get("Client", '')
                    self.infocollector.order_Status = json_data["Order"].get("Current status", '')
                    self.infocollector.avail_testers = json_data["Order"].get("Testers", '')
                    self.infocollector.order_AvailStatus = ','.join(json_data["Order"].get("Statuses", '')).split(',')
                    self.infocollector.isOrdered = True
                    self.infocollector.debug_info("Information", "Order Information loaded")
                self.is_connectible = True
                self.is_connection_established = True
                self.infocollector.debug_info("Notice", "Existing record info was successfully loaded to GUI")
            # If unforeseen condition happened, hail
            else:
                self.is_connectible = True
                self.is_connection_established = False
                self.infocollector.debug_info("Critical", "Failure on the server side: " + content)
        except Exception as e:
            self.infocollector.debug_info("Critical", "Error while trying to handle status code: " + str(status))
            self.infocollector.debug_info("Error", e)
            self.is_connectible = False
            self.is_connection_established = False
        self.infocollector.debug_info("Information", "Communication done with server at " + str(self.server_ip))

    def get_recorded_observations(self, _recorded_data):
        try:
            recorded_obs = self.infocollector.observations["Recorded"]
            for _category_key, _category_val in _recorded_data["Observations"].items():
                # Create category key in recorded (loaded) observations
                recorded_obs.setdefault(_category_key, {})

                for _code_key, _code_val in _category_val.items():
                    # Now lets find in which type each code goes
                    _char = _code_val[3].lower()
                    if _char == "a":
                        code_type = 'Appearance'
                    elif _char == "f":
                        code_type = 'Function'
                    elif _char == "m":
                        code_type = 'Missing'
                    else:
                        continue

                    # If SubCategory(type) doesn't exist, create it
                    recorded_obs[_category_key].setdefault(code_type, {})

                    # Push code {key} and {val} to dict
                    recorded_obs[_category_key][code_type].update({_code_key: _code_val})
        except Exception as e:
            self.infocollector.debug_info("Critical", "Recorded observation couldn't be loaded")
            self.infocollector.debug_info("Exception", e)

    def is_unsuccessful_connection(self):
        if not self.is_connection_established:
            self.infocollector.avail_testers.clear()
            self.infocollector.available_batches.clear()
            self.infocollector.available_categories.clear()

    def record_exists(self):
        request_dict = dict()
        request_dict["Serial"] = self.infocollector.id_Dict["GUI"]["Serial"].get_text()
        try:
            json_dump = json.dumps(request_dict)
            resp = requests.get(self.server_ip + 'if/exists/', json_dump, timeout=3)
            if resp.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            self.infocollector.debug_info("Exception", e)
            return True

    def send_json(self, _post_dict):
        json_data = json.dumps(_post_dict)
        resp = requests.post(self.server_ip + 'if/data/', data=json_data, timeout=3)
        # picture = self.infocollector.manage_Photos()
        # if picture:
        #    pictureTar = {'tarFile': open(picture,'rb')}
        #    rP = requests.post(self.server_ip + 'if/pictures/' + str(self.computerID) + '/', files=pictureTar)

        if resp.status_code == 200:
            json_data = resp.json()
            self.computer_id = json_data['Index']

            self.infocollector.debug_info("Information", "Code: " + str(resp.status_code))
            self.infocollector.debug_info("Information", "Reason: " + str(resp.reason))
            self.infocollector.debug_info("Information", "Content: " + str(resp.content.decode('utf-8')))
            self.infocollector.debug_info("Notice", json.dumps(_post_dict, indent=4, sort_keys=True))
            return True
        else:
            error = "Error [" + str(resp.status_code) + "] - " + str(resp.reason) + "\n" + resp.content.decode('utf-8')
            self.infocollector.debug_info("Error", error)
            return False

    def request_print_qr(self, _printer):
        requests.post(self.server_ip + "website/edit/" + str(self.computer_id) + "/print_qr/" + _printer + "/")
        self.infocollector.debug_info("Information", "QR Printed, Computer Index: " + str(self.computer_id))
