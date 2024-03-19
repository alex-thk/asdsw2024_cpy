# from: https://github.com/spurin/python-ipc-examples

import logging
import os
import time
import multiprocessing
from multiprocessing import Process

# Process1 logic
def process1(pipe):
    process1_logger = logging.getLogger('process1') #questo è un oggetto di tipo logger, usato per loggare le informazioni su schermo
    # in questo caso si fa un log a livello informativo
    process1_logger.info(f"Pid:{os.getpid()}")

    # Open the file descriptor
    file = os.fdopen(pipe.fileno(), 'w') #aperta la pipe in scrittura
    process1_logger.info("Opened file descriptor")

    # Write 10 entries
    for i in range(1,11):

        # Attempt to write to our pipe until succession
        while True:
            try:
                process1_logger.info(f"Writing {int(i)}")
                file.write(f"{i}\n")
                file.flush()
                if i % 6 == 0:
                    process1_logger.info("Intentionally sleeping for 5 seconds")
                    time.sleep(5)
                break
            except:
                pass

    # Clean up pipe
    pipe.close()

    # Log completion
    process1_logger.info("Finished process 1")


# Process2 logic
def process2(pipe):
    process2_logger = logging.getLogger('process2')
    process2_logger.info(f"Pid:{os.getpid()}")

    # Open the file descriptor
    file = os.fdopen(pipe.fileno(), 'r') # qui la pipe viene aperta in lettura
    process2_logger.info("Opened file descriptor")

    # Expect 10 entries
    count = 0
    while count < 10:
        while True:
            try:
                line = file.readline()
                process2_logger.info(f"Read: {int(line)}")
                count += 1
                break
            except Exception:
                pass

    # Clean up pipe
    pipe.close()

    # Log completion
    process2_logger.info("Finished process 2")


# Main
def main():

    # Setup parent logger and log pid
    parent_logger = logging.getLogger('parent')
    parent_logger.info(f"Pid:{os.getpid()}")

    # Setup pipe
    r, w = multiprocessing.Pipe(False)

    # Setup processes
    # al processo 1 viene passata la pipe in scrittura
    # al processo 2 viene passata la pipe in lettura
    procs = [Process(target=process1, args=(w,)), Process(target=process2, args=(r,))]

    # Start processes
    for proc in procs:
        proc.start()

    # Run to completion
    for proc in procs:
        proc.join()

# Setup simple logging
logging.basicConfig(level=logging.INFO)

# Execute main
if __name__ == '__main__':
    main()

# le pipe servono per trasferire informazioni da un processo ad un altro processo in modo che i processi possano
# comunicare