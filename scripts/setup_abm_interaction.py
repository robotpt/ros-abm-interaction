#!/usr/bin/env python3.6

import os
import rospy
import subprocess
import json

from fitbit_client import FitbitClient


# Setup fitbit
credentials_file_path=rospy.get_param(
    'abm/fitbit/credentials/path',
    default='/root/state/fitbit_credentials.yaml'
)
redirect_url=rospy.get_param(
    'abm/fitbit/redirect_url',
    default="http://localhost",
)
FitbitClient(
    credentials_file_path=credentials_file_path,
    redirect_url=redirect_url,
)

# Setup AWS
os.system("aws configure")

out = subprocess.check_output(["aws", "sts", "get-caller-identity"])
out = json.loads(out)
print(out, type(out))

print("Make sure to grab the IP addresses below")
tablet_port = 8082
os.system("http-server -p {}".format(tablet_port))

print("\n\tDONE! Hit Ctrl-C to exit\n")
