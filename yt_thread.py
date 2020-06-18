import xml.etree.ElementTree as ET
from time import sleep, time, ctime

import requests as r

import file_proc
import vk_


def req(url):
    try:
        response = r.get(url).text
        return response
    except r.exceptions.RequestException as exception:
        file_proc.error_log(str(exception) + '| YT(req)')
        print(exception, ctime(time()), '| YT(req)')
        return None


def processing(data):
    result = list()

    try:
        xml = ET.fromstring(data)
    except Exception as exception:
        file_proc.error_log(str(exception) + '| YT(xml)')
        print(exception, ctime(time()), '| YT(req)')
        return None

    for entry in xml.findall('{http://www.w3.org/2005/Atom}entry'):
        video_id = entry.find('{http://www.youtube.com/xml/schemas/2015}videoId').text
        title = entry.find('{http://www.w3.org/2005/Atom}title').text
        link = entry.find('{http://www.w3.org/2005/Atom}link_TEST').attrib['href']
        result.append([video_id, title, link])
    return result


def to_send(title, link, index):
    channel = 'основном' if index == 0 else 'втором'
    message = f'Новое видео на {channel} канале:\n\n"{title}"\n{link}'
    vk_.send(message=message, category='youtube')
    print(f'New youtube video send successfully! {link}')


def start_yt():
    channels = file_proc.read_config('youtube', 'channels', list_=True)
    last_videos_ids = dict()

    # Первоначальное заполнение video_id
    for index, channel in enumerate(channels):
        # Сколько каналов в конфиге, столько и ключей словаря. Затем к ключу с id канала добавим id каждого видео
        last_videos_ids.update({channel: list()})
        response = req(url=f'https://www.youtube.com/feeds/videos.xml?channel_id={channel}')
        items = processing(response)
        for item in items:
            last_videos_ids[channel].append(item[0])

        last_videos_ids[channel].reverse()  # Разворачиваем список, чтобы последние видео были в конце

    while True:
        for channel_index, channel in enumerate(channels):
            response = req(url=f'https://www.youtube.com/feeds/videos.xml?channel_id={channel}')

            if response is None:
                sleep(15)
                continue

            items = processing(response)

            if items is None:
                sleep(15)
                continue

            for item in items:
                if item[0] not in last_videos_ids[channel]:
                    to_send(title=item[1], link=item[2], index=channel_index)
                    last_videos_ids[channel].pop(0)
                    last_videos_ids[channel].append(item[0])

            sleep(2)
