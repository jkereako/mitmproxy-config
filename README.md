# Configurations for mitmproxy
This script automatically sets and activates HTTP and HTTPS proxies on your
active network device and automatically deactivates the proxies when you kill
mitmproxy. Additionally, it allows you to test network timeouts and status code
and error code responses via the query string.

> Tested on macOS Monterey (12.4) and mitmproxy 8.0

# Installation
1. Clone the repository

```sh
$> git clone git@github.com:jkereako/mitmproxy-config.git
Cloning into 'mitmproxy-config'...
remote: Counting objects: 5, done.
remote: Compressing objects: 100% (5/5), done.
Receiving objects: 100% (5/5), done.
remote: Total 5 (delta 0), reused 0 (delta 0), pack-reused 0
```

Then copy the directory `.mitmproxy` to your home directory.

```sh
$> cp -R mitmproxy-config/.mitmproxy ~/
```

2. Start mitmproxy.

```sh
$> mitmproxy
```

> *The following setps install mitmproxy's root certificate. This 
> allows mitmproxy to decrypt encrypted traffic.*

3. Navigate to http://mitm.it in your browser and select Apple.
4. Follow the instructions for how to install the certificate.

That's it! Now you can view traffic for the domains specified in `view_filter`.

# Files
### config.yaml
This is mitmproxy's config file which is loaded on start up.

### toggle_system_proxies.py
This script makes mitmproxy much easier to work with when using it on macOS. It
will automatically set and activate proxies on the network device you're
currently using. When you quit mitmproxy, the script will automatically
deactivate those proxies.

### error_response.py
This script allows you to test response time-outs and error responses in the
form of an HTTP status code or a custom error code your service may send back.
When provided arguments via the query string, this script will return a status
code, an error code encoded in JSON and a response delay.

For example, this URL will return an HTTP error code of 422: `http://ytmnd.com?s=422`

Here are the supported query string parameters and the type of their arguments:

|                 |  Parameter         |   Type    |
|-----------------|--------------------|-----------|
| URL redirect    | `redirect`         |  URL      |
| Clear cookies   | `clear_cookies`    |  Boolean  |
| Status code     | `status`           |  Integer  |
| Error code      | `code`             |  String   |
| Response delay  | `delay`            |  Integer  |

# Troubleshooting

### Problems with VPN
Proxies won't work over a VPN, but, there are work-arounds. The folks at
[Proxyman have a doc for said work-arounds][1].

### Proxies not automatically set
For the first time only, you may need to manually toggle the proxies. Go to 
**System Preferences > Network > Advanced > Proxies**. Select "Web Proxy 
(HTTP)" and "Secure Web Proxy (HTTPS)", click **OK** and then
click **Apply**. Now turn them off and try running mitmproxy again.

# mitmproxy script debugging
To debug a custom script in mitmproxy, use mitmdump.

```sh
 $> mitmdump -s custom_script.py
```

This runs mitmproxy directly in the command line which allows you to see errors
printed to stderr and logs printed to stdout.

[1]: https://docs.proxyman.io/troubleshooting/proxyman-does-not-work-with-vpn-apps