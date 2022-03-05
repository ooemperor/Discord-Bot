# -*- coding: utf-8 -*-
"""
Created on Sat Mar  5 21:45:48 2022

@author: mikai
"""

import nest_asyncio
nest_asyncio.apply()
import discord
from discord.ext import commands
from youtube_dl import YoutubeDL
from subprocess import call
from datetime import datetime
import random
import sys
import json
import requests
from gpiozero import CPUTemperature #only working on raspberry pi
import asyncio
import time as t
import queue

#------------------------------------------------------------------------------------------------
"""
global variables and operations at the start of the script
"""
#general settings for the Bot. 
description = '''BB-8''' #change if you have a different name
intents = discord.Intents.default() #all avaible Intents need to be set in discord developer portal
bot = commands.Bot(command_prefix='!', description=description, intents=intents)

#Reading and setting the API Key for Discord
tk = open('./API Keys/Bot Token.txt', 'r')
TOKEN = tk.read()
tk.close()

#Reading the Tenor API Key and setting the need global variables
tenor_api = open('./API Keys/Tenor API Key.txt', 'r')
TENOR_API_KEY = tenor_api.read()
tenor_api.close()
Limit_Tenor = 1

Started = datetime.now() #timestamp when the Bot was started. uesed in stats command

server_channels = {} # Server channel cache
sound_que = queue.Queue() #Queue for the soundlist

#---------------------------------------------------------------------------------------------------
"""
normal functions that are used multipletimes
no async functions in this part
"""
def timestamp():
    #Creates the Timestamp
    current_time = t.strftime("%d/%m/%y %H:%M:%S", t.localtime())
    return(current_time)

def server_logging(message, server):
    #Logs a message with timestamp on the server. 
    name = './Logs/' + str(server) + '/Server Logging ' + t.strftime("%Y.%m.%d", t.localtime()) + '.txt'
    f = open(name, 'a')
    f.write('\n' + timestamp() + '  ' + message)
    f.close()
    
def generate_log_message(author, cmd):
    #generates a string that can then be logged
    message = author + ' used the command: ' + cmd
    return message
    
def search_tenor(term):
    """Searches a Meme on Tenor.com for a given search term"""
    r = requests.get("https://g.tenor.com/v1/search?q=%s&key=%s&limit=%s" % (term, TENOR_API_KEY, Limit_Tenor))
    if r.status_code == 200:
        top_gif = json.loads(r.content)
        if 'results' in top_gif:
            return((top_gif['results'][0])['itemurl']) #do not change the path, specified based on json
        else:
            return('https://tenor.com/view/somethings-not-right-there-regina-mom-theres-something-wrong-there-somethings-wrong-gif-19844156')  
    else:
        return('https://tenor.com/view/somethings-not-right-there-regina-mom-theres-something-wrong-there-somethings-wrong-gif-19844156')

def replace(input):
    output = input.replace('#', '%23')
    return(output)

 
def excpetion_url_test(url):
    #checking if a url is valid or not
    try:
        response = requests.get(url)
        return(0)
    except:
        return(1)
    
#-------------------------------------------------------------------------------------------------------
"""
async functions for the bot
"""
        
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(str(len(bot.guilds)) + " Actice Servers")
    await bot.change_presence(activity=discord.Game(name='Star Wars'))
    
@bot.command()
async def up(ctx):
    """Checks if the Bot is running"""
    server_logging(generate_log_message(str(ctx.author), 'up'), ctx.guild)
    await ctx.send('awaiting further instructions. Order 66 cannot be executed')

"""
@bot.command()
async def r2d2(ctx):
    Returns a surprise
    if ctx.author.voice != None:
        channel = str(ctx.author.voice.channel)
        voiceChannel = discord.utils.get(ctx.guild.voice_channels, name = channel)
        await voiceChannel.connect()
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        file = "./Sounds/r2d2.mp3"
        voice.play(discord.FFmpegPCMAudio(file))
        await ctx.send('https://tenor.com/view/happy-rocking-r2d2-star-wars-artoo-gif-15352285')
        await asyncio.sleep(2)
        await voice.disconnect()
    else:
        await ctx.send('https://tenor.com/view/happy-rocking-r2d2-star-wars-artoo-gif-15352285')
   """
   
