from vk_api import VkApi, VkUpload, exceptions
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

import file_handler
from file_handler import read_config
from longpoll_thread import logger


def vk_auth():
    vk_session = VkApi(token=read_config('vk', 'token'))
    vk = vk_session.get_api()
    return vk


def vk_auth_upload():
    vk_session = VkApi(token=read_config('vk', 'token'))
    upload = VkUpload(vk_session)
    return upload


def send(message, category):
    vk = vk_auth()
    users = file_handler.read_users(category, separated=True)
    for list_of_users in users:
        try:
            vk.messages.send(user_ids=list_of_users, message=message, random_id=0)
            # print(f'Отправка сообщения: {list_of_users = }, {len(list_of_users) = }')
        except exceptions.VkApiError as exception:
            logger.error(f'{exception} | VK(send)')


def send_once(user_id, message):
    vk = vk_auth()
    try:
        vk.messages.send(user_id=user_id, message=message, random_id=0)
    except exceptions.VkApiError as exception:
        logger.error(f'{exception} | VK(send_once)')


def send_emergency(thread, delay):
    vk = vk_auth()
    admins = read_config('data', 'admins', list_=True)
    message = f'ЧП: Аварийная остановка потока {thread}. Попытка автоматического перезапуска через {delay} секунд...'
    try:
        vk.messages.send(user_ids=admins, message=message, random_id=0)
    except exceptions.VkApiError as exception:
        logger.error(f'{exception} | VK(send_once)')


def send_with_keyboard(user_id, message):
    vk = vk_auth()
    keyboard = create_keyboard(user_id)
    try:
        vk.messages.send(user_id=user_id, message=message, keyboard=keyboard, random_id=0)
    except exceptions.VkApiError as exception:
        logger.error(f'{exception} | VK(send_keyboard)')


def send_with_time(game, secs, exit_status):
    vk = vk_auth()
    h = secs // 3600
    m = (secs-h*3600)//60
    hm = f'{h}h. {m}m.'
    users = file_handler.read_users(category='steam', separated=True)

    if exit_status == 'in_offline' or exit_status == 'in_online' or exit_status == 'in_other_game':
        message = f'Шусс играл в {game}. Сессия длилась {hm}'
        for list_of_users in users:
            try:
                vk.messages.send(user_ids=list_of_users, message=message, random_id=0)
            except exceptions.VkApiError as exception:
                logger.error(f'{exception} | VK(send_timer)')

        logger.info(f'Wycc played in {game}. Session time: {hm}')


def send_photo(file, message):
    users = file_handler.read_users(category='telegram', separated=True)
    vk = vk_auth()
    upload = vk_auth_upload()
    ready_file = upload.photo_messages(photos=file)
    attach = f'photo{ready_file[0]["owner_id"]}_{ready_file[0]["id"]}'
    for list_of_users in users:
        try:
            vk.messages.send(user_ids=list_of_users, message=message, attachment=attach, random_id=0)
        except exceptions.VkApiError as exception:
            logger.error(f'{exception} | VK(send_photo)')

    logger.info('Photo send successfully')


def send_doc(file, message):
    users = file_handler.read_users(category='telegram', separated=True)
    vk = vk_auth()
    upload = vk_auth_upload()
    ready_file = upload.document_message(doc=file, title=file, peer_id=154348822)
    attach = f'doc{ready_file["doc"]["owner_id"]}_{ready_file["doc"]["id"]}'
    for list_of_users in users:
        try:
            vk.messages.send(user_ids=list_of_users, message=message, attachment=attach, random_id=0)
        except exceptions.VkApiError as exception:
            logger.error(f'{exception} | VK(send_doc)')

    logger.info('Doc send successfully')


def send_doc_once(file, message, user_id):
    vk = vk_auth()
    upload = vk_auth_upload()
    ready_file = upload.document_message(doc=file, title=file, peer_id=154348822)
    attach = f'doc{ready_file["doc"]["owner_id"]}_{ready_file["doc"]["id"]}'
    try:
        vk.messages.send(user_id=user_id, message=message, attachment=attach, random_id=0)
    except exceptions.VkApiError as exception:
        logger.error(f'{exception} | VK(send_doc)')

    logger.info('Doc send successfully')


def create_keyboard(user_id):
    keyboard = VkKeyboard(one_time=False)
    data = file_handler.read_users(raw=True)
    if user_id in data['steam']:
        keyboard.add_button('Отписаться от Steam', color=VkKeyboardColor.NEGATIVE)
    else:
        keyboard.add_button('Подписаться на Steam', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()

    if user_id in data['twitch']:
        keyboard.add_button('Отписаться от Twitch', color=VkKeyboardColor.NEGATIVE)
    else:
        keyboard.add_button('Подписаться на Twitch', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()

    if user_id in data['twitch_games']:
        keyboard.add_button('Отписаться от Twitch_games', color=VkKeyboardColor.NEGATIVE)
    else:
        keyboard.add_button('Подписаться на Twitch_games', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()

    if user_id in data['на_стриме_банды']:
        keyboard.add_button('Отписаться от На_стриме_банды', color=VkKeyboardColor.NEGATIVE)
    else:
        keyboard.add_button('Подписаться на На_стриме_банды', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()

    if user_id in data['telegram']:
        keyboard.add_button('Отписаться от Telegram', color=VkKeyboardColor.NEGATIVE)
    else:
        keyboard.add_button('Подписаться на Telegram', color=VkKeyboardColor.POSITIVE)
    keyboard.add_line()

    if user_id in data['youtube']:
        keyboard.add_button('Отписаться от YouTube', color=VkKeyboardColor.NEGATIVE)
    else:
        keyboard.add_button('Подписаться на YouTube', color=VkKeyboardColor.POSITIVE)

    return keyboard.get_keyboard()
