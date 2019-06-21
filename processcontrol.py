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
        self.process = None
        self.name = name
        self.command = cmd
        self.thread = None

    def start(self):
        self.process = subprocess.Popen("exec " + self.command,
                                        shell=True, 
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        preexec_fn=os.setsid,
                                        encoding="utf-8")
        self.queue = Queue()
        if not self.thread:
            self.thread = Thread(target=self.output_reader)
            self.thread.setName("PCoutputThread_" + self.name)
            self.thread.daemon = True
            self.thread.start()

    def output_reader(self):
        while True and not self.process is None:
            self.queue.put(self.process.stdout.readline())
            time.sleep(0.05) # this is important and without it would slow down the MainThread

    def stop(self):
        self.stop_or_kill(sig=signal.SIGTERM)

    def kill(self):
        self.stop_or_kill(sig=signal.SIGKILL)

    def stop_or_kill(self, sig=signal.SIGTERM):
        try:
            os.killpg(os.getpgid(self.process.pid), sig)
            self.process = None
            return True
        except:
            return False
        time.sleep(0.05)

    def get_output(self):
        out = ""
        while self.is_running():
            try:
                out += self.queue.get(block=False)
            except Empty:
                return out

    def is_running(self):
        if self.process is None:
            return False
        if self.process.poll() is None:
            return True
        else:
            return False


if __name__ == "__main__":

    # Simple list command
    p1 = ProcessControl("Test1", "ls -l")
    p1.start()
    #time.sleep(2)
    print(p1.get_output())
    p1.stop()

    # Long running command
    """p2 = ProcessControl("Test2", "./testscript.sh")
    p2.start()
    print(p2.get_output())
    time.sleep(2)
    print("---")
    print(p2.get_output())
    time.sleep(2)
    print("---")
    print(p2.is_running())
    print(p2.get_output())
    time.sleep(2)
    print(p2.is_running())
    p2.kill()
    print("Done.")"""
