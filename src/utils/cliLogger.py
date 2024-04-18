from src.utils import getCurrentTime
def cliLogger(message, task, type="standard"):
    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    time_log = "[" + bcolors.HEADER + getCurrentTime.currentTime() + bcolors.ENDC + "] "
    task_id = "[" + bcolors.OKCYAN + str(task["id"]) + bcolors.ENDC + "] "
    
    if type == "standard":
        print(str(time_log + task_id + message))
    
    if type == "error":
        print(str(time_log + task_id + bcolors.FAIL + str(message) + bcolors.ENDC))

    if type == "success":
        print(str(time_log + task_id + bcolors.OKGREEN + str(message) + bcolors.ENDC))
    
    if type == "alert":
        print(str(time_log + task_id + bcolors.WARNING + str(message) + bcolors.ENDC))
    
    if type == "paypal":
        print(str(time_log + task_id + bcolors.OKCYAN + str(message) + bcolors.ENDC))
# cliLogger("Test", {"id": "1"}, "error")