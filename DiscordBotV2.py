import discord
import logging
import credentials
import aiohttp
import asyncio
from random import randint
from collections import deque
from discord import opus


logging.basicConfig(level=logging.INFO) #set debugging config
client = discord.Client() #declare client

dogSubreddits = ["dogpictures", "puppies", "dogsdrivingcars", "dogswitheyebrows"]
shibaSubreddits = ["doge", "SuperShibe"]

acceptableImageFormats = [".png",".jpg",".jpeg",".gif",".gifv",".webm",".mp4","imgur.com"]

dogHistory = deque() #limited to 63 entries
shibaHistory = deque() #limited to 127 entries


def char_lang(char): #returns if the char is rtl, ltr, or not direction based
    charcode = ord(char)
    if ord('א') <= charcode <= ord('ת') or ord('؀') <= charcode <= ord('ۿ'):
        return "rtl"
    if ord('a') <= charcode <= ord('z') or ord('A') <= charcode <= ord('Z'):
        return "ltr"
    return ""

#commands:

async def cat(msg): # $cat
    await client.send_typing(msg.channel)
    try:
        with aiohttp.ClientSession() as session:
            async with session.get('http://random.cat/meow') as response:
                request = await response.json()
        img = request['file']
        await client.send_message(msg.channel, img)
    except:
        #failed to get cats
        await client.send_message(msg.channel, ":crying_cat_face:")

async def dog(msg): # $dog
    await client.send_typing(msg.channel)
    chosenSubreddit = dogSubreddits[randint(0,len(dogSubreddits) - 1)]

    with aiohttp.ClientSession() as session:
        async with session.get("https://www.reddit.com/r/" + chosenSubreddit + "/new.json?limit=100") as response:
            request = await response.json()

    attempts = 1
    while attempts < 5:
        if 'error' in request:
            print("failed request {}".format(attempts))
            await asyncio.sleep(2)
            with aiohttp.ClientSession() as session:
                async with session.get("https://www.reddit.com/r/" + chosenSubreddit + "/new.json?limit=100") as response:
                    request = await response.json()
            attempts += 1
        else:
            index = 0

            for index, val in enumerate(request['data']['children']):
                if 'url' in val['data']:
                    url = val['data']['url']
                    urlLower = url.lower()
                    accepted = False
                    for j, v, in enumerate(acceptableImageFormats): #check if it's an acceptable image
                        if v in urlLower:
                            accepted = True
                    if accepted:
                        if url not in dogHistory:
                            dogHistory.append(url)  #add the url to the history, so it won't be posted again
                            if len(dogHistory) > 63: #limit size
                                dogHistory.popleft() #remove the oldest

                            break #done with this loop, can send image
            await client.send_message(msg.channel, dogHistory[len(dogHistory) - 1]) #send the last image
            return
    await client.send_message(msg.channel, ":poodle: _{}! ({})_".format(str(request['message']), str(request['error'])))
        

async def shiba(msg): # $doge
    await client.send_typing(msg.channel)
    chosenSubreddit = shibaSubreddits[randint(0,len(shibaSubreddits) - 1)]
    with aiohttp.ClientSession() as session:
        async with session.get("https://www.reddit.com/r/" + chosenSubreddit + "/new.json?limit=100") as response:
            request = await response.json()
    attempts = 1

    while attempts < 5:
        if 'error' in request:
             print("failed request {}".format(attempts))
             await asyncio.sleep(2)
             with aiohttp.ClientSession() as session:
                async with session.get("https://www.reddit.com/r/" + chosenSubreddit + "/new.json?limit=100") as response:
                    request = await response.json()
             attempts += 1
        else:
            index = 0
        
            for index, val in enumerate(request['data']['children']):
                if 'url' in val['data']:
                    url = val['data']['url']
                    urlLower = url.lower()
                    accepted = False
                    for j, v, in enumerate(acceptableImageFormats): #check if it's an acceptable image
                        if v in urlLower:
                            accepted = True

                    if accepted:
                        if url not in shibaHistory:
                            shibaHistory.append(url)  #add the url to the history, so it won't be posted again

                            if len(shibaHistory) > 127: #limit size
                                shibaHistory.popleft() #remove the oldest

                            break #done with this loop, can send image
            await client.send_message(msg.channel, shibaHistory[len(shibaHistory) - 1]) #send the last image
            return
    await client.send_message(msg.channel, ":feet: _{}! ({})_".format(str(request['message']), str(request['error'])))

