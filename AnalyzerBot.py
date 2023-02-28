#AnalyzerBot is created by Michael Speer
#This is super rough, about half is leftover code from one of the recommended framework for Telegram
#The idea for this project is to host this bot on a RaspberryPi and analyze the data
#The end goal is a predictive model that can guess whether or not we will have a "high traffic day"
#A machine learning mechanism might be put in place later in my education but this is done in my time off so that might not materialize.

from time import sleep
from origamibot import OrigamiBot as Bot
from origamibot.listener import Listener

import csv
import time
import json

approved_array = [1488653414]
filename = 'listening.csv'
filename2 = 'approved.csv'
fields = ['message_id', 'date', 'time', 'chat.id', 'chat.type', 'user.id', 'text']


class BotsCommands:
    def __init__(self, bot: Bot):  # Can initialize however you like
        self.bot = bot

    def start(self, message):   # /start command
        self.bot.send_message(
            message.chat.id,
            'Hello user!\nThis is an example bot.')

    def add(self, message, a: float, b: float):  # /add [a: float] [b: float]
        self.bot.send_message(
            message.chat.id,
            str(a + b)
            )

    def _not_a_command(self):   # This method not considered a command
        print('I am not a command')


class MessageListener(Listener):  # Event listener must inherit Listener
    def __init__(self, bot):
        self.bot = bot
        self.m_count = 0

    def my_echo(self, message):
        value = message.text.replace('/echo ','')
        self.bot.send_message(message.chat.id, value)

    def on_message(self, message):   # called on every message
        self.m_count += 1
        print(message)
        with open('raw.tsv', 'a+') as raw:
            try:
                raw.writelines(str(str(message).encode(encoding='utf8', errors= 'xmlcharrefreplace'))+'\n')
            except Exception as e: 
                raw.writelines(str(e)+'\n')


        if message.text != None:
            if message.chat.id in approved_array:
                cleanstring = message.text.replace(',','|')
                writ = [message.message_id,message.date,time.time(),(message.chat.id),(message.chat.type),message.from_user.id, cleanstring]
                #print(writ)
                with open(filename, 'a') as csvfile:
                    csvwriter = csv.writer(csvfile)
                    try:
                        csvwriter.writerow(writ)
                    except:
                        csvwriter.writerow([message.message_id,message.date,time.time(),(message.chat.id),(message.chat.type),message.from_user.id, cleanstring.encode(encoding='utf8', errors= 'xmlcharrefreplace')])
                #print("success")

##OptIn and OptOut aren't working exactly right but I don't have time to fix it currently.
            if '/optin' in message.text.lower():
                if message.chat.id in approved_array:
                    self.bot.send_message(message.chat.id, 'You have already opted into having mesasges recorded. To opt out, try /OptOut')
                else:
                    approved_array.append(message.chat.id)
                    self.bot.send_message(message.chat.id, 'You have successfully opted in. This bot will now begin recording your messages and pertinent metadata. This data will be stored securely and will not be released for any reason.')
                    with open(filename2, 'a+') as csvarray:
                        arraywriter = csv.writer(csvarray)
                        arraywriter.writerow(approved_array)

            if '/optout' in message.text.lower():
                if message.chat.id in approved_array:
                    approved_array.remove(message.chat.id)
                    self.bot.send_message(message.chat.id, 'You have successfully opted out, this bot will no longer record messages until someone opts in. Thank you.')
                    with open(filename2, 'w') as csvarray:
                        arraywriter = csv.writer(csvarray)
                        arraywriter.writerow(approved_array)
                else:
                    self.bot.send_message(message.chat.id, 'This chat was not found as having opted in. This bot is not recording your messages.')

            if '/echo' in message.text:
                self.my_echo(message)
        elif message.animation != None:
            with open(filename, 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([message.message_id,message.date,time.time(),(message.chat.id),(message.chat.type),message.from_user.id, "Message Type: Animation"])
        elif message.photo != None:
             with open(filename, 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([message.message_id,message.date,time.time(),(message.chat.id),(message.chat.type),message.from_user.id, "Message Type: Photo"])
        elif message.sticker != None:
            with open(filename, 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([message.message_id,message.date,time.time(),(message.chat.id),(message.chat.type),message.from_user.id, "Message Type: Sticker"])
        else:
            with open(filename, 'a') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow([message.message_id,message.date,time.time(),(message.chat.id),(message.chat.type),message.from_user.id, "Message Type: Unknown"])

    def on_command_failure(self, message, err=None):  # When command fails
        if err is None:
            self.bot.send_message(message.chat.id,
                                  'Command failed to bind arguments!')
        else:
            self.bot.send_message(message.chat.id,
                                  'Error in command:\n{err}')


if __name__ == '__main__':
    f = open('config.json')
    config = json.load(f)
    token = config['keys']['TelegramKey']
    bot = Bot(token)   # Create instance of OrigamiBot class


    # Add an event listener
    bot.add_listener(MessageListener(bot))

    # Add a command holder
    bot.add_commands(BotsCommands(bot))

    # We can add as many command holders
    # and event listeners as we like

    bot.start()   # start bot's threads
    while True:
        sleep(1)
        # Can also do some useful work i main thread
        # Like autoposting to channels for example
