from twitch import TwitchClient

import file_proc
from file_proc import read_config


def tw_auth():
    twitch_client = TwitchClient(client_id=read_config('twitch', 'client_id'))
    return twitch_client


def twitch(game):
    streamers = read_config('twitch', 'streamers', list_=True)
    twitch_client = tw_auth()
    streamers = twitch_client.users.translate_usernames_to_ids(streamers)
    for streamer in streamers:
        streamer_live = twitch_client.streams.get_stream_by_user(channel_id=streamer['id'])
        if streamer_live is not None and streamer_live['game'] == game:
            streamer_name = streamer_live['channel']['display_name']
            file_proc.wycc_log(f'with_twitch {streamer_name} {game}')
            return streamer_name
