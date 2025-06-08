import logging
import os
from datetime import datetime

LOG_FORMAT = f"{datetime.now().strftime('%m_%d_%y_%H_%M_%S')}.log"

LOGS_PATH = os.path.join(os.getcwd(),'logs')
os.makedirs(LOGS_PATH,exist_ok=True)



FILE_PATH = os.path.join(LOGS_PATH,LOG_FORMAT)

logging.basicConfig(filename=FILE_PATH,
                    level=logging.INFO, 
                    format="%(asctime)s  %(lineno)d %(name)s - %(levelname)s - %(message)s")



if __name__ =='__main__':
    logging.info('Logging has started')



