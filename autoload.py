import Main
import time
from function_common import *

if __name__ == "__main__":
    time_load = readinfo_json("autoload")
    while (True):
        Main.process_FILTER() 
        print("Dowload mail thanh cong")
        if readinfo_json("Exit_program") == False:
            time.sleep(time_load);
        else:
           break
