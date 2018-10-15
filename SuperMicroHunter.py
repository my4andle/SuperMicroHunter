#!/usr/bin/python3
"""
Usage:
  SuperMicroHunter.py -h | --help
  SuperMicroHunter.py (--subnet=<subnet> | --rhosts=<rhosts>)
 
Options:
  --subnet=<subnet> subnet in CIDR notation
  --rhosts=<rhosts> a file containing a single IPv4 address per line
"""
import sys
import json
import ipaddress
import requests
import typing
import concurrent.futures

from datetime import datetime
from docopt import docopt

def generate_urls_from_subnet(subnet: str) -> list:
    """
    Generate a list of URLs from a given subnet in CIDR notation

    Args:
        subnet: A subnet in CIDR notation ex. 192.168.1.0/24

    Returns:
        List of IPv4 addresses
    """
    print("Generating url list from given subnet: {}".format(subnet))
    ipaddress.ip_network(subnet)
    urls = []
    for ip in ipaddress.ip_network(subnet):
        url = "http://{}".format(ip)
        urls.append(url)
    return urls

def generate_list_from_file(data_file: str) -> list:
    """
    Generate a list from a given file containing a single line of desired data, intended for IPv4 and passwords.

    Args:
        data_file: A file containing a single IPv4 address per line

    Returns:
        List of IPv4 addresses
    """
    print("Generating data list from: {}".format(data_file))
    data_list = []
    with open(data_file, 'r') as my_file:
        for line in my_file:
            ip = line.strip('\n').strip(' ')
            url = "http://{}".format(ip)
            data_list.append(url)
    return data_list

