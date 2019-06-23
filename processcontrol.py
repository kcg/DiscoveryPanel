#!/usr/bin/env python
#-*- coding: utf-8 -*-


import subprocess
import os
import signal
from threading import Thread
from queue import Queue, Empty
import time
import psutil


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
                                        start_new_session=True,
                                        encoding="utf-8")
        self.queue = Queue()
        if not self.thread:
            self.thread = Thread(target=self.output_reader)
            self.thread.setName("PCoutputThread_" + self.name)
            self.thread.daemon = True
            self.thread.start()
        time.sleep(0.05)
        if self.is_running():
            return True
        else:
            return False

    def output_reader(self):
        while not self.process is None:
            self.queue.put(self.process.stdout.readline())
            time.sleep(0.05) # this is important and without it would slow down the MainThread
        time.sleep(0.05)

    def stop(self):
        try:
            current_process = psutil.Process(self.process.pid)
            children = current_process.children(recursive=True)
            for child in children:
                child.terminate()
        except:
            pass
        self.process.terminate()

    def kill(self):
        try:
            current_process = psutil.Process(self.process.pid)
            children = current_process.children(recursive=True)
            for child in children:
                child.kill()
        except:
            pass
        self.process.kill()

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
    #p1 = ProcessControl("Test1", "ls -l")
    #p1.start()
    #time.sleep(2)
    #print(p1.get_output())
    #p1.stop()

    # Long running command
    p2 = ProcessControl("Test2", "./testscript.sh")
    p2.start()
    startt = time.time()
    t = 0
    while t < 2:
        t = time.time() - startt
        print(p2.get_output())
        time.sleep(0.2)
    p2.kill()
    time.sleep(1)
    p2.start()
    time.sleep(3)
    print(p2.get_output())
    p2.kill()
    print("Done.")
