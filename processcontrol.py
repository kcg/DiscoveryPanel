#!/usr/bin/env python
#-*- coding: utf-8 -*-


import subprocess
import os
import signal
from threading import Thread
from queue import Queue, Empty
import time


class ProcessControl:

    def __init__(self, name="", cmd=""):
        self.name = name
        self.command = cmd

    def start(self):
        self.process = subprocess.Popen("exec " + self.command,
                                        shell=True, 
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        preexec_fn=os.setsid,
                                        encoding="utf-8")

        self.queue = Queue()
        self.thread = Thread(target=self.output_reader)
        self.thread.daemon = True
        self.thread.start()

    def output_reader(self):
        for line in iter(self.process.stdout.readline, b''):
            self.queue.put(line)

    def stop(self):
        try:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            return True
        except:
            return False

    def kill(self):
        try:
            os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
            return True
        except:
            return False

    def get_output(self):
        out = ""
        while self.is_running:
            try:
                out += self.queue.get(block=False)
            except Empty:
                return out

    def is_running(self):
        if self.process.poll == None:
            return True
        else:
            return False


if __name__ == "__main__":

    # Simple list command
    p1 = ProcessControl("Test1", "ls -l")
    p1.start()
    print(p1.get_output())
    print(p1.get_error())
    p1.stop()

    # Long running command
    p2 = ProcessControl("Test2", "./script.sh")
    p2.start()
    print(p2.get_output())
    time.sleep(2)
    print("---")
    print(p2.get_output())
    time.sleep(2)
    print("---")
    print(p2.get_output())
    p2.kill()

    print("Done.")
