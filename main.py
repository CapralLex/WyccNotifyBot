from threading import Thread
from time import time, ctime, sleep

import file_proc
import longpoll_thread
import steam_thread
import tg_thread
import twitch_thread
import yt_thread


def start():
    try:

        Thread(target=steam_thread.start_steam).start()
        print('Steam thread running')

        Thread(target=longpoll_thread.start_longpoll).start()
        print('Longpoll thread running')

        Thread(target=twitch_thread.start_twitch).start()
        print('Twitch thread running')

        Thread(target=yt_thread.start_yt).start()
        print('YouTube thread running')

        tg_thread.start_tg()

    except Exception as exception:
        file_proc.error_log(str(exception) + '| MAIN_STARTER')
        print(exception, ctime(time()), 'MAIN_STARTER')
        sleep(120)
        start()


if __name__ == "__main__":
    start()
