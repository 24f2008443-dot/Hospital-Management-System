from datetime import datetime, time as dtime

def is_time_in_availabilities(avail_list, check_time):
    for a in avail_list:
        if a.start_time <= check_time < a.end_time:
            return True
    return False
