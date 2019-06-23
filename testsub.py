import subprocess
import time

command = "exec /bin/bash -i -c testit"

p = subprocess.Popen(command,
                        shell=True, 
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        start_new_session=True,
                        encoding="utf-8")

#time.sleep(5)