import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os
import shutil
import requests
from bs4 import BeautifulSoup

TOKEN = 'NjM1MzY3MjIxNDAwNTY3ODE4.XawCIg.oV8rNFwzinNbWC8noYlgBABIsOI'
BOT_PREFIX = '!'
queues = {}

bot = commands.Bot(command_prefix=BOT_PREFIX)


@bot.event
async def on_ready():
    print(bot.user.name)
    print("ready")
    game = discord.Game("열일")
    await bot.change_presence(status=discord.Status.online, activity=game)


@bot.command()  # 채널에 불러오기
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"Nezuko has connected to {channel}")

    await ctx.send(f"네즈코가 {channel}채널에 들어왔다!")


@bot.command()  # 채널에서 떠나기
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        print(f"Nezuko has left {channel}")
        await ctx.send(f"네즈코가 {channel}채널에서 나갔다")
    else:
        print("Nezuko was told to leave voice channel, but was not in one")
        await ctx.send(f"네즈코는 {channel}채널에 없어요")


@bot.command()  # 음악 플레이
async def play(ctx, url: str):

    def check_queue():
        Queue_infile = os.path.isdir("./Queue")
        if Queue_infile is True:
            DIR = os.path.abspath(os.path.realpath("Queue"))
            length = len(os.listdir(DIR))
            still_q = length - 1
            try:
                first_file = os.listdir(DIR)[0]
            except:
                print("No more queued song(s)\n")
                queues.clear()
                return
            main_location = os.path.dirname(os.path.realpath(__file__))
            song_path = os.path.abspath(os.path.realpath("Queue") +  "\\" + first_file)
            if length != 0:
                print("Song done, playing next queued\n")
                print(f"Songs still in queue: {still_q}")
                song_there = os.path.isfile("song.mp3")
                if song_there:
                    os.remove("song.mp3")
                shutil.move(song_path, main_location)
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, 'song.mp3')

                voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
                voice.source = discord.PCMVolumeTransformer(voice.source)
                voice.source.volume = 0.07
            else:
                queues.clear()
                return

        else:
            queues.clear()
            print("No songs were queued before the ending of the last song\n")

    song_there = os.path.isfile("song.mp3")
    try:
        if song_there:
            os.remove("song.mp3")
            queues.clear()
            print("Removed old song file")
    except PermissionError:
        print("Trying to delete song file, but it's being played")
        await ctx.send("음악이 이미 나오고 있어요!")
        return

    Queue_infile = os.path.isdir("./Queue")
    try:
        Queue_infile = "./Queue"
        if Queue_infile is True:
            print("Removed old Queue Folder")
            shutil.rmtree(Queue_folder)
    except:
        print("No old Queue folder")

    await ctx.send("음악을 준비하고 있어요")

    voice = get(bot.voice_clients, guild=ctx.guild)

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading audio now\n")
        ydl.download([url])

    for file in os.listdir("./"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed File: {file}\n")
            os.rename(file, "song.mp3")

    voice.play(discord.FFmpegPCMAudio("song.mp3"), after=lambda e: check_queue())
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07

    rename = name.rsplit("-", 2)[0]
    await ctx.send(f"재생중: {rename}")
    print("playing\n")


@bot.command()  # 음악 일시정지
async def pause(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Music paused")
        voice.pause()
        await ctx.send("음악을 일시중지 했어요")
    else:
        print("Music not playing")
        await ctx.send("재생중인 음악이 없어요")


@bot.command()  # 음악 계속 재생
async def resume(ctx):

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        print("Resumed music")
        voice.resume()
        await ctx.send("계속 재생할게요!")
    else:
        print("Music is not paused")
        await ctx.send("음악이 이미 재생중이에요")


@bot.command()  # 음악 완전 멈추기, 재생목록 초기화
async def clear(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    queues.clear()

    queue_infile = os.path.isdir("./Queue")
    if queue_infile is True:
        shutil.rmtree("./Queue")

    if voice and voice.is_playing():
        print("Music stopped")
        voice.stop()
        await ctx.send("음악을 완전히 중지했어요. 재생목록도 초기화 했답니다!")
    else:
        print("No music playing failed to stop")
        await ctx.send("재생중인 음악이 없어요")


@bot.command()
async def add(ctx, url: str):
    Queue_infile = os.path.isdir("./Queue")
    if Queue_infile is False:
        os.mkdir("Queue")
    DIR = os.path.abspath(os.path.realpath("Queue"))
    q_num = len(os.listdir(DIR))
    q_num += 1
    add_queue = True
    while add_queue:
        if q_num in queues:
            q_num += 1
        else:
            add_queue = False
            queues[q_num] = q_num

    queue_path = os.path.abspath(os.path.realpath("Queue") + f"\song{q_num}.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': queue_path,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print("Downloading Audio now\n")
        await ctx.send("음악을 추가할게요")
        ydl.download([url])
    await ctx.send("재생 목록 추가 [" + str(q_num) + "]")

    print("Song added to queue\n")


@bot.command()  # 다음곡 재생하기
async def next(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        print("Playing next")
        voice.stop()
        await ctx.send("다음곡을 재생할게요")
    else:
        print("No music playing failed to playing next song")
        await ctx.send("다음곡이 없어요.")


@bot.event
async def on_message(message):
    # 봇 정보/명령어
    if message.content.startswith("!도움"):
        embed = discord.Embed(
            title='네즈코 통합 Bot Information',
            description='Version 0.1 last updated 2019.10.21\n',
            colour=discord.Colour.orange()
        )
        embed.add_field(name='-----------------------------명령어 리스트-----------------------------',
                        value='모든 명령어는 느낌표를 붙입니다\n\n', inline=False)

        embed.add_field(name='[전적 검색]', value='!롤 닉네임 - 소환사의 전적을 불러옵니다\n\n', inline=False)
        embed.add_field(name='[음악 기능]', value='!join - 네즈코를 채널로 옮깁니다\n' +
                                              '!leave - 네즈코를 채널에서 내보냅니다\n' +
                                              '!play 유튜브주소 - 음악을 재생합니다\n' +
                                              '!add 유튜브주소 - 재생목록에 음악을 추가합니다\n' +
                                              '!next - 다음 곡을 재생합니다\n' +
                                              '!pause - 재생중인 음악을 일시정지합니다\n' +
                                              '!resume - 음악을 다시 재생합니다\n' +
                                              '!clear - 재생중인 음악을 중지하고 재생목록을 초기화 합니다\n', inline=False)

        embed.set_image(
            url="https://1.gall-img.com/tdgall/files/attach/images/82/929/905/065/561638e19f671203c3e3c71b04afe7dd.png")

        await message.channel.send(embed=embed)

    if message.content.startswith('!롤'):
        name = message.content[3:len(message.content)]

        req = requests.get('https://www.op.gg/summoner/userName=' + name)
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        # print(soup)

        try:
            # 솔로랭크 정보
            rank_solo = soup.find('div', {'class': 'TierRank'}).get_text()
            point = soup.find('span', {'class': 'LeaguePoints'}).get_text().split('\n')[1].split('LP')[0]
            wins = soup.find('span', {'class': 'wins'}).get_text().split('W')[0] + '승'
            losses = soup.find('span', {'class': 'losses'}).get_text().split('L')[0] + '패'
            winratio = '승률' + soup.find('span', {'class': 'winratio'}).get_text().split('Ratio')[1]

            # 자유랭크 정보
            rank_sub = soup.find('div', {'class': 'sub-tier__rank-tier'}).get_text().split('\n')[1]
            point_sub = soup.find('div', {'class': 'sub-tier__league-point'}).get_text().split('LP')[0]
            wins_losses_sub = soup.find('span', {'class': 'sub-tier__gray-text'}).get_text()
            wins_sub = wins_losses_sub.split('W')[0].split('/')[1] + '승'
            losses_sub = wins_losses_sub.split('W')[1].split('L')[0] + '패'
            winratio_sub = \
                '승률' + soup.find('div', {'class': 'sub-tier__gray-text'}).get_text().split('\n')[1].split('Rate')[1]

            # 모스트 챔프 (첫번째 하나만)
            champ_name = soup.find('div', {'class': 'ChampionName'}).get_text().split('\n')[2].strip()
            champ_kda = soup.find('div', {'class': 'KDA'}).get_text().split('KDA')[0].strip()
            kdaint = champ_kda.split(':')[0]
            champ_KDAEach = soup.find_all('div', {'class': 'KDAEach'})[0].get_text()
            champ_kill = champ_KDAEach.split('/')[0].strip()
            champ_death = champ_KDAEach.split('/')[1].strip()
            champ_assist = champ_KDAEach.split('/')[2].strip()
            champ_winrate_playtime = soup.find('div', {'class': 'Played'}).get_text().strip()
            champ_winrate = champ_winrate_playtime.split('\n')[0].strip()
            champ_playtime = champ_winrate_playtime.split('\t\t\t\t')[1].strip().split('Played')[0]
            # print(champ_winrate)
            # print(champ_playtime)

            msg = None
            if float(kdaint) >= 4:
                msg = name + "님은 " + champ_name + " 장인이에요!"
            if 3 <= float(kdaint) < 4:
                msg = name + "님은 " + champ_name + " 숙련자에요!"
            if 2 <= float(kdaint) < 3:
                msg = name + "님은 " + champ_name + " 연습중이에요!"
            if float(kdaint) < 2:
                msg = name + "님은 " + champ_name + " 충이에요!\n" + \
                      "좀 더 연습하세요!"
            print(msg)

            # 챔프 이미지 가져오기
            temp = str(soup.find('img', {'alt': champ_name}))
            champ_image = temp.split('src="//')[1]
            champ_image = "http://" + champ_image.split('"')[0]

            # 티어 이미지 가져오기
            temp = str(soup.find_all('img', {'class': 'Image'})[2])
            tierurl = temp.split('src="//')[1]
            tierurl = "http://" + tierurl.split('"')[0]
            # print(tierurl)

            embed = discord.Embed(
                title='전적 검색 결과',
                description='소환사: ' + name + '\n\n',
                colour=discord.Colour.blue()
            )

            embed.add_field(name='---솔로랭크---', value=
            rank_solo + ' - ' + point + '포인트' + ' / ' + wins + ' / ' + losses + ' / ' + winratio, inline=False)

            embed.add_field(name='---자유랭크---', value=
            rank_sub + ' - ' + point_sub + ' 포인트' + ' / ' + wins_sub + ' / ' + losses_sub + ' / ' + winratio_sub,
                            inline=False)

            embed.add_field(name='---모스트 챔피언---', value=champ_name + ' - ' + champ_kda + ' ' + ' [ '
                        + champ_kill + ' / ' + champ_death + ' / ' + champ_assist + ' ] / ' + ' 승률: ' + champ_winrate
                        + ' / ' + champ_playtime + '게임\n' + msg, inline=False)

            embed.set_image(url=champ_image)  # 모스트 챔피언 이미지
            embed.set_thumbnail(url=tierurl)  # 티어 이미지

            await message.channel.send(embed=embed)
        except:
            print("랭크 정보중 등록되지 않은 정보가 있습니다")
            await message.channel.send("정보를 불러올 수 없어요!\n" +
                                       "솔로랭크 또는 자유랭크 배치를 보지 않은 소환사에요")

    await bot.process_commands(message)


bot.run(TOKEN)