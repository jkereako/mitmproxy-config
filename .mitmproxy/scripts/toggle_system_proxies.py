import subprocess

class NetworkDeviceInspector(object):
    '''
    Inspects network devices in macOS.
    '''
    def active_device_name(self):
        '''
        Finds the active device name, e.g. "Wi-Fi", "Thunderbolt Ethernet"
        '''
        return self.__find_active_device_name()

    def __find_active_device_name(self):
        '''
        Finds the network service name for a given device identifier
        '''
        args = ["networksetup", "-listnetworkserviceorder"]
        lines = Helper().execute(args)
        expected_length = 3

        # The output of `networksetup -listnetworkserviceorder` is the following:
        #
        # > An asterisk (*) denotes that a network service is disabled.
        # > (1) Wi-Fi
        # > (Hardware Port: Wi-Fi, Device: en0)
        # > 
        # > (2) Thunderbolt Bridge
        # > (Hardware Port: Thunderbolt Bridge, Device: bridge0)
        #
        # We want line #3. It's currently used network device.
        if len(lines) < expected_length:
            assert False, "Unable find active network device name"

        # Find the first line that contains the device identifier. This 
        # solution allows us to avoid direct indexing.
        for line in lines:
            string = str(line).strip()

            if "(Hardware Port:" in string:
                name = string.split(",")[0].split(":")[-1].strip("\"' ")
                break

        return name

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
        args = ["-getwebproxy", "-getsecurewebproxy"]

        for arg in args:
            cmd = ["networksetup", arg, self.device_name]
            lines = helper.execute(cmd)

            for line in lines:
                split_line = line.split(":")

                if split_line[0].strip() == "Enabled" and split_line[-1].strip() == "Yes":
                    return True

            return False

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