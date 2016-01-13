
import atexit
import signal
import os
import subprocess
import time

metamap_dir = os.path.join(*[os.environ["CLINER_DIR"], "cliner", "lib", "java", "metamap", "metamapBase", "public_mm", "bin"])

mmserver_path = os.path.join(metamap_dir, "mmserver")
skrmedpost_path = os.path.join(metamap_dir, "skrmedpostctl")

from kill_process import kill_process_by_name

devnull = open(os.devnull, "wb")
class MetaMapServer():

    mmserver = None
    skrmedpost = None

    def __init__(self):
        pass

    @staticmethod
    def start_server():

#        print "\nLoading metamap..."

        init_time = time.time()

        MetaMapServer.execute_skrmedpost()

        while True:

            MetaMapServer.execute_mmserver()

            time.sleep(10)

            return_code = MetaMapServer.mmserver.poll()

            if return_code not in [None, 0]:

                if (time.time() - init_time) > 120:

                    exit("Could not run memtap server...")

                else:

                    MetaMapServer.shutdown_server()
                    continue

            else:
                break

    @staticmethod
    def execute_skrmedpost():

        MetaMapServer.skrmedpost = subprocess.Popen([skrmedpost_path, "start"], stdout=devnull, stderr=subprocess.STDOUT)

    @staticmethod
    def kill_skrmedpost():

        MetaMapServer.skrmedpost = subprocess.Popen([skrmedpost_path, "stop"], stdout=devnull, stderr=subprocess.STDOUT)

    @staticmethod
    def execute_mmserver():

        if MetaMapServer.mmserver is None:
            MetaMapServer.mmserver = subprocess.Popen([mmserver_path], stdout=devnull, stderr=subprocess.STDOUT)


    @staticmethod
    def shutdown_server():
        kill_process_by_name("mmserver.*")
        os.kill(MetaMapServer.skrmedpost.pid, signal.SIGKILL)
        MetaMapServer.mmserver = None

    @staticmethod
    @atexit.register
    def cleanup():

        # kill all user processes with the name mmserver
        kill_process_by_name("mmserver.*")
        os.kill(MetaMapServer.skrmedpost.pid, signal.SIGKILL)
        MetaMapServer.mmserver = None
        MetaMapServer.kill_skrmedpost()
        devnull.close()

if __name__ == "__main__":

    MetaMapServer.start_server()

    while True:
        pass

