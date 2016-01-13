
import re
import os
import sys

import subprocess
import signal

def kill_process_by_name(re_pattern):

    """ kills process by regex pattern matching.
        origins: hacky way of ensuring all metamap processes are killed.
    """

    user_name = os.getlogin()
    parent_pid = os.getppid()
    current_pid = os.getpid()

    stdin = subprocess.check_output(["ps", "-u", user_name])

    processes = []

    processes = [(int(re.match(" *[0-9]+", line).group()), line.split(' ')[-1]) for line in stdin.split('\n')[1:-1]]

    for process in processes:

        if re.match(re_pattern, process[1]) and process[0] != current_pid:
#            print "KILLING PID: ", process
            os.kill(process[0], signal.SIGKILL)

# EOF