@bot.command()
async def ping(ctx):
    """Returns the latency of the bot"""
    server_logging(generate_log_message(str(ctx.author), 'ping'), ctx.guild)
    ms = (datetime.utcnow() - ctx.message.created_at).microseconds / 1000
    before = datetime.now()
    await ctx.send('Latency: ' + str(int(ms)) + 'ms')
    ms2 = (datetime.now() - before).microseconds / 1000
    await ctx.send('Message delay: '+ str(int(ms2)) + 'ms')

@bot.command()
async def sudo_poweroff(ctx):
    """Shutdown Command of the Bot. Only working for admin"""
    server_logging(generate_log_message(str(ctx.author), 'sudo_poweroff'), ctx.guild)
    if ctx.message.author.guild_permissions.administrator:
        await ctx.send('Powering down')
        await call('sudo nohup shutdown -h now', shell=True)
        sys.exit()
    else:
        await ctx.send('Nice Try :joy:')

        
@bot.command()
async def rand(ctx, number):
    """ generates a random number between 1 and you given number"""
    server_logging(generate_log_message(str(ctx.author), 'rand ' + str(number)), ctx.guild)
    r = random.randint(1, int(number))
    await ctx.send(r)
    
@bot.command()
async def meme(ctx, *, term):
    server_logging(generate_log_message(str(ctx.author), 'meme ' + str(term)), ctx.guild)
    """gives you a meme for the search term"""
    back = search_tenor(term)
    await ctx.send(back)
   
@bot.command()
async def temp(ctx):
    """Returns the CPU Temp of R2D2"""
    server_logging(generate_log_message(str(ctx.author), 'temp'), ctx.guild)
    cpu=CPUTemperature()
    temp = str((int(10*(cpu.temperature)))/10)
    await ctx.send('CPU temperature is ' + temp + '°C')
    
@bot.command()
async def stats(ctx):
    """Returns the actual stats of the bot/raspberry in a privat message"""
    server_logging(generate_log_message(str(ctx.author), 'stats'), ctx.guild)
    ms = (datetime.utcnow() - ctx.message.created_at).microseconds / 1000
    user = ctx.author
    cpu=CPUTemperature()
    temp = str((int(10*(cpu.temperature)))/10)
    await user.send(content = f"Ping is: `{str(int(ms))}ms`")
    await user.send(temp + '°C')
    await user.send('Running since: ' + Started.strftime("%d %B %Y, %H:%M"))
    

@bot.command()
async def play(ctx, effect):
    """Plays a soundeffect which keyword you can enter after play if avaible. Send "!play help" for all avaible sound effects. """
    server_logging(generate_log_message(str(ctx.author), 'play ' + str(effect)), ctx.guild)
    f = open('sounddata.json')
    sounddata = json.load(f)
    
    if effect == 'help':
        keylist = []
        for key in sounddata:
            keylist.append(key)
        keytext = 'Possible Effects are: '
        for i in range(0, len(keylist)):
            keytext = keytext + keylist[i] + ', '
        await ctx.send(keytext)
        
    else:
        if ctx.author.voice != None:
            channel = str(ctx.author.voice.channel)
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            
            #definition of the local
            async def loc_play(ctx, channel, effect):
                voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=channel)
                
                error_code = excpetion_url_test(effect)
                
                if error_code == 0:
                    ydl_options = {'format': 'bestaudio', 'noplaylist': 'True'}
                    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    
                    #channel = str(ctx.author.voice.channel)
                    voiceChannel = discord.utils.get(ctx.guild.voice_channels, name = channel)
                    voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
                    if voice == None:
                        await voiceChannel.connect()
                        
    
                    with YoutubeDL(ydl_options) as ydl:
                        info = ydl.extract_info(effect, download=False)
                        URL = info['formats'][0]['url']
                        voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
                        voice.play(discord.FFmpegPCMAudio(URL, **ffmpeg_options))
                        await ctx.send('Now Playing: ' + effect)
                    
                        
                            
                elif error_code == 1:
                    await ctx.send('Sound Effect not Avaible or URL not valid! Try Again. ')
            
            if voice != None:
                await ctx.send('BB-8 is already playing some Music! Try "!add" with your sound to add to the Queue')
                
            else:
                await loc_play(ctx, channel, effect)
                while (discord.utils.get(bot.voice_clients, guild=ctx.guild) != None):
                    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
                    while voice.is_playing() or voice.is_paused():
                        await asyncio.sleep(2)
                    if sound_que.qsize() == 0:
                        await voice.disconnect()
                    else:
                        await loc_play(ctx, channel, sound_que.get())
                
        else:
            await ctx.send('You must be in a Voice Channel')
            
