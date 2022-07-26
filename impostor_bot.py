import discord
import json
import asyncio

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]
help_msg='''Usage:
`$impostor help` shows this message
`$impostor record start RECORDING-NAME` starts a recording in the room that you are in. `RECORDING-NAME` will be the name of the recording
`$impostor record stop` stops the recording
`$impostor @USER RECORDING-NAME` plays the given user's recording if it exists. `RECORDING-NAME` is the name of the recording, `@USER` is the name of the user
`$impostor #!CHANNEL @USER RECORDING-NAME` plays the given user's recording if it exists in specified channel. `RECORDING-NAME` is the name of the recording, `@USER` is the name of the user, `#!CHANNEL` is the name of the voice channel'''
if __name__ == '__main__':
    
    intents = discord.Intents.all()

    f = open('config.json')
    config = json.load(f)
    f.close()
    if not config["eula"]:
        print("please accept the end user licence agreement")
        quit()
    client = discord.Client(intents=intents)
    member = []
    bot_channel_names = config["bot_channels"]
    print(bot_channel_names)

    async def once_done(sink: discord.sinks.mp3, channel: discord.TextChannel, name:str, calling_user:str, *args):  # Our voice client already passes these in.
        user_recorded = [f"<@{user_id}>" for user_id, audio in sink.audio_data.items() if user_id == calling_user]
        await sink.vc.disconnect()  # Disconnect from the voice channel.
        files = [discord.File(audio.file, f"{user_id}-{name}.{sink.encoding}") for user_id, audio in sink.audio_data.items() if user_id == calling_user]  # List down the files.
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
            for channel in guild.channels:
                if channel.name == bot_channel_names[0]:
                    await channel.send("Bienvenidos, Soy el impuster de amogus")

    @client.event
    async def on_message(message):
        if message.channel.name not in bot_channel_names:
            print(message.channel.name)
            return
        if message.author == client.user:
            return
        roles = [r.name for r in message.author.roles]
        if config["bot_user"] not in roles:
            return
        if message.content.startswith('$impostor'):
            if "$impostor help" == message.content or "$impostor" == message.content:
                await message.channel.send(help_msg)

            if "reset" in message.content:
                await member[0].edit(nick = "IMPOSTOR")
                with open('pfp.jpg', 'rb') as image:
                    await client.user.edit(avatar=image.read())

            if "record start " in message.content:
                f_name = remove_prefix(message.content, "$impostor record start ")
                vc = await message.author.voice.channel.connect()
                vc.start_recording(discord.sinks.mp3.MP3Sink(), once_done, message.channel, f_name, message.author.id)

            if "record stop" in message.content:
                for vc in client.voice_clients:
                    vc.stop_recording() 

            if message.mentions:
                try:
                    if member[0].nick != message.mentions[0].display_name:
                        name = message.mentions[0].display_name
                        await member[0].edit(nick = name)
                        pfp = await message.mentions[0].avatar.read()
                        await client.user.edit(avatar=pfp)
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