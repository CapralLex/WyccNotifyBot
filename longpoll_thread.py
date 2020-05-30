from time import sleep, ctime, time

from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

import file_proc
import vk_
from file_proc import read_config


def vk_lp_auth():
    vk_session = VkApi(token=read_config('vk', 'token'))
    longpoll = VkLongPoll(vk_session)
    return longpoll


def start_longpoll():
    available_commands = file_proc.read_users(raw=True).keys()
    print(available_commands)
    try:
        longpoll = vk_lp_auth()
        for event in longpoll.listen():

            # print(event.type)
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                text = str(event.text).lower().split(' ')

                if text[0] == 'начать':
                    write_status = file_proc.write_users(user=event.user_id, category='all')
                    if write_status:
                        message = 'Вы подписались на уведомления 😎\n\nЧтобы настроить уведомления воспользуйтесь ' \
                                  'моей клавиатурой. \n\nЕсли ваше приложение не поддерживает клавитуру - отправьте ' \
                                  'мне команду "помощь" или "help"'
                        vk_.send_with_keyboard(user_id=event.user_id, message=message)
                    else:
                        vk_.send_with_keyboard(user_id=event.user_id, message='Вы уже подписаны на все уведомления')

                elif text[0] == 'помощь' or text[0] == 'help':
                    message = 'Список доступных команд:\n\n' \
                              'Подписаться на Steam - если Шусс играл в игру через Steam - пришлю название игры и ' \
                              'время сессии.\n' \
                              'Подписаться на Twitch - пришлю уведомление, если Шусс запустит стрим.\n' \
                              'Подписаться на На_стриме_банды - пришлю уведомление, если велик шанс, что Шусс сидит ' \
                              'на стриме у кого-нибудь из банды.\n' \
                              'Подписаться на Telegram - перешлю сообщение из Telegram канала Шусса.' \
                              '\n\nПримеры изменения настроек без клавиатуры:' \
                              '\n"Подписаться на Telegram", "Отписаться от На_стриме_банды" и т.п.'
                    vk_.send_once(user_id=event.user_id, message=message)

                elif len(text) == 3 and text[2] in available_commands:
                    if text[0] == 'подписаться' and text[1] == 'на':
                        file_proc.write_users(user=event.user_id, category=text[2])
                        vk_.send_with_keyboard(user_id=event.user_id,
                                               message=f'Теперь вы подписаны на уведомления {text[2]}')
                    elif text[0] == 'отписаться' and text[1] == 'от':
                        file_proc.delete_users(user=event.user_id, category=text[2])
                        vk_.send_with_keyboard(user_id=event.user_id,
                                               message=f'Теперь вы отписаны от уведомлений {text[2]}')

                else:
                    vk_.send_once(user_id=event.user_id, message='Неизвестная команда 😕')

    except Exception as exception:
        file_proc.error_log(str(exception) + '| LONGPOLL')
        print(exception, ctime(time()), 'LONGPOLL')
        sleep(120)
        start_longpoll()
