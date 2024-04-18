from src.modes import regular, mobile, generate, jacklinks, burgerking
from src.utils import findProduct, findAlbum, discord, loadTasks, cliLogger, checkoutAlert

import requests


import json
from multiprocessing import Process
from threading import Thread
import time
import os


def main():
    os.system("title " + "Bandcamp Bot")

    tasks = loadTasks.loadTasks()

    input(f"Press Enter to start {len(tasks)} tasks...")
    os.system('cls' if os.name == 'nt' else 'clear')
    count = 0


    threads = []
    for task in tasks:
        task["id"] = count
        count += 1

        if task["mode"] == "regular":
            threads.append(Thread(
                target=regular.bandCampRegular, args=(task,)))
        if task["mode"] == "mobile":
            threads.append(Thread(
                target=mobile.bandCampMobile, args=(task,)))
        if task["mode"] == "generate":
            threads.append(Thread(
                target=generate.bandCampGenerate, args=(task,)))


    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
