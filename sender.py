import json
import json 
import scrapetube
from requests import get
from bs4 import BeautifulSoup
import builtins
import telebot


with open('data.json', 'r') as f:
    data = json.load(f)

with open("config.json", "r") as f:
    config = json.load(f)


bot = telebot.TeleBot(token=config["bot_token"])


try:
    data["subs"]
except KeyError:
    data["subs"] = {}
    
for channel in data["subs"]:
    print(channel)
    # check if the channel have new video/live stream
    # if yes then send notification to all subscribers
    
    # make a file videos.txt if not exist
    if not data["subs"][channel]:
        # should not care if there is no one to see the notification
        print("no subs")
        continue
    try:
        open("videos.txt", "r").close() 
    except FileNotFoundError:
        open("videos.txt", "w").close()
    with open("videos.txt", "r") as f:
        known_videos = f.read().split("\n")
    channel_link = f"https://youtube.com/channel/{channel}"
    html_data = get(channel_link).text
    soup = BeautifulSoup(html_data, 'html.parser')
    channel_name = soup.find("meta", property="og:title")["content"]
    channel_image = soup.find("meta", property="og:image")["content"]
    types = ['videos', 'shorts', 'streams']
    for type in types:
        print("doing type", type)
        videos = scrapetube.get_channel(channel, content_type=type, sort_by="newest")
        count = 0
        for video in videos:
            print(video["videoId"])
            count += 1
            if count > 1:
                break
            with open("videos.json", "w") as f:
                json.dump(video, f, indent=4)
            if type == "videos":
                ago = video["publishedTimeText"]["simpleText"].lower()
                if "day" in ago or "week" in ago or "month" in ago or "year" in ago:
                    print("not new")
                    print(ago)
                    continue
            video_id = video["videoId"]
            if video_id in known_videos:
                print("known video")
                continue
            # write video_id to videos.txt
            with open("videos.txt", "a") as f:
                f.write(video_id+"\n")
            sent_to_count = 0
            # send notification to all subscribers
            for sub in data["subs"][channel]:
                print(sub)
                vtitle = video["headline"]["simpleText"] if type == "shorts" else video["title"]["runs"][0]["text"]
                title = f"{channel_name} has posted a new video!" if type in ["videos", "shorts"] else f"{channel_name} is live now!"
                try:
                    bot.send_message(sub, f"{title}\n{vtitle}\nhttps://youtube.com/watch?v={video_id}")
                except Exception as e:
                    print(e)
                    continue
                sent_to_count += 1