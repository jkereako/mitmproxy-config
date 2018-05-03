import subprocess

class NetworkDeviceInspector(object):
    '''
    Inspects network devices in macOS
    '''
    def active_device_name(self):
        '''
        Finds the active device name, e.g. "Wi-Fi", "Thunderbolt Ethernet"
        '''
        active_device = self.__find_active_device_identifier()

        assert active_device is not None, "Unable to detect the active network device"

        return self.__find_active_device_name(active_device)

    def __find_active_device_identifier(self):
        '''
        Finds the active network device identifier (e.g. "en0" or "en1")
        '''

        # This is the simplest way to determine the active network device.
        args = ["route", "get", "google.com"]
        lines = Helper().execute(args)
        substring = "interface"

        for line in lines:
            string = str(line)
            if substring in string:
                # output: b'  interface: en0'
                #
                # Splits the string on the colon to remove the first half, index
                # the last element and then remove unwanted string
                return string.split(":")[-1].strip("\"' ")

    def __find_active_device_name(self, active_device):
        '''
        Finds the network service name for a given device identifier
        '''
        args = ["networksetup", "-listnetworkserviceorder"]
        lines = Helper().execute(args)

        for line in lines:
            string = str(line)
            if active_device in string:
                # output: b'(Hardware Port: Wi-Fi, Device: en0)'
                name = string.split(",")[0].split(":")[-1].strip("\"' ")
                return name

        # Unexpected behavior
        assert False, "Unable find active network device name"

class ProxyManager(object):
    '''
    Inspects and manipulates proxies in macOS
    '''
    def __init__(self, device_name):
        self.device_name = device_name
        self.server = "localhost"
        self.port = "8080"

    def are_proxies_already_set(self):
        '''
        Sets both the HTTP and HTTPS web proxies for the argument
        'self.device_name'.
        '''
        helper = Helper()
        get_web_proxy_args = ["-getwebproxy", "-getsecurewebproxy"]

        for get_web_proxy_arg in get_web_proxy_args:
            args = ["networksetup", get_web_proxy_arg, self.device_name]
            lines = helper.execute(args)

            for line in lines:
                split_line = line.strip("\"' ").split(":")

                if split_line[0] == "Server":
                    if split_line[-1] != self.server:
                        return False

                elif split_line[0] == "Port":
                    if split_line[-1] != self.port:
                        return False

            return True

    def set_proxies(self):
        '''
        Sets both the HTTP and HTTPS web proxies for the argument
        'self.device_name'.
        '''
        helper = Helper()
        set_web_proxy_args = ["-setwebproxy", "-setsecurewebproxy"]

        for set_web_proxy_arg in set_web_proxy_args:
            args = ["networksetup", set_web_proxy_arg, self.device_name, "localhost", "8080"]
            helper.execute(args)

    def deactivate_proxies(self):
        '''
        Deactivates both the HTTP and HTTPS web proxies for the argument
        'self.device_name'.
        '''

        self.__toggle_web_proxies(self.device_name, "off")

    def activate_proxies(self):
        '''
        Activates both the HTTP and HTTPS web proxies for the argument
        'self.device_name'.
        '''

        self.__toggle_web_proxies(self.device_name, "on")

    def __toggle_web_proxies(self, service_name, state="on"):
        '''
        Toggles both the HTTP and HTTPS web proxies for the argument
        'service_name'.
        '''

        helper = Helper()
        set_web_proxy_state_args = ["-setwebproxystate", "-setsecurewebproxystate"]

        for set_web_proxy_state_arg in set_web_proxy_state_args:
            args = ["networksetup", set_web_proxy_state_arg, service_name, state]
            helper.execute(args)

class Helper(object):
    '''
    Internal helper methods.
    '''
    def execute(self, arg_list):
        print(arg_list)
        # Use this line instead to see the actual reported error
        # result = subprocess.run(arg_list, stdout=subprocess.PIPE).stdout
        result = subprocess.check_output(arg_list)
        return result.decode("utf-8").splitlines()

#-- MITM events
class ProxyToggler(object):
    def load(self, l):
        device_inspector = NetworkDeviceInspector()
        active_device = device_inspector.active_device_name()
        proxy_manager = ProxyManager(active_device)

        if not proxy_manager.are_proxies_already_set():
            proxy_manager.set_proxies()

        proxy_manager.activate_proxies()

    def done(self):
        device_inspector = NetworkDeviceInspector()
        active_device = device_inspector.active_device_name()
        proxy_manager = ProxyManager(active_device)
        proxy_manager.deactivate_proxies()

addons = [
    ProxyToggler()
]