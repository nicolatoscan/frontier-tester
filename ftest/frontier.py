import pathlib
import subprocess
import time
import logging
import os
from tqdm import tqdm
import asyncio
from multiprocessing import Pool


def startWorker([port, worker]):
    

class Frontier:
    FRONTIER_PATH = pathlib.Path("/home/toscan/dev/bd/frontier")
    EXAMPLE_PATH = FRONTIER_PATH / pathlib.Path("seep-system/examples/acita_demo_2015")

    SEEP_JAR = EXAMPLE_PATH / pathlib.Path("lib/seep-system-0.0.1-SNAPSHOT.jar")
    QUERY_JAR = EXAMPLE_PATH / pathlib.Path("dist/acita_demo_2015.jar")

    LOGS_DIR = pathlib.Path("./logs")
    RESULTS_DIR = pathlib.Path("./results")

    N_TUPLES = 20000

    workers = []

    def __init__(self, nWorkers: int):
        self.nWorkers = nWorkers
        self.env = {
            'numTuples': '20000',
        }

    def startMaster(self):
        with open(self.LOGS_DIR / 'master.log', 'w') as log:
            args = [ 'java', '-DnumTuples=20000', '-jar', self.SEEP_JAR, 'Master', self.QUERY_JAR, 'Base' ]
            p =  subprocess.Popen(
                args, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT,
                preexec_fn=os.setsid, env=self.env
            )
            time.sleep(2)
            return p

    def startWorker(self, port: int):
        # with open(self.LOGS_DIR / f'worker-{port}.log', 'w') as log:
        print(f"Starting worker on port {port} ...")
        with open(self.LOGS_DIR / f'worker{port}.log', 'w') as log:
            args = [ 'java', '-DnumTuples=20000', '-jar', self.SEEP_JAR, 'Worker', str(port) ]
            p = subprocess.Popen(
                args, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT,
                preexec_fn=os.setsid, env=self.env
            )
            self.workers.append(p)
            time.sleep(1)

            if p.stdout:
                for line in p.stdout:
                    print(f"{port} - {line}")
            p.wait()

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

        ports = list(range(3501, 3501 + self.nWorkers + 2))

        pool = Pool(processes=len(ports))
        results = [pool.apply_async(run_parallel, (num, new_num_list, self.num_to_add)) # num_to_add is passed as an argument
                      for num in num_list]
        roots = [r.get() for r in results]
        pool.close()
        pool.terminate()
        pool.join()

        pool = Pool(processes=len(ports))
        time.sleep(5)
        self.stop()
        pool.map(self.startWorker, ports)
        # self.stop()
        # self.workers = [ self.startWorker(3501 + i) for i in range(self.nWorkers + 2) ]

    def oldStart(self):
        # source = self.workers[0]
        # sink = self.workers[1]
        # operators = self.workers[2:]

        # logging.info("Deploying Query and Run ...")
        # self.deployAndRunQuery(self.master)

        # logging.info("Waiting for Workers to finish ...")

        # # read sink output until it finishes
        # killEach = int( self.N_TUPLES / self.nWorkers ) + 1
        # print(f"Killing each operator after {killEach} tuples")

        # tuplesDone = 0
        # masterTask = asyncio.create_task(self.readOutput(self.master, "Master"))
        # sourceTask = self.readOutput(source, "Source")
        # sinkTask = self.readOutput(sink, "Sink")
        # operatorsTasks = [ self.readOutput(o, f"Operator {i}") for i, o in enumerate(operators) ]

        # ranges = [masterTask, sourceTask, sinkTask, *operatorsTasks]
        # pool = Pool(processes=len(ranges))
        # pool.map(self.readOutput, ranges)

        # await asyncio.gather(masterTask, sourceTask, sinkTask, *operatorsTasks)
        # await masterTask

        # progress = tqdm(total=self.N_TUPLES, desc="Sink Progress")
        # with open(self.RESULTS_DIR / 'sink.csv', 'w') as log:
        #     if sink.stdout:
        #         print('PARTIAMO')
        #         for line in sink.stdout:
        #             print(line)
                    # line = line.decode('utf-8')
                    # if line.startswith("PY,"):
                    #     log.write(line[3:])
                    #     # progress.update(1)
                    #     tuplesDone += 1
                        
                    #     if tuplesDone % killEach == 0:
                    #         idTokill = int(line.split(",")[-2])
                    #         print(f"Killing Operator {idTokill}")

                    #         if idTokill != 0:
                    #             idTokill -= 9

                    #         print(f"in pos {idTokill}")
                    #         # operators[int(idTokill)].kill()

                # print('Waiting')
                # sink.wait()
                # print('Waited')
        self.stop()

    def readOutput(self, p: subprocess.Popen, name: str):
        print(f"Reading {name} output ...")
        i = 0
        if p.stdout:
            for line in p.stdout:
                i += 1
                print(f"{name} - {line}")
        p.wait()

    def stop(self):
        print("Stopping Frontier ...")
        if self.master:
            self.master.terminate()
        if self.workers:
            for w in self.workers:
                if w:
                    w.terminate()

        time.sleep(1)
        # if self.master:
            # self.master.wait()
            # self.writeStdoutToFile(self.master, self.LOGS_DIR / 'master.log')
        # if self.workers:
            # for i, w in enumerate( self.workers ):
                # if w:
                    # w.wait()
                    # self.writeStdoutToFile(w, self.LOGS_DIR / f'worker-{i}.log')
        # time.sleep(1)

    def writeStdoutToFile(self, p: subprocess.Popen, filename: pathlib.Path):
        if p.stdout is None:
            print(f"Skipping {filename} because stdout is None")
            return
        with open(filename, 'w') as f:
            for line in p.stdout.read():
                line = line.decode('utf-8')
                f.write(line)