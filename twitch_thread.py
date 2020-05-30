from time import ctime, time, sleep

import file_proc
import twitch_
import vk_


def start_twitch():
    twitch_client = twitch_.tw_auth()
    already_live = False

    try:
        while True:
            wycc_live = twitch_client.streams.get_stream_by_user(94849379)

            if not already_live and wycc_live is not None:
                print('Wycc twitch online!')
                file_proc.wycc_log('start_stream')
                already_live = True
                vk_.send(message='Wycc подрубил стрим\ntwitch.tv/elwycco', category='twitch')
                sleep(1800)
            elif already_live and wycc_live is None:
                print('Wycc twitch offline')
                already_live = False
                sleep(15)

            sleep(2)

    except Exception as exception:
        file_proc.error_log(str(exception) + '| TWITCH')
        print(exception, ctime(time()), 'TWITCH')
        sleep(120)
        start_twitch()
