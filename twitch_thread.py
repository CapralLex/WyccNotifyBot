from time import sleep, time, ctime, strftime

from loguru import logger
from twitch import TwitchClient

import main
import vk_
from file_handler import read_config


def tw_auth():
    twitch_client = TwitchClient(client_id=read_config('twitch', 'client_id'))
    return twitch_client


def get_good_streamers(game):
    # Чекаем игры всех стримеров на совпадение с игрой Wycc`a
    game = game.replace(':', '')  # Некоторые игры в стиме и твитче называются по разному
    streamer_names = read_config('twitch', 'streamers', list_=True)
    twitch_client = tw_auth()
    streamers = twitch_client.users.translate_usernames_to_ids(streamer_names)
    for streamer in streamers:
        streamer_live = twitch_client.streams.get_stream_by_user(channel_id=streamer['id'])
        if streamer_live is not None:
            streamer_game = streamer_live['game'].replace(':', '')
            if streamer_game == game:
                streamer_name = streamer_live['channel']['display_name']
                logger.info(f'with_twitch {streamer_name} {game}')
                return streamer_name


@logger.catch(onerror=lambda _: main.restart_thread(start_twitch, 'twitch'))
def start_twitch():

    print('Twitch thread running')

    twitch_client = tw_auth()
    already_live = False
    bad_games = read_config('twitch', 'bad_games')
    wycc_id = read_config('twitch', 'wycc_id')
    game = str()
    start_stream_timer = None

    try:
        while True:
            wycc_live = twitch_client.streams.get_stream_by_user(wycc_id)

            if wycc_live is not None:
                current_game = wycc_live['game']

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