def check_http_status(URL: str) -> str:
    """
    Check status code for http request to given URL

    Args:
        URL: A single URL
    
    Returns:
        The supplied URL if it meets condition checks
    """
    try:
        print("Testing: {}".format(URL))
        # The default content of the BMC page may differ requiring an update to this code, however I do not have differing BMC splashpage examples to test at this time
        content = b'<!--\r\n<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\r\n-->\r\n<html xmlns="http://www.w3.org/1999/xhtml">\r\n<head>\r\n    <META http-equiv="Content-Type" content="text/html; charset=utf-8">\r\n    <META HTTP-EQUIV="Pragma" CONTENT="no_cache">\r\n    <META NAME="ATEN International Co Ltd." CONTENT="(c) ATEN International Co Ltd. 2010">\r\n    <title></title>\r\n<!--    <link rel="shortcut icon" href="../images/favicon.ico">\t-->\r\n    <link rel="stylesheet" href="../css/basic.css" type="text/css">\r\n    <script language="JavaScript">\r\n\tif (window != top)\r\n\t\ttop.location.href = "/";//location.href;\r\n    </script>\r\n    <script language="JavaScript" src="../js/utils.js"></script>\r\n    <script language="JavaScript" type="text/javascript">\r\n<!--\r\n    var lang_setting;\r\n    lang_setting = ReadCookie("language");\r\n    if (lang_setting == null)\r\n    {\r\n    \tCreateCookie("langSetFlag","0");\r\n    \tCreateCookie("language","English");\r\n    \tlang_setting = "English";\r\n    }\r\n    document.write("<script type=\\"text/javascript\\", src = \\"../js/lang/" + lang_setting + "/lang_str.js\\"><\\/script>");\t\r\n\tfunction checkform()\r\n\t{\r\n\t\tif(Trim(form1.name.value) == "")\r\n\t\t{\r\n\t\t\talert(lang.LANG_LOGIN_INVALID_USERNAME);\r\n\t\t\tform1.name.focus();\r\n\t\t\treturn;\r\n\t\t}\r\n\t\tif(Trim(form1.pwd.value) == "")\r\n\t\t{\r\n\t\t\talert(lang.LANG_LOGIN_INVALID_PASSWORD);\r\n\t\t\tform1.pwd.focus();\r\n\t\t\treturn;\r\n\t\t}\r\n\t\tdocument.form1.submit();\r\n\t\treturn;\r\n\t}\r\n\tfunction checkEnt(e)\r\n\t{\r\n        var key = window.event ? e.keyCode : e.which;\r\n        if(key == 13) \r\n        {\r\n\r\n            checkform();\r\n        }\r\n \t}\r\n\tfunction PageInit()\r\n\t{\r\n\t\tvar msg = document.getElementById("login_word");\r\n\t\tmsg.setAttribute("value", lang.LANG_LOGIN_LOGIN);\r\n\t\treturn;\r\n\t}\r\n-->\r\n\t</script>\r\n</head>\r\n<body onload=\'PageInit()\'>\r\n\t<table style="margin: 0px; height: 100%; width: 100%" border="0" background=#FFFFFF cellpadding="0" cellspacing="0">\r\n\t\t<tr>\r\n\t\t\t<td style="height: 25%; vertical-align: bottom; text-align: center">\r\n\t\t\t\t<table style="margin: 0 auto;" border="0" width="412px">\r\n\t\t\t\t\t<tr>\r\n\t\t\t\t\t\t<td>\r\n\t\t\t\t\t\t\t<img src="../images/logo.gif" style="margin: 0px; padding: 0px;">\r\n\t\t\t\t\t\t</td>\r\n\t\t\t\t\t</tr>\r\n\t\t\t\t</table>\r\n\t\t\t</td>\r\n\t\t</tr>\r\n\t\t<tr style="width: 100%">\r\n\t\t\t<td style="height: 75%; vertical-align: top; text-align: center">\r\n\t\t\t\t<table class="login">\r\n\t\t\t\t\t<tr><td>\r\n\t\t\t\t\t<h3><script>document.writeln(lang.LANG_LOGIN_PROMPT);</script></h3>\r\n\t\t\t\t\t<form name="form1" action="/cgi/login.cgi" method="post">\r\n           \t\t\t<label style="width:85px; text-align:left; margin-right: 2px;"><script>document.writeln(lang.LANG_LOGIN_USERNAME)</script></label><input name="name" size="20" maxlength="64" style="width:146px;" type="text" onKeyDown="checkEnt(event)"><br><br>\r\n           \t\t\t<label style="width:85px; text-align:left; margin-right: 2px;"><script>document.writeln(lang.LANG_LOGIN_PASSWORD)</script></label><input name="pwd" size="20" maxlength="64" style="width:146px;" type="password" onKeyDown="checkEnt(event)"><br><br>\r\n           \t\t\t<input id="login_word" class="btnStyle" name="Login" type="button" onclick="javascript: checkform(this)">\r\n\t\t\t\t\t</form>\r\n\t\t\t\t\t</td></tr>\r\n\t\t\t\t</table>\r\n\t\t\t</td>\r\n\t\t</tr>\r\n\t</table>\r\n</body>\r\n</html>'
        r = requests.get(URL, timeout=1)
        if r.status_code == 200 and r.content == content:
            print("SuperMicro BMC found: {}".format(URL))
            return URL
    except:
        pass

def check_http_status_concurrent(URLs: list) -> list:
    """
    Check URLs against the required conditions concurrently

    Args:
        URLs: A list containing one or more URLs
    
    Returns:
        A list of URLs that meet our conditions
    """
    results_list = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=50) as pool:
        results = {pool.submit(check_http_status, URL): URL for URL in URLs}
        for future in concurrent.futures.as_completed(results):
            if future.result():
                results_list.append(future.result())
    return results_list

def main():
    try:
        opts = docopt(__doc__)
        if opts['--subnet']:
            URLs = generate_urls_from_subnet(opts['--subnet'])
        elif opts['--rhosts']:
            URLs = generate_list_from_file(opts['--rhosts'])
        else:
            print("Oops no input targets I blame docopt")
            sys.exit()

        results = check_http_status_concurrent(URLs)
        logfilename = datetime.now().strftime('SuperMicroHunter_%H_%M_%d_%m_%Y.log')
        with open(logfilename, "w+") as file:
            file.write(json.dumps(results, indent=4))
    except ValueError as ex:
        print("Value error check inputs: {}".format(str(ex)))
    except Exception as ex:
        print(str(ex))

if __name__ == '__main__':
    main()
