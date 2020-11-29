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
    logger.debug('Longpoll thread running')

    Thread(target=steam_thread.start_steam).start()
    logger.debug('Steam thread running')

    Thread(target=twitch_thread.start_twitch).start()
    logger.debug('Twitch thread running')

    Thread(target=yt_thread.start_yt).start()
    logger.debug('Youtube thread running')

    tg_thread.start_tg()


if __name__ == "__main__":
    logger.add('out.log')

    start_all_threads()
