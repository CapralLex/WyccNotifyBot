from threading import Thread

import longpoll_thread
import steam_thread
import twitch_thread
import yt_thread

if __name__ == "__main__":
    Thread(target=steam_thread.start_steam).start()
    print('Steam thread running')

    Thread(target=longpoll_thread.start_longpoll).start()
    print('Longpoll thread running')

    Thread(target=twitch_thread.start_twitch).start()
    print('Twitch thread running')

    Thread(target=yt_thread.start_yt).start()
    print('YouTube thread running')

    # tg_thread.start_tg()