from threading import Thread

import steam_thread
import longpoll_thread
import twitch_thread
import tg_thread


if __name__ == "__main__":
    Thread(target=steam_thread.start_steam).start()
    print('Steam thread running')

    Thread(target=longpoll_thread.start_longpoll).start()
    print('Longpoll thread running')

    Thread(target=twitch_thread.start_twitch).start()
    print('Twitch thread running')

    # tg_thread.start_tg()