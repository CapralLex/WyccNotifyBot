import os
from time import time, sleep, ctime

from telethon import connection
from telethon.sync import TelegramClient, events

import file_proc
import vk_
from file_proc import read_config


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
            print('Telegram txt post send successfully')

        if vk_media is not None:
            file = await client.download_media(message=event.message, progress_callback=callback)
            mediatype = vk_media['_']
            if mediatype == 'MessageMediaPhoto':
                vk_.send_photo(file, message_to_send)

            elif mediatype == 'MessageMediaDocument':
                if '.tgs' not in file and 'sticker' not in file:
                    vk_.send_doc(file, message_to_send)
                else:
                    print('Warning: sticker')

            elif mediatype == 'MessageMediaPoll':
                poll_title = vk_media['poll']['question']
                answers = []
                for ans in vk_media['poll']['answers']:
                    answers.append(ans['text'])
                quiz_message = f'В Telegram канале Шусса новый опрос:\n\n"{poll_title}"\n'
                for n in range(len(answers)):
                    quiz_message += f'\n{n+1}) {answers[n]}'
                vk_.send(message=quiz_message, category='telegram')

            os.remove(file)  # Удаляем уже ненужный файл
            print(f'Photo "{file}" deleted')

    try:
        client.run_until_disconnected()
    except Exception as exception:
        file_proc.error_log(str(exception) + '| TG')
        print(exception, ctime(time()), 'TG')
        sleep(600)
