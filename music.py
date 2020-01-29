import discord
from discord.ext import commands
from discord.utils import get
import logging
import os
import asyncio
from itertools import cycle
import youtube_dl
import shutil
import requests as rq
import json
file = open('youtube_api.txt', 'r')
YOUTUBE_API = file.read().replace('\n', '')
queues={}

class Music(commands.Cog):
    def __init__(self, client):
        self.client=client
    @commands.command()
    async def join(self,ctx):
        if ctx.author.voice and ctx.author.voice.channel:
            channel = ctx.author.voice.channel
        else:
            await ctx.send("You are not connected to a voice channel")
            return
        global vc
        try:
            vc=await channel.connect()
        except:
            TimeoutError
    @commands.command()
    async def leave(self,ctx):
        try:
            if vc.is_connected():
                await vc.disconnect()
        except:
            TimeoutError
            pass
    @commands.command()
    async def play(self,ctx,*,url):
        def check_queue():
            Queue_infile=os.path.isdir("./Queue")
            if Queue_infile is True:
                DIR=os.path.abspath(os.path.realpath("Queue"))
                length=len(os.listdir(DIR))
                still_q=length-1
                try:
                    first_file=os.listdir(DIR)[0]
                except:
                    print("No more songs")
                    queues.clear()
                    return
                main_location= os.path.dirname(os.path.realpath(__file__))
                song_path=os.path.abspath(os.path.realpath("Queue")+"\\"+first_file)
                if length!=0:
                    print("Playing next song")
                    print(f"Songs in queue:{still_q}")
                    song_there=os.path.isfile("song.mp3")
                    if song_there:
                        os.remove("song.mp3")
                    shutil.move(song_path,main_location)
                    for file in os.listdir("./"):
                        if file.endswith(".mp3"):
                            os.rename(file,"song.mp3")
                    vc.play(discord.FFmpegPCMAudio("song.mp3"),after=lambda e: check_queue())
                    vc.source=discord.PCMVolumeTransformer(vc.source)
                    vc.source.volume=0.07
                else:
                    queues.clear()
                    return
            else:
                queues.clear()
                print("No song")
        if os.path.isfile("song.mp3"):
            os.remove("song.mp3")
            queues.clear()
        if os.path.isfile("./Queue") is True:
            shutil.rmtree("./Queue")

        vc = ctx.voice_client
        ydl_opts={
        'format':'bestaudio/best',
        'postprocessors': [{
            'key':'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality':'192',

        }],
        }
        song_pack = rq.get(
        "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={}&key={}".format(url, YOUTUBE_API)).json()
        url = "https://www.youtube.com/watch?v={}".format(
                song_pack['items'][0]['id']['videoId'])
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            print("downloading song")
            try:
                ydl.download([url])
            except:
                await ctx.send("Error downloading invalid url")
        if os.path.isfile("song.mp3"):
            os.remove("song.mp3")
        for file in os.listdir("./"):
            if file.endswith(".mp3"):
                name=file
                #print(f"Renamed file:{file}\n")
                try:
                    os.rename(file,"song.mp3")
                except:
                    pass
        try:
            await ctx.send("Playing Music")
            vc.play(discord.FFmpegPCMAudio("song.mp3"),after=lambda e: check_queue())
        except:
            await ctx.send("The bot may not be in voice channel")
        try:
            vc.source=discord.PCMVolumeTransformer(vc.source)
            vc.source.volume=0.07
        except:
            AttributeError
    @commands.command()
    async def pause(self,ctx):
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("Paused!")
        else:
            await ctx.send("Music not playing!")
    @commands.command()
    async def resume(self,ctx):
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("Music Resumed!")
        else:
            await ctx.send("Music not paused")
    @commands.command()
    async def stop(self,ctx):
        vc= get(self.client.voice_clients,guild=ctx.guild)
        queues.clear()
#Removing the complete Directory of Queued Songs 
        queue_infile=os.path.isdir("./Queue")      
        if queue_infile is True:
            shutil.rmtree("./Queue")

        if vc and vc.is_playing:
            vc.stop()
            await ctx.send("Stopped")
        else:
            await ctx.send("Music not playing!")

    @commands.command()
    async def next(self,ctx):
        vc=get(self.client.voice_clients,guild=ctx.guild)
        if vc and vc.is_playing:
            print("Playing next")
            vc.stop()
            await ctx.send("Playing Next Song!")
        else:
            await ctx.send("No song in queue")
    @commands.command()
    #URL will represent the name of song now after Youtube search feature is added
    async def queue(self,ctx,*,url):
        try:
            Queue_infile=os.path.isdir("./Queue")
            if Queue_infile is False:
                os.mkdir("Queue")
            DIR=os.path.abspath(os.path.realpath("Queue"))
            q_num=len(os.listdir(DIR))
            q_num+=1
            add_queue=True
            while add_queue:
                if q_num in queues:
                    q_num+=1
                else:
                    add_queue = False
                    queues[q_num]=q_num
            queue_path=os.path.abspath(os.path.realpath("./Queue")+f"\song{q_num}.%(ext)s")
            ydl_opts={
            'default_search': 'auto',
            'format':'bestaudio/best',
            'outtmpl':queue_path,
            'postprocessors': [{
                'key':'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality':'192',

            }],

            }
            song_pack = rq.get(
            "https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={}&key={}".format(url, YOUTUBE_API)).json()
            url = "https://www.youtube.com/watch?v={}".format(
                    song_pack['items'][0]['id']['videoId'])
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                print("downloading song")
                ydl.download([url])
            await ctx.send("Added to queue at no."+str(q_num))
        except:
            pass


#Setup Cog Command

def setup(client):
    client.add_cog(Music(client))

