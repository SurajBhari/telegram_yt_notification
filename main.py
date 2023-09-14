import json, os

from flask import request, Response, render_template, jsonify, Flask, redirect
from requests import get
from bs4 import BeautifulSoup
import telebot
import threading

with open("config.json", "r") as f:
    config = json.load(f)
app = Flask(__name__)
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
bot = telebot.TeleBot(token=config["bot_token"])


@app.route('/')
def index():
    return "hello world"


@app.route("/c/<channel>/")
@app.route("/channel/<channel>/")
def channel(channel):
    data = {}
    channel_link = f"https://youtube.com/channel/{channel}"
    html_data = get(channel_link).text
    soup = BeautifulSoup(html_data, 'html.parser')
    channel_image = soup.find("meta", property="og:image")["content"]
    channel_name = soup.find("meta", property="og:title")["content"]
    data["channel_link"] = channel_link
    data["channelimage"] = channel_image
    # bgimage is channel banner
    data["bgimage"] = soup.find
    data["channelname"] = channel_name
    data["channel_id"] = channel
    data["bot_name"] = config["bot_name"]
    return render_template("index.html", data=data)

@bot.message_handler(commands=['start'])
def start(message):
    # give info about context
    print(message.text)
    user_id = message.chat.id
    try:
        command, *channel_id = message.text.split()[1].split("_")
    except (ValueError, IndexError):
        bot.reply_to(message, "Wrong command")
        return
    channel_id = "_".join(channel_id)
    if "unsubscribe" in command:
        bot.reply_to(message, unsubscribe(user_id, channel_id))
        return
    elif "subscribe" in command:
        bot.reply_to(message, subscribe(user_id, channel_id))
        return
    else:
        bot.reply_to(message, "Wrong command")
        return
        

def subscribe(user, channel_id):
    url_channel = f"https://youtube.com/channel/{channel_id}"
    try:
        html_data = get(url_channel).text
        soup = BeautifulSoup(html_data, 'html.parser')
        channel_name = soup.find("meta", property="og:title")["content"]
    except:
        return "Channel not found"
    with open("data.json", "r") as f:
        data = json.load(f)
    if "subs" not in data:
        data["subs"] = {}
    try:
        if user in data["subs"][channel_id]:
            return "Already subscribed"
        data["subs"][channel_id].append(user)
    except KeyError:
        data["subs"][channel_id] = [user]
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)
    return f"Subscribed to {channel_name}"

def unsubscribe(user, channel_id):
    url_channel = f"https://youtube.com/channel/{channel_id}"
    try:
        html_data = get(url_channel).text
        soup = BeautifulSoup(html_data, 'html.parser')
        channel_name = soup.find("meta", property="og:title")["content"]
    except:
        return "Channel not found"
    with open("data.json", "r") as f:
        data = json.load(f)
    if "subs" not in data:
        data["subs"] = {}
    try:
        if user not in data["subs"][channel_id]:
            return "Not subscribed"
        status = data["subs"][channel_id].remove(user)
        print(status)
    except KeyError:
        data["subs"][channel_id] = []
    print(data)
    with open("data.json", "w") as f:
        json.dump(data, f, indent=4)
    return f"UnSubscribed to {channel_name}"



if __name__ == "__main__":
    bot_polling_thread = threading.Thread(target=bot.polling)
    bot_polling_thread.start()

    # Start the Flask app
    app.run(host='0.0.0.0', port=10000)
