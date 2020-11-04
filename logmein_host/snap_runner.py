#!/usr/bin/env python3
#
# Copyright (c) 2018 LogMeIn, Inc.
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to deal 
# in the Software without restriction, including without limitation the rights 
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell 
# copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE 
# SOFTWARE. 

"""Running logmein_host from snap"""

import logging
import os
import sys
import subprocess
import time
from .logmein_host import Config, Host, Register

def main():
    config = Config()

    p = subprocess.Popen(["snapctl", "get", "loglevel"], stdout=subprocess.PIPE)
    config.loglevel = p.stdout.read().decode().rstrip()
    p.wait()
    if config.loglevel != "INFO" and config.loglevel != "DEBUG":
        config.loglevel = "INFO"

    logging.basicConfig(level=config.getLoglevel(), format='%(threadName)s %(message)s')

    licensePath = os.getenv("SNAP_COMMON", "/var/lib/logmein-host")
    config.globalLicenseFile = "{}/license.dat".format(licensePath)
    config.osSpec = 987168779

    p = subprocess.Popen(["snapctl", "get", "homesite"], stdout=subprocess.PIPE)
    config.homeSite = p.stdout.read().decode().rstrip()
    retval = p.wait()
    if retval != 0 or config.homeSite == "":
        config.homeSite = "secure.logmein.com"

    p = subprocess.Popen(["snapctl", "get", "deploy-code"], stdout=subprocess.PIPE)
    deploy_code = p.stdout.read().decode().rstrip()
    retval = p.wait()

    if retval != 0:
        sys.exit(retval)

    if deploy_code == "" or deploy_code == "none":
        logging.error("Generate an Installation Link and configure first. Further info:")
        logging.error("https://repository.services.logmein.com/linux/index.html")
        subprocess.run("snapctl stop --disable \"${SNAP_NAME}.pytty\"", shell=True)
        subprocess.run("snapctl stop --disable \"${SNAP_NAME}.logmein-host\"", shell=True)
        time.sleep(5)

    if deploy_code != "SAVED":
        register = Register(config, deploy_code)
        register.hostRegister()
        subprocess.run(["snapctl", "set", "deploy-code=SAVED"])

    config.parseLicenseFile(False)
    Host.runForever(config)
