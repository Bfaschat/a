
#!/usr/bin/env python
# coding: utf-8
from __future__ import print_function
from bs4 import BeautifulSoup
import progressbar
import requests
import sys
import re
import json
import os
import html
import time
import datetime
from datetime import datetime
from urllib.parse import urlparse, quote_plus
from os.path import splitext
from urllib.request import urlretrieve
from urllib.request import urlopen
from shutil import copyfileobj
from pyaxmlparser import APK
from shutil import copyfile
from tempfile import NamedTemporaryFile
import threading
import pprint
import traceback
import urllib.request
import amanobot
import amanobot.namedtuple
from tqdm import tqdm
from amanobot.namedtuple import InlineKeyboardMarkup
import warnings
from random import randint
try:
    import urllib.request
    python3 = True
except ImportError:
    import urllib2
    python3 = False
import config
import keyboard

bot = config.bot
version = config.version
bot_username = config.bot_username
### XXX: hack to skip some stupid beautifulsoup warnings that I'll fix when refactoring
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TMP_DOWNLOAD_DIRECTORY", "./downloads/")
def progress(current, total):
    print("Downloaded {} of {}\nCompleted {}".format(current, total, (current / total) * 100))
def make_progress_bar():
    return progressbar.ProgressBar(
        redirect_stdout=True,
        redirect_stderr=True,
        widgets=[
            progressbar.Percentage(),
            progressbar.Bar(),
            ' (',
            progressbar.AdaptiveTransferSpeed(),
            ' ',
            progressbar.ETA(),
            ') ',
        ])
dlk = keyboard.restart_dl

def shuffle(word):
    wordlen = len(word)
    word = list(word)
    for i in range(0,wordlen-1):
        pos = randint(i+1,wordlen-1)
        word[i], word[pos] = word[pos], word[i]
    word = "".join(word)
    return word

def pretty_size(size):
    units = ['B', 'KB', 'MB', 'GB']
    unit = 0
    while size >= 1024:
        size /= 1024
        unit += 1
    return '%0.2f %s' % (size, units[unit])
def dados(msg):
    if msg.get('text'):
        teclado = keyboard.restart_dl
        if msg['text'].startswith('!dl'):
            input_str = msg['text'][3:]
            if input_str == '':
                bot.sendMessage(msg['chat']['id'], '*Use:* `/dl or !dl <url/link>`',
                                parse_mode='Markdown',
                                reply_to_message_id=msg['message_id'])
            else:
                app_name = input_str.split('/')[-1]
                sent = bot.sendMessage(msg['chat']['id'], "🔁 getting download link for {}".format(app_name), 'Markdown', reply_to_message_id=msg['message_id'])['message_id']
                if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
                    os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
                site = "https://apkpure.com"
                url = "https://apkpure.com/search?q=%s" %(app_name)
                html = requests.get(url).text
                parse = BeautifulSoup(html, features="lxml")
                for i in parse.find("p"):
                    a_url = i["href"]
                    app_url = site + a_url + "/download?from=details"
                    html2 = requests.get(app_url).text
                    parse2 = BeautifulSoup(html2, features="lxml")
                    links = []
                    for link in parse2.find_all('a', {'id': 'download_link'}):
                        links.append(link.get('href'))
                        downloadlink = link.get('href')
                        word = "123456789abcdefgh-_"
                        servers = shuffle(word)
                        bot.editMessageText((msg['chat']['id'], sent), "⬇️ downloading from [{}.apkpure.com]({}) in progress...".format(servers, downloadlink), 'Markdown', disable_web_page_preview=True)
                        #bot.deleteMessage(chat_id, sent)
                        required_file_name = TEMP_DOWNLOAD_DIRECTORY + "" + app_name + ".apk"
                        start = datetime.now()
                        chunk_size = 1024
                        r = requests.get(downloadlink, stream = True) 
                        with open(required_file_name,"wb") as apk:
                            for chunk in r.iter_content(chunk_size=chunk_size):
                                total_length = r.headers.get('content-length')
                                dl = 0
                                total_length = int(total_length)
                                if chunk:
                                    dl += len(chunk)
                                    done = int(100 * dl / total_length)
                                    apk.write(chunk)
                                    apk.flush()
                                    upload_progress_string = "... [%s of %s]" % (str(dl), str(pretty_size(total_length)))
                            bot.editMessageText((msg['chat']['id'], sent), "⬆️ Uploading *{}* to Telegram \n\n {}".format(app_name, upload_progress_string), 'Markdown')
                            time.sleep(5)
                            starts = datetime.now()
                            if total_length < 52428800:
                                bot.sendChatAction(msg['chat']['id'], 'upload_document')
                                tr = bot.sendDocument(msg['chat']['id'], open(required_file_name, 'rb'), caption="@" + bot_username, parse_mode='Markdown')
                                time.sleep(0.5)
                                ends = datetime.now()
                                mss = (ends - starts).seconds
                                os.remove(required_file_name)
                                bot.deleteMessage((msg['chat']['id'],sent))
                            else:
                                bot.editMessageText((msg['chat']['id'], sent), "⚠️ *{}* is more than the 50MB limit. Unfortunately, The current download job has ended unexpectedly.\n Try downloading something smaller than this".format(app_name), 'Markdown')
                                os.remove(required_file_name)
                                time.sleep(5)
                                bot.deleteMessage((msg['chat']['id'],sent))
                                return True

        

