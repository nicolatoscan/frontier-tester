from ftest.args import get_args
import logging
from ftest.frontier import Frontier
import signal
import sys
import os
def kill(frontier):
    frontier.stop()
    sys.exit(0)

def main():
    
    args = get_args()
    logging.info(args)

    frontier = Frontier(args.processors)
    signal.signal(signal.SIGINT, lambda sig, frame: kill(frontier))
    frontier.start()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()



