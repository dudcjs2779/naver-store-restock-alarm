import schedule
import time
import json
from scripts import soldout_ui

config = soldout_ui.get_config()

start_times = config['start_times']
print(config)
# print(type(config))
    

def print_something(msg):
    print(msg)


for start_time in start_times:
    schedule.every().day.at(start_time).do(soldout_ui.get_alarm)
    
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)