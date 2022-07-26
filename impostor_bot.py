import discord
import json
import asyncio

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]

if __name__ == '__main__':
    intents = discord.Intents.all()

    f = open('config.json')
    config = json.load(f)
    f.close()

    client = discord.Client(intents=intents)
    member = []
    bot_channel_names = config["bot_channels"]
    print(bot_channel_names)

    async def once_done(sink: discord.sinks.mp3, channel: discord.TextChannel, name:str, *args):  # Our voice client already passes these in.
        user_recorded = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items()]
        await sink.vc.disconnect()  # Disconnect from the voice channel.
        files = [discord.File(audio.file, f"{user_id}-{name}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.
        for f in files:
            with open(f"recordings/{f.filename}", "wb") as output: 
                output.write(f.fp.getbuffer())
        await channel.send(f"finished recording audio for: {', '.join(user_recorded)}.", files=files)  # Send a message with the accumulated files.
    
    @client.event
    async def on_ready():
        await client.change_presence(status=discord.Status.invisible)
        for guild in client.guilds:
            member.append(guild.get_member(client.user.id))
            print(member)

    @client.event
    async def on_message(message):
        if message.channel.name not in bot_channel_names:
            print(message.channel.name)
            return
        if message.author == client.user:
            return

        if message.content.startswith('$impostor'):
            if "reset" in message.content:
                await member[0].edit(nick = "IMPOSTOR")
                with open('pfp.jpg', 'rb') as image:
                    await client.user.edit(avatar=image.read())

            if "record start " in message.content:
                f_name = remove_prefix(message.content, "$impostor record start ")
                vc = await message.author.voice.channel.connect()
                vc.start_recording(discord.sinks.mp3.MP3Sink(), once_done,message.channel,f_name)

            if "record stop" in message.content:
                for vc in client.voice_clients:
                    vc.stop_recording() 

            if message.mentions:
                try:
                    if member[0].nick != message.mentions[0].display_name:
                        pfp = await message.mentions[0].avatar.read()
                        await client.user.edit(avatar=pfp)
                        name = message.mentions[0].display_name
                        await member[0].edit(nick = name)
                    else:
                        print("already impersonating")

                    if message.channel_mentions:
                        file_title = "recordings/"+str(message.mentions[0].id)+"-"+" ".join(message.content.split(" ")[3:])+".mp3"
                        print(file_title)
                        vc = await message.channel_mentions[0].connect()
                    else:
                        file_title = "recordings/"+str(message.mentions[0].id)+"-"+" ".join(message.content.split(" ")[2:])+".mp3"
                        print(file_title)
                        vc = await message.author.voice.channel.connect()

                    vc.play(discord.FFmpegPCMAudio(file_title))
                    while vc.is_playing():
                        await asyncio.sleep(1)
                    await vc.disconnect()
                except Exception as e:
                    print(e)
                    await message.channel.send("cannot imposter, too much pasta")

    client.run(config['private_token'])