import pathlib
import subprocess
import time
import logging
import os
from tqdm import tqdm

class Frontier:
    FRONTIER_PATH = pathlib.Path("/home/toscan/dev/bd/frontier")
    EXAMPLE_PATH = FRONTIER_PATH / pathlib.Path("seep-system/examples/acita_demo_2015")

    SEEP_JAR = EXAMPLE_PATH / pathlib.Path("lib/seep-system-0.0.1-SNAPSHOT.jar")
    QUERY_JAR = EXAMPLE_PATH / pathlib.Path("dist/acita_demo_2015.jar")

    LOGS_DIR = pathlib.Path("./logs")
    RESULTS_DIR = pathlib.Path("./results")

    def __init__(self, nWorkers: int):
        self.nWorkers = nWorkers
        self.env = {
            'numTuples': '100',
        }

    def startMaster(self):
        with open(self.LOGS_DIR / 'master.log', 'w') as log:
            args = [ 'java', '-DnumTuples=100', '-jar', self.SEEP_JAR, 'Master', self.QUERY_JAR, 'Base' ]
            p =  subprocess.Popen(
                args, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT,
                preexec_fn=os.setsid, env=self.env
            )
            time.sleep(2)
            return p

    def startWorker(self, port: int):
        # with open(self.LOGS_DIR / f'worker-{port}.log', 'w') as log:
        args = [ 'java', '-DnumTuples=100', '-jar', self.SEEP_JAR, 'Worker', str(port) ]
        p = subprocess.Popen(
            args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            preexec_fn=os.setsid, env=self.env
        )
        time.sleep(1)
        return p

    def deployQuery(self, master: subprocess.Popen) -> bool:
        if master.stdin:
            master.stdin.write(b'1\n')
            time.sleep(10)
            return True
        return False

    def runQuery(self, master: subprocess.Popen) -> bool:
        if master.stdin:
            master.stdin.write(b'2\n')
            time.sleep(2)
            return True
        return False

    def deployAndRunQuery(self, master: subprocess.Popen) -> bool:
        if master.stdin:
            master.stdin.write(b'7\n')
            master.stdin.flush()
            time.sleep(1)
            return True
        return False



    def start(self):
        logging.info("Starting Master ...")
        self.master = self.startMaster()
        logging.info("Starting Workers ...")
        self.workers = [ self.startWorker(3501 + i) for i in range(self.nWorkers) ]

        source = self.workers[0]
        sink = self.workers[1]
        operators = self.workers[2:]

        logging.info("Deploying Query and Run ...")
        self.deployAndRunQuery(self.master)

        logging.info("Waiting for Workers to finish ...")

        # read sink output until it finishes
        N_TUPLES = 2000
        KILL_AT = 1000

        tuplesDone = 0
        progress = tqdm(total=N_TUPLES, desc="Sink Progress")
        with open(self.RESULTS_DIR / 'sink.csv', 'w') as log:
            if sink.stdout:
                for line in sink.stdout:
                    line = line.decode('utf-8')
                    if line.startswith("PY,"):
                        log.write(line[3:])
                        progress.update(1)
                        tuplesDone += 1
                        
                        if tuplesDone == KILL_AT:
                            print("Killing Operator 10")
                            operators[1].kill()

                sink.wait()
        self.stop()

    def stop(self):
        print("Stopping Frontier ...")
        if self.master:
            self.master.kill()
        if self.workers:
            for w in self.workers:
                if w:
                    w.kill()
        time.sleep(1)
