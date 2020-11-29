import os
from time import sleep

from loguru import logger
from telethon import connection
from telethon.sync import TelegramClient, events

import main
import vk_
from file_handler import read_config


@logger.catch(onerror=lambda _: main.restart_thread(start_tg, 'telegram'))
def start_tg():
    channel = read_config('telegram', 'channel')
    api_id = read_config('telegram', 'api_id')
    api_hash = read_config('telegram', 'api_hash')
    use_proxy = read_config('telegram', 'proxy')

    if use_proxy == 'True':
        proxy = (read_config('telegram', 'p_server'),
                 int(read_config('telegram', 'p_port')),
                 read_config('telegram', 'p_secret'))

        client = TelegramClient('wycc_parser',
                                api_id, api_hash,
                                connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                                proxy=proxy)
    else:
        client = TelegramClient('wycc_parser', api_id, api_hash)

    client.start()
    print('Telegram thread running')

    def callback(current, total):
        print('Downloaded', current, 'out of', total, 'bytes: {:.2%}'.format(current / total))

    @client.on(events.NewMessage(chats=channel))
    async def handler(event):
        vk_data = event.message.to_dict()
        vk_message = vk_data['message']
        vk_media = vk_data['media']
        message_to_send = 'В Telegram канале Шусса новый пост:'

        if vk_message != '':
            vk_.send(message=f'{message_to_send}\n\n"{vk_message}"', category='telegram')

        if vk_media is not None:
            file = await client.download_media(message=event.message, progress_callback=callback)
            media_type = vk_media['_']
            if media_type == 'MessageMediaPhoto':
                vk_.send_photo(file, message_to_send)

            elif media_type == 'MessageMediaDocument':
                if '.tgs' not in file and 'sticker' not in file:
                    vk_.send_doc(file, message_to_send)
                else:
                    logger.warning('Telegram sticker detected')

            elif media_type == 'MessageMediaPoll':
                poll_title = vk_media['poll']['question']
                answers = []
                for ans in vk_media['poll']['answers']:
                    answers.append(ans['text'])
                quiz_message = f'В Telegram канале Шусса новый опрос:\n\n"{poll_title}"\n'
                for n in range(len(answers)):
                    quiz_message += f'\n{n+1}) {answers[n]}'
                vk_.send(message=quiz_message, category='telegram')

            os.remove(file)  # Удаляем уже ненужный файл

    try:
        client.run_until_disconnected()
    except Exception as exception:
        logger.error(f'{exception} | TG_T')
        sleep(int(read_config('data', 'delay')))
