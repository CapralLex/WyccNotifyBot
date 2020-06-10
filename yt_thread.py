import xml.etree.ElementTree as ET
from time import sleep

import requests as r

import file_proc
import vk_


def req(url):
    try:
        response = r.get(url).text
        return response
    except r.exceptions.RequestException as error:
        file_proc.error_log(error)
        print(error)
        return None


def processing(data):
    xml = ET.fromstring(data)
    last_entry = xml.find('{http://www.w3.org/2005/Atom}entry')
    video_id = last_entry.find('{http://www.youtube.com/xml/schemas/2015}videoId').text
    title = last_entry.find('{http://www.w3.org/2005/Atom}title').text
    link = last_entry.find('{http://www.w3.org/2005/Atom}link').attrib['href']
    return video_id, title, link


def to_send(title, link, index):
    channel = 'основном' if index == 0 else 'втором'
    message = f'Новое видео на {channel} канале:\n\n"{title}"\n{link}'
    vk_.send(message=message, category='youtube')
    print(message)


def start_yt():
    # n = 1
    last_videos_ids = [[None], [None]]
    channels = file_proc.read_config('youtube', 'channels', list_=True)

    while True:
        for index in range(len(channels)):
            response = req(url=f'https://www.youtube.com/feeds/videos.xml?channel_id={channels[index]}')
            # print(f'Запрос {n} выполнен ({channels[index]})')

            if response is None:
                sleep(15)
                continue

            # TODO: Получить все в случае, если новое видео. Иначе только id. Некритично
            video_id, title, link = processing(response)

            # Это нужно, чтобы при запуске бота он не отправлял последнее видео
            if last_videos_ids[index][0] is None:
                last_videos_ids[index][0] = video_id
                continue

            if video_id not in last_videos_ids[index]:
                to_send(title, link, index)
                last_videos_ids[index].append(video_id)

        # n += 1
        # print('\n')
        sleep(2)