async def square(msg): # messages that end with ^^2
    process = msg.content[:-3].upper()  #remove the ending
    if len(process) > 0: #make sure there is something to square
        output = '```\n'
        add = ""
        withSpace = ""
        for i in range(len(process)):
            add = process[i:] + process[:i] #build a line
            withSpace = ""
            for j, txt in enumerate(add): #add spaces between characters
                withSpace += txt + " "
            output += withSpace + "\n" #add line to output
        output += "```" #close output
        if len(output) > 2000:
            output = ":scissors: *Message is Too Long!* :scissors:"
        await client.send_message(msg.channel, output)
        
async def manticore(msg): # $manticore
    await client.send_message(msg.author, "מנטיקור")
    await client.send_message(msg.author, "מנטיקור")
    await client.send_message(msg.author, "מנטיקור")
    await client.send_message(msg.author, "!!!!!!!!!!!!!!!")
    await asyncio.sleep(1.5)
    await client.send_file(msg.author, 'images/angry-manti.png')
    await asyncio.sleep(0.5)
    await client.send_message(msg.author, "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    await client.send_file(msg.author, 'images/super-angry-manti.png')
    await asyncio.sleep(1.5)
    await client.send_message(msg.author, "שמח?!?!?!?!?!?!?!?")

async def meow(msg): # $meow
    load_opus_lib()
    await client.send_message(msg.channel, opus.is_loaded())
    voice = await client.join_voice_channel(get_user_voice(msg))
    player = voice.create_ffmpeg_player('sounds/meow.mp3')
    player.start()

async def rtl(msg): # $, left to right text -> right to left text
    str = msg.content[1:] # the sentence to process
    if len(str) > 0: #not empty
        temp = "" #storage of temporary part of sentence
        parts = [] #the parts of the sentence (seperated by language)
        neutralChars = "" #characters with no specific direction, should check what is the next character after them and then get a direction
        endChars = "" #characters that should be kept and added at the end of the string
        chartype = "rtl"
        prevchartype = "rtl"
        for i, char in enumerate(str):
            chartype = char_lang(char)
            if chartype == "":
                neutralChars += char
            else:
                if chartype == prevchartype: #same language, or language-neutral
                    if len(neutralChars) > 0: #add neutral chars from previous part
                        temp += neutralChars
                        neutralChars = ""
                    temp += char
                else: #different language
                    if len(endChars) > 0: #add end chars from previous
                        temp += endChars
                        endChars = ""
                    endChars = neutralChars
                    neutralChars = ""
                    parts.append(temp) #cut the sentence
                    temp = ""
                    temp += char #new language part
                    prevchartype = chartype

        temp = neutralChars + temp + endChars
        parts.append(temp) #append last sentence
        parts.reverse() #change direction
        output = "".join(parts) #join it all together

        await client.send_message(msg.channel, "__***{}:***__\n{}".format(msg.author.display_name, output))


#OPUS_LIBS = ['libopus-0.x86.dll', 'libopus-0.x64.dll', 'libopus-0.dll', 'libopus.so.0', 'libopus.0.dylib']

#def load_opus_lib(opus_libs=OPUS_LIBS):
#    if opus.is_loaded():
#        return True

#    for opus_lib in opus_libs:
#        try:
#            opus.load_opus(opus_lib)
#            return
#        except OSError:
#            pass

#    raise RuntimeError('Could not load an opus lib. Tried %s' % (', '.join(opus_libs)))

#def get_user_voice(msg): #gets the voice channel that the user is in.
#    server = msg.server
#    if server:
#        for channel in server.channels:
#            for usr in channel.voice_members:
#                if usr == msg.author:
#                    return channel
#    return


@client.event
async def on_message(msg):
    #don't process the bot's own messages
    if msg.author == client.user:
        return

    if msg.content == '$cat':
        await cat(msg)
        return
    if msg.content == '$dog':
        await dog(msg)
        return
    if msg.content == '$doge':
        await shiba(msg)
        return
    if msg.content.endswith('^^2'):
        await square(msg)
        return
    if msg.content == "$manticore":
        await manticore(msg)
        return

    if msg.content.startswith("$"):
        await rtl(msg)
        return

@client.event
async def on_ready():
    print('------')
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(credentials.TOKEN) #start the bot