
import telepot
import json
import requests
import time
from imdb import IMDb
from settings import TELEGRAM_BOT_TOKEN


MOST_KNOWN_MOVIE = 0
BOT_URL = "https://api.telegram.org/bot{0}/".format(TELEGRAM_BOT_TOKEN)
TELEGRAMBOT = telepot.Bot(TELEGRAM_BOT_TOKEN)


def display_help():
    return "Enter a name of a movie or TV serie and you will get it's stats from the known website IMDB!"

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    payload = json.loads(content)
    return payload


def get_updates(offset = None):
    url = BOT_URL + "getUpdates?timeout=100"

    if offset:
        url += "&offset={}".format(offset)
    
    js = get_json_from_url(url)
    return js

def get_max_update_id(updates):
    return max(map(lambda update_message: int(update_message["update_id"]), updates["result"]))

def get_last_chat_id(updates):
    last_update = len(updates["result"]) - 1
    return updates["result"][last_update]["message"]["chat"]["id"]

def get_last_text(updates):
    last_update = len(updates["result"]) - 1
    return updates["result"][last_update]["message"]["text"]
    return (text_last_message, chat_id)


def send_response(text, chat_id):
    if text:
        if text == "help":
            TELEGRAMBOT.sendMessage(chat_id, display_help(), parse_mode='Markdown')
        else:
            TELEGRAMBOT.sendMessage(chat_id, get_movie_or_serie_stats(text), parse_mode='Markdown')
    else:
        TELEGRAMBOT.sendMessage(chat_id, 'I do not understand you, Sir!', parse_mode='Markdown')


def get_movie_or_serie_stats(movie_name):
    moviesDB = IMDb()
    movieID = moviesDB.search_movie(movie_name)[MOST_KNOWN_MOVIE].getID()
    movie = moviesDB.get_movie(movieID)
    title = movie['title']
    year = movie['year']
    rating = movie['rating']

    if title.lower() == movie_name.lower():
        return f'the movie/serie {title} released in {year} and has rating of {rating}'
    return f'can not find the exact movie or serie with this name. The closest one is: {title} that released in {year} and has rating of {rating}'

def respond_all_updates(updates):
    for update in updates["result"]:
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]
        
        try: 
            send_response(text, chat_id)
        
        except Exception as exp:
            TELEGRAMBOT.sendMessage(chat_id, 'Sorry, something went wrong please try again', parse_mode='Markdown')
            print(exp)

def main():
    last_update_id = None

    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_max_update_id(updates) + 1
            respond_all_updates(updates)
        time.sleep(0.5)


if __name__ == "__main__":
    main()