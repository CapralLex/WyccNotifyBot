import os
from time import sleep, time, ctime

from loguru import logger
from requests.exceptions import ConnectionError
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

import file_handler
import main
import vk_
from file_handler import read_config, write_users


MSG_HELLO = '''Теперь ты будешь получать все мои уведомления 😎
    
Чтобы настроить уведомления - воспользуйся моей клавиатурой.
    
Если твое приложение не поддерживает клавиатуру - отправь мне команду "помощь" или "help"'''

MSG_HELP = '''Чтобы подписаться на все уведомления - отправь мне команду "Начать".

Список доступных команд:

Подписаться на Steam - если Шусс играл в игру через Steam - пришлю название игры и время сессии.
Подписаться на Twitch - пришлю уведомление, если Шусс запустит стрим или сменит игру на стриме.
Подписаться на На_стриме_банды - пришлю уведомление, если велик шанс, что Шусс сидит на стриме у кого-нибудь из банды.
Подписаться на Telegram - перешлю пост из Telegram канала Шусса.
Подписаться на Youtube - если на основном или втором канале выйдет новое видео - пришлю тебе его.

Примеры изменения настроек без клавиатуры: "Подписаться на Telegram", "Отписаться от На_стриме_банды" и т.п.'''

ADMIN_HELP = '''/help
/backup
/get_users
/get_logs
/send [категория] {текст сообщения}
/send_test [категория] {текст сообщения}
/stop'''


def vk_lp_auth():
    vk_session = VkApi(token=read_config('vk', 'token'))
    longpoll = VkLongPoll(vk_session)
    return longpoll


@logger.catch(onerror=lambda _: main.restart_thread(start_longpoll, 'longpoll'))
def start_longpoll():

    print('Longpoll thread running')

    available_commands = file_handler.read_users(raw=True).keys()
    admins = [int(_) for _ in read_config(section='data', key='admins', list_=True)]
    try:
        longpoll = vk_lp_auth()
        for event in longpoll.listen():

            # print(event.__dict__)

            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                text = str(event.text).lower().split(' ')
                user_id = event.user_id

                # --- start ---
                if text[0] == 'начать' or text[0] == 'start' or text[0] == 'старт':
                    debug_timer = time()
                    write_status = write_users(user=user_id, category='all')
                    if write_status:
                        vk_.send_with_keyboard(user_id=user_id, message=MSG_HELLO)
                        logger.debug(f'{user_id} subscribed to all. Complete in {time() - debug_timer}')
                    else:
                        vk_.send_with_keyboard(user_id=user_id, message='Ты уже подписан(а) на все уведомления')

                # --- main commands ---
                elif len(text) == 3 and text[2] in available_commands:
                    debug_timer = time()
                    if text[0] == 'подписаться' and text[1] == 'на':
                        write_users(user=user_id, category=text[2])
                        vk_.send_with_keyboard(user_id=user_id,
                                               message=f'Теперь ты будешь получать уведомления {text[2]}')
                        logger.debug(f'{user_id} subscribed on {text[2]}. Complete in {time()-debug_timer}')
                    elif text[0] == 'отписаться' and text[1] == 'от':
                        file_handler.delete_users(user=user_id, category=text[2])
                        vk_.send_with_keyboard(user_id=user_id,
                                               message=f'Теперь ты не будешь получать уведомления {text[2]}')
                        logger.debug(f'{user_id} unsubscribed from {text[2]}. Complete in {time()-debug_timer}')

                # --- help ---
                elif text[0] == 'помощь' or text[0] == 'help' or text[0] == 'хелп':
                    vk_.send_once(user_id=user_id, message=MSG_HELP)

                elif text[0] == 'енот' and text[1] == 'пидор':
                    vk_.send_photo_once(user_id=user_id, photo_link='photo-190892622_457239054', message='Вот он - роковой мужчина 😎🤙🏻')

                # --- Админ команды ---
                elif event.peer_id in admins:

                    if text[0] == '/help':
                        vk_.send_once(user_id=user_id, message=ADMIN_HELP)

                    elif text[0] == '/backup':
                        vk_.send_doc_once(file='users.json', message=ctime(time()), user_id=user_id)

                    elif text[0] == '/get_users':
                        user_stats = file_handler.get_all_users()
                        vk_.send_once(user_id=user_id, message=str(user_stats))

                    elif text[0] == '/get_logs':
                        vk_.send_doc_once(file='logs.log', message=ctime(time()), user_id=user_id)

                    elif text[0] == '/send' or text[0] == '/send_test':
                        _category = event.text[event.text.find('[')+1:event.text.find(']')]
                        _text = event.text[event.text.find('{')+1:event.text.find('}')]

                        if _category not in available_commands:
                            vk_.send_once(user_id=user_id, message='Категория не найдена')
                            continue

                        if text[0] == '/send':
                            vk_.send(message=_text, category=_category)
                        else:
                            vk_.send_once(user_id=user_id, message=f'Категория: "{_category}"\n\n{_text}')

                    elif text[0] == '/stop':
                        vk_.send_once(user_id=user_id, message='Выключение...')
                        os.abort()

                    else:
                        vk_.send_once(user_id=user_id, message='''Неизвестная команда 😕 
                                                                Если что-то непонятно - отправь мне команду "Помощь".''')
                else:
                    vk_.send_once(user_id=user_id, message='''Неизвестная команда 😕 
                                                            Если что-то непонятно - отправь мне команду "Помощь".''')

    except ConnectionError:
        sleep(5)
        start_longpoll()

    except Exception as exception:
        restart_timer = int(read_config('data', 'delay'))
        logger.error(f'{exception} | LONGPOLL_T')
        print(f'Restart after {restart_timer} seconds (longpoll) ...')
        sleep(restart_timer)
        start_longpoll()
