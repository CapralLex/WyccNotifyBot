import configparser
import json
from time import strftime, localtime, time


def read_users(category=None, raw=False, separated=False):
    with open('users.json', 'r', encoding='UTF-8') as file:
        data = json.load(file)

    if separated and category:
        users = list()
        full_list = data[category]
        # full_list = ['test_id'+str(_) for _ in range(1, 1+1)]

        for index in range(len(full_list)//100+1):
            users.append(full_list[index*100:index*100+100])

    elif type(category) is list:  # Если передали список категорий
        users = []
        for key in category:  # Для каждого элемента категории
            for _ in data[key]:  # Для каждого юзера категории
                if _ not in users:  # Если еще не записали
                    users.append(_)

    elif raw:  # Если нужно отдать только сырые данные
        return data

    else:
        users = data[category]

    return users


def write_users(user, category):
    checker = False  # Чекер нужен для проверки, вносили ли мы изменения в файл или нет
    with open('users.json', 'r', encoding='UTF-8') as file:
        data = json.load(file)

    if category == 'all':
        for key in data.keys():
            if user not in data[key]:
                data[key].append(user)
                checker = True
            else:
                print(f'WAR: Category already contains a user {user} (all)')

    else:
        if user not in data[category]:
            data[category].append(user)
            checker = True
        else:
            print(f'WAR: Category already contains a user {user} (ones)')

    if checker:  # Если мы вносили изменение в файл - записываем и возвращаем True
        with open('users.json', 'w', encoding='UTF-8') as file:
            json.dump(data, file, indent=1)
        return True
    else:
        return False


def delete_users(user, category):
    checker = False  # Чекер нужен для проверки, вносили ли мы изменения в файл или нет
    with open('users.json', 'r', encoding='UTF-8') as file:
        data = json.load(file)

    if category == 'all':
        for key in data.keys():
            if user in data[key]:
                data[key].remove(user)
                checker = True
            else:
                print(f'WAR: Category does not contain user {user} (all)')

    else:
        if user in data[category]:
            data[category].remove(user)
            checker = True
        else:
            print(f'WAR: Category does not contain user {user} (ones)')

    if checker:  # Если мы вносили изменение в файл - записываем и возвращаем True
        with open('users.json', 'w', encoding='UTF-8') as file:
            json.dump(data, file, indent=1)
        return True
    else:
        return False


def wycc_log(action):
    with open('wycc.log', 'a', encoding='UTF-8') as logfile:
        action_time = strftime('%x %X', localtime(time()))
        logfile.write(f'{action} | {action_time}\n')


def error_log(exception):
    with open('error.log', 'a', encoding='UTF-8') as logfile:
        action_time = strftime('%x %X', localtime(time()))
        logfile.write(f'{exception} | {action_time}\n')


def read_config(section, key, list_=False):
    config = configparser.ConfigParser()
    config.read('config.ini')
    result = config.get(section, key)
    if list_:
        result = result.split(', ')
    return result


def write_config(section, key, value):
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.set(section, key, value)
    with open('config.ini', 'w') as config_file:
        config.write(config_file)