@bot.command()
async def add(ctx, url):
    """Add a Sound to the queue when you are in a voice channel with the bot"""
    if ctx.author.voice != None and ctx.author.voice.channel == ctx.voice_client.channel:
        #Problem still here that it will throw an error when bot is not in an voice channel. 
        sound_que.put(url)
        await ctx.send("Your Song has been added to the list and is on place number: " + str(sound_que.qsize()))
    else:
        await ctx.send("You must be in the same voice channel as the bot")
        
@bot.command()
async def playlist(ctx):
    """returns the playlist at the moment"""
    out = "Actual waiting list for Sounds: \n"
    l = list(sound_que.queue)
    for i in range(0, len(l)):
        out += (str(i+1) + ": " + str(l[i]) + "\n")
    await ctx.send(out)
    
@bot.command()
async def stop(ctx):
    """If the bot is in a Voice Channel it disconnects"""
    server_logging(generate_log_message(str(ctx.author), 'stop'), ctx.guild)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice != None:
        if ctx.author.voice != None and ctx.author.voice.channel == ctx.voice_client.channel:
            while (sound_que.empty() == False):
                sound_que.get()
            await voice.disconnect()
            
        else:
            await ctx.send('Nice Try, but you must be in the Voice Channel')
    else:
        await ctx.send('Already disconnected')
             
@bot.command()
async def pause(ctx):
    """pauses the music playing from R2D2"""
    server_logging(generate_log_message(str(ctx.author), 'pause'), ctx.guild)
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if ctx.author.voice.channel and ctx.author.voice.channel == ctx.voice_client.channel:
        voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
        if voice.is_playing():
            voice.pause()
            await asyncio.sleep(120)
            while voice.is_paused():
                await voice.disconnect()
        else:
            await ctx.send('Not possible at the moment!')
    else:
        await ctx.send('Nice Try, but you must be in the Voice Channel')

@bot.command()
async def resume(ctx):
    """resumes the music that is playing"""
    server_logging(generate_log_message(str(ctx.author), 'resume'), ctx.guild)
    if ctx.author.voice.channel and ctx.author.voice.channel == ctx.voice_client.channel:
        voice = discord.utils.get(bot.voice_clients, guild = ctx.guild)
        if voice.is_paused():
            voice.resume()
            
        else:
            await ctx.send('Not Possible at the Moment')
    else:
        await ctx.send('Nice Try, but you must be in the Voice Channel')
        
@bot.command()
async def support(ctx):
    """Type this if you need support with the bot"""
    await ctx.send("If there is some problem with the bot, please contact your server admin or oo_emperor#9843 to get support")

        
@bot.event
async def on_voice_state_update(ctx, member_before, member_after):
    
    voice_channel_before = member_before.channel
    voice_channel_after = member_after.channel
    
    if voice_channel_before == voice_channel_after:
        print()
        
    elif voice_channel_before == None:
        server = ctx.guild
        log = (str(ctx) + ' joined '+ str(voice_channel_after))
        server_logging(log, server)
        
    else:
        if voice_channel_after == None:
            server = ctx.guild
            log = (str(ctx) + ' disconnected from ' + str(voice_channel_before))
            server_logging(log, server)
            
        else:
            server = ctx.guild
            log = (str(ctx) + ' went from ' + str(voice_channel_before) + ' to ' + str(voice_channel_after))
            server_logging(log, server)   

bot.run(TOKEN)