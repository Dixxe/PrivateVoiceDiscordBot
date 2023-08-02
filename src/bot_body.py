import disnake
from disnake.ext import tasks, commands

################
intents = disnake.Intents.default()
intents.message_content = True

global slash_inter, button_inter

slash_inter: disnake.AppCmdInter
button_inter = disnake.MessageInteraction


activity = disnake.Activity(
    name="Made by dixxe",
    type=disnake.ActivityType.listening)
################
bot = commands.Bot(command_prefix='>', intents=intents, help_command=None, activity=activity)

global vc

category = disnake.CategoryChannel
vc = {} # dictionary with user id and his vc id- {'User id': 'vc id'}



@bot.event
async def on_ready():
    print(f'Бот {bot.user} запущен')
    delete_empty_vc.start()
    global guild
    guild = bot.guilds[0] # because im using it on one guild

@bot.slash_command(description='Описание возможностей бота.')
async def help(slash_inter):
    await slash_inter.response.defer()
    emb = disnake.Embed(title='Все команды бота', color=9699539)
    emb.add_field(name='/create', value='Создать персональный голосовой канал.', inline=False)
    emb.add_field(name='/remove', value='Удалить персональный голосовой чат', inline=False)
    emb.add_field(name='/add [пользователь]', value='Разрешить пользователю присоединиться к вам.', inline=False)
    emb.add_field(name='/delete [пользователь]', value='Запретить пользователю присоединиться к вам.', inline=False)
    emb.add_field(name='/set [категории]', value='Привязать категорию где будут созданные голосовые каналы.', inline=False)
    emb.set_author(name='Бусти создателя', url='https://boosty.to/dixxe')
    await slash_inter.edit_original_response(embed=emb)

@bot.slash_command(description='Создать персональный голосовой канал.')
async def create(slash_inter):
    await slash_inter.response.defer()
    try:
        if(slash_inter.author.name not in vc):
            category = linked_category
            everyone = guild.default_role
            channel = await category.create_voice_channel(name=f'Комната {slash_inter.author.name}', overwrites={everyone : disnake.PermissionOverwrite(connect=False), slash_inter.author : disnake.PermissionOverwrite(connect=True)}, reason=f'Канал был создан {slash_inter.author.name}')
            vc[f"{slash_inter.author.name}"]= channel.id
            print(vc)
            await slash_inter.edit_original_response(f'Канал создан: {channel}')
        else:
            await slash_inter.edit_original_response(f'У вас уже есть канал: {vc[slash_inter.author.name]}.')
    except Exception as e:
        await slash_inter.edit_original_response(f'Что-то пошло не так, сообщите создателю код ошибки:\n```{e}```')

@bot.slash_command(description='Привязать категорию где будут созданные голосовые каналы.')
async def set(slash_inter, category : disnake.CategoryChannel):
    await slash_inter.response.defer()
    try:
        global linked_category
        linked_category = category
        await slash_inter.edit_original_response('Категория привязана')
    except Exception as e:
        await slash_inter.edit_original_response(f'Что-то пошло не так, сообщите создателю код ошибки:\n```{e}```')

@bot.slash_command(description="Удалить персональный голосовой чат")
async def remove(slash_inter):
    await slash_inter.response.defer()
    try:
        if(slash_inter.author.name in vc):
            channel_id = vc[slash_inter.author.name]
            channel = bot.get_channel(channel_id)
            await channel.delete()
            await slash_inter.edit_original_response('Ваш канал удален.')
            vc.pop(slash_inter.author.name)
        else:
            await slash_inter.edit_original_response('У вас нету канала.')
    except Exception as e:
        await slash_inter.edit_original_response(f'Что-то пошло не так, сообщите создателю код ошибки:\n```{e}```')

@bot.slash_command(description="Разрешить пользователю присоединиться к вам.")
async def add(slash_inter, user : disnake.Member):
    try:
        await slash_inter.response.defer()
        if(slash_inter.author.name in vc):
            channel_id = vc[slash_inter.author.name]
            channel = bot.get_channel(channel_id)
            await channel.edit(overwrites={user : disnake.PermissionOverwrite(connect=True)})
            await slash_inter.edit_original_response(f'Пользователь {user.mention} может присоединиться в вашу комнату.')
        else:
            await slash_inter.edit_original_response('У вас нету канала.')
    except Exception as e:
        await slash_inter.edit_original_response(f'Что-то пошло не так, сообщите создателю код ошибки:\n```{e}```')

@bot.slash_command(description="Запретить пользователю присоединиться к вам.")
async def delete(slash_inter, user : disnake.Member):
    await slash_inter.response.defer()
    try:
        if(slash_inter.author.name in vc):
            channel_id = vc[slash_inter.author.name]
            channel = bot.get_channel(channel_id)
            await channel.edit(overwrites={user : disnake.PermissionOverwrite(connect=None)})
            await slash_inter.edit_original_response(f'Пользователь {user.mention} больше не может присоединиться в вашу комнату.')
        else:
            await slash_inter.edit_original_response('У вас нету канала.')
    except Exception as e:
        await slash_inter.edit_original_response(f'Что-то пошло не так, сообщите создателю код ошибки:\n```{e}```')
@tasks.loop(minutes=5.0)
async def delete_empty_vc():
    temp_dict = vc
    for user in temp_dict.keys():
        channel_id = vc[user]
        channel = bot.get_channel(channel_id)
        members = channel.members
        if (len(members) == 0):
            await channel.delete()
            vc.pop(user)


with open('token.txt', 'r') as file:
    token = file.read()
bot.run(token)