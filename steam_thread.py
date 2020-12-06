from time import time, sleep

from loguru import logger
from requests import get

import main
import twitch_thread
import vk_
from file_handler import read_config, write_config


@logger.catch(onerror=lambda _: main.restart_thread(start_steam, 'longpoll'))
def start_steam():

    print('Steam thread running')

    steam_key = read_config('steam', 'key')
    status = 'NO_STATUS'
    game = 'NO_GAME'
    timer_started = None
    timer_status = False
    already_with_streamer = False
    wycc_id = read_config('steam', 'wycc_id')

    while True:
        bad_games = read_config('steam', 'bad_games', list_=True)

        try:
            r = get(f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key='
                    f'{steam_key}&steamids={wycc_id}')
            req_proc = r.json()['response']['players'][0]
        except Exception as exception:
            restart_timer = int(read_config('data', 'delay'))
            logger.error(f'{exception} | STEAM_T')
            print(f'Сontinue after {restart_timer} seconds (steam) ...')
            sleep(restart_timer)
            continue

        req_visible = str(req_proc['communityvisibilitystate'])

        # Если профиль Steam закрыт
        if req_visible == '1':
            # Если в конфиге значение другое
            if req_visible != read_config('data', 'visible_status'):
                write_config('data', 'visible_status', '1')
                vk_.send(message='Wycc закрыл свой профиль Steam 😕', category=['steam', 'на_стриме_банды'])
                logger.warning('Visible_status in config.ini was changed to 1')
            sleep(3600)
            continue

        # Если профиль открыт и в конфиге значение отличается
        elif req_visible == '3' and req_visible != read_config('data', 'visible_status'):
            write_config('data', 'visible_status', '3')
            vk_.send(message='Wycc открыл свой профиль Steam 😎', category=['steam', 'на_стриме_банды'])
            logger.warning('Visible_status in config.ini was changed to 3')

        req_status = req_proc['personastate']  # 0 offline, 1-6 online

        if req_status == 0:  # Если оффлайн

            # log
            if status != 'offline':
                logger.info('Wycc Steam now is offline')

            # TODO: Убрать постоянное обновление переменных
            status = 'offline'
            already_with_streamer = False

            if timer_status:  # Если таймер был вкл
                exit_status = 'in_offline'
                secs = int(time() - timer_started)  # Завершаем подсчет секунд

                if secs >= 600:  # Защита: если играл меньше - не отправляем
                    vk_.send_with_time(game, secs, exit_status)  # Передаем секунды и игру в функцию

                timer_status = False  # Меняем статус таймера на выкл

            sleep(30)

        elif req_status != 0 and 'gameextrainfo' not in req_proc:  # Если онлайн и нету игры

            # log
            if status != 'online':
                logger.info('Wycc Steam now is online')

            status = 'online'
            already_with_streamer = False

            if timer_status:  # Если таймер был вкл
                exit_status = 'in_online'
                secs = int(time() - timer_started)  # Завершаем подсчет секунд

                if secs >= 600:  # Защита: если играл меньше - не отправляем
                    vk_.send_with_time(game, secs, exit_status)  # Передаем секунды и игру в функцию

                timer_status = False  # Меняем статус таймера на выкл

            sleep(15)

        elif req_status != 0 and 'gameextrainfo' in req_proc:  # Если онлайн и есть игры
            game = req_proc['gameextrainfo']

            # Если "неправильная" игра, то скипаем итерацию
            if game in bad_games:
                sleep(60)
                continue

            if status != game:  # Если новая игра

                # log
                logger.info(f'Wycc Steam now in {game}')

                if not timer_status:  # Если таймер выкл
                    timer_started = time()  # Засекаем начало отсчета
                    timer_status = True  # Меняем статус таймера на вкл

                elif timer_status:  # Если таймер вкл
                    exit_status = 'in_other_game'
                    secs = int(time()-timer_started)  # Завершаем подсчет секунд

                    if secs >= 600:  # Защита: если играл меньше - не отправляем
                        vk_.send_with_time(game, secs, exit_status)  # Передаем секунды и игру в функцию

                    timer_started = time()  # Запускаем таймер сразу же еще раз

                status = game  # Обновляем переменную с игрой
                already_with_streamer = False

            elif status == game:  # Если все еще в предыдущей игре

                # Проверка на совместный стрим
                if not already_with_streamer:
                    with_streamer = twitch_thread.get_good_streamers(game)
                    if with_streamer is not None:
                        message = f'Возможно Wycc и {with_streamer} играют вместе в {game} на стриме' \
                                  f'\n\ntwitch.tv/{with_streamer.lower()}'
                        vk_.send(message, category='на_стриме_банды')
                        already_with_streamer = True

            sleep(30)
