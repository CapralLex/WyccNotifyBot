from threading import Thread
from time import sleep

from loguru import logger

import longpoll_thread
import steam_thread
import tg_thread
import twitch_thread
import vk_
import yt_thread
from file_handler import read_config


def restart_thread(err_thread, thread_name):
    delay = int(read_config('data', 'delay'))
    logger.critical(f'CRITICAL ERROR: {thread_name}')
    vk_.send_emergency(thread_name, delay)
    sleep(delay)
    err_thread()  # Рестарт функции, которая бросила исключение


def start_all_threads():
    Thread(target=longpoll_thread.start_longpoll).start()

    Thread(target=steam_thread.start_steam).start()

    Thread(target=twitch_thread.start_twitch).start()

    Thread(target=yt_thread.start_yt).start()

    tg_thread.start_tg()


if __name__ == "__main__":
    logger.add('logs.log', encoding="utf8")
    start_all_threads()
