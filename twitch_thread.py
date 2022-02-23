from time import sleep, time

from loguru import logger
from twitchAPI.twitch import Twitch

import main
import vk_
from file_handler import read_config


def tw_auth():
    twitch_client = Twitch(read_config('twitch', 'client_id'), read_config('twitch', 'client_secret_id'))
    return twitch_client


def get_good_streamers(wycc_game):
    wycc_game = wycc_game.replace(':', '').replace('™', '')  # Некоторые игры в стиме и твитче называются по разному
    streamer_names = read_config('twitch', 'streamers', list_=True)
    bad_coop_streaming_games = read_config('twitch', 'bad_coop_streaming_games', list_=True)
    streamers_names = []
    streamers_links = []

    twitch = tw_auth()
    streamers_live = twitch.get_streams(user_login=streamer_names)['data']
    for streamer in streamers_live:
        streamer_game = streamer['game_name'].replace(':', '').replace('™', '')
        if streamer_game == wycc_game and wycc_game not in bad_coop_streaming_games:
            streamers_names.append(streamer['user_name'])
            streamers_links.append(f"\n\ntwitch.tv/{streamer['user_login']}")

    return streamers_names, streamers_links


@logger.catch(onerror=lambda _: main.restart_thread(start_twitch, 'twitch'))
def start_twitch():

    print('Twitch thread running')

    twitch = tw_auth()
    already_live = False
    bad_games = read_config('twitch', 'bad_games')
    game = str()
    start_stream_timer = None

    try:
        while True:
            wycc_live = twitch.get_streams(user_login=['elwycco'])['data']

            if len(wycc_live):
                current_game = wycc_live[0]['game_name']

                if not already_live:

                    logger.info('Wycc twitch online')

                    already_live = True
                    start_stream_timer = time()
                    vk_.send(message='Wycc подрубил стрим\ntwitch.tv/elwycco', category='twitch')
                    sleep(60)

                elif already_live:

                    if current_game != game and current_game.lower() not in bad_games:
                        message = f'Текущая игра на стриме: {current_game}'
                        vk_.send(message=message, category='twitch')
                        logger.info(f'Wycc streaming game changed to {current_game}')
                        game = current_game
                    else:
                        sleep(30)

            elif already_live and wycc_live is None:
                logger.info('Wycc twitch offline')
                already_live = False

                end_stream_timer = int(time() - start_stream_timer)
                h = end_stream_timer // 3600
                m = (end_stream_timer - h * 3600) // 60

                vk_.send(message=f'Wycc закончил стрим. Он длился {h}ч. {m}м.\nСледующий стрим через час 🌚', category='twitch')
                game = ''
                sleep(60)

            sleep(2)

    except Exception as exception:
        restart_timer = int(read_config('data', 'delay'))
        logger.error(f'{exception} | TWITCH_T')
        print(f'Restart after {restart_timer} seconds (twitch) ...')
        sleep(restart_timer)
        start_twitch()
