from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from aiogram.utils.deep_linking import decode_payload, create_start_link
from aiogram import Bot

import random, re, sqlite3



def add_user(message: Message):
    user_id = message.from_user.id
    username = user_id if message.from_user.username is None else message.from_user.username
    first_name = message.from_user.first_name

    if cursor.execute('select user_id from users where user_id = ?', (user_id,)).fetchone() is None:
        cursor.execute('insert into users values(?, ?, ?, ?, ?)', (user_id, username, first_name, 0, 0))


def add_chat(user_id, chat_id):
    if cursor.execute('select chat_id from chats where user_id = ? and chat_id = ?', (user_id, chat_id)).fetchone() is None:
        cursor.execute('insert into chats values (?, ?)', (user_id, chat_id))


def user_check(user_id):
    if cursor.execute('select user_id from users where user_id = ?', (user_id,)).fetchone() is None:
        return 1
    

def update_user(message: Message):
    user_id = message.from_user.id
    username = user_id if message.from_user.username is None else message.from_user.username
    first_name = message.from_user.first_name

    if cursor.execute('select user_id from users where user_id = ?', (user_id,)).fetchone() is None:
        cursor.execute('update users set username = ?, first_name = ? where user_id = ?', (username, first_name, user_id))



router = Router()

connectionDB = sqlite3.connect('pipisa_db.db')
cursor = connectionDB.cursor()



@router.message(CommandStart())
async def cmd_start(message: Message):
    data = re.match(r'^\/start[^ ]* (.*)', message.text)

    if data is None:
        return await message.reply('Нажмите <a href="/help">/help</a>, чтобы вывести справку', parse_mode='HTML')
    
    user_id = message.from_user.id

    try:
        if cursor.execute('select user_id from users where user_id = ?', (decode_payload(data[1]),)).fetchone() is None:
            return await message.reply('Неверная реферальная ссылка!')
    except:
         return await message.reply('Неверная реферальная ссылка!')
    
    if cursor.execute('select user_id from users where user_id = ?', (user_id,)).fetchone() is None:
        add_user(message)

        cursor.execute('update users set length = length + 5 where user_id = ?', (user_id,))
        cursor.execute('update users set length = length + 1 where user_id = ?', (decode_payload(data[1]),))
        
        await message.answer(f'<a href="t.me/{user_id}">{message.from_user.first_name}</a> теперь твоя пиписа равна: {5}см\nНажмите <a href="/help">/help</a>, чтобы вывести справку', parse_mode='HTML')
    else:
        return await message.reply('Вы уже есть в базе!')
    
    connectionDB.commit()


#Справка
@router.message(Command('help'))
async def help_pipisa(message: Message):
    await message.reply('<b>Описание команд бота:</b>\n<a href="/grow">/grow</a> - Попытайте удачу и выращивайте вашу "Пипису" раз в день. Диапазон от -5 до 10\n<a href="/top">/top</a> - Посмотреть рейтинг "Пипис" чата\n<a href="/global_top">/global_top</a> - Посмотреть глобальный рейтинг "Пипис"\n<a href="/give">/give</a> - Передайте часть своей "Пиписы" другому пользователю, например, в споре на сантиметры\n<a href="/ref">/ref</a> - Пригласите друга по реферальной ссылке и получите сантиметры за это', parse_mode='HTML')


#Увеличение пиписы
@router.message(Command('grow'))
async def grow_pipisa(message: Message):
    # Обновление данных пользователя, если пользователь существует
    update_user(message)

    user_id = message.from_user.id
    username = user_id if message.from_user.username is None else message.from_user.username
    first_name = message.from_user.first_name
    chat_id = message.chat.id

    # Проверка на существование пользователя в БД
    if user_check(user_id):
        add_user(message)

    # Провека на существование чата в БД
    add_chat(user_id, chat_id)

    forwardDate = message.date.strftime('%Y-%m-%d')
    print(cursor.execute('select last_grow from users where user_id = ?', (message.from_user.id,)).fetchone()[0])
    print(forwardDate)

    pipisaSize = cursor.execute('select length from users where user_id = ?', (user_id,)).fetchone()[0]
    
    # Проверка на последний запрос
    if cursor.execute('select last_grow from users where user_id = ?', (user_id,)).fetchone()[0] == forwardDate:
        return await message.answer(f'<a href="t.me/{username}">{first_name}</a>, сегодня ты уже играл!\nТекущий размер: {pipisaSize}см!', parse_mode='HTML', disable_web_page_preview=True)
    
    numberRandom = random.randint(-5, 10)
    
    cursor.execute('update users set length = length + ?, username = ?, first_name = ?, last_grow = ? where user_id = ?', (numberRandom, username, first_name, forwardDate, user_id))

    pipisaSize = cursor.execute('select length from users where user_id = ?', (user_id,)).fetchone()[0]

    if numberRandom > 0:
        await message.reply(f'<a href="t.me/{username}">{first_name}</a>, твоя пиписа выросла на {numberRandom}см!\nТеперь она равна {pipisaSize}см!\nСледующая попытка завтра!', parse_mode='HTML', disable_web_page_preview=True)
    elif numberRandom < 0:
        await message.reply(f'<a href="t.me/{username}">{first_name}</a>, твоя пиписа уменьшилась на {abs(numberRandom)}см!\nТеперь она равна {pipisaSize}см!\nСледующая попытка завтра!', parse_mode='HTML', disable_web_page_preview=True)
    else:
        await message.reply(f'<a href="t.me/{username}">{first_name}</a>, твоя пиписа не выросла!\nТеперь она равна {pipisaSize}см!\nСледующая попытка завтра!', parse_mode='HTML', disable_web_page_preview=True)
    connectionDB.commit()


#Топ 10 пипис группы
@router.message(Command('top'))
async def stats(message: Message):
    # Обновление данных пользователя, если пользователь существует
    update_user(message)

    user_id = message.from_user.id
    chat_id = message.chat.id

    # Провека на существование чата в БД
    add_chat(user_id, chat_id)

    stats = cursor.execute('select users.first_name, users.length from chats inner join users on chats.user_id = users.user_id where chats.chat_id = ? order by length DESC limit 10', (chat_id,)).fetchall()

    list = 'Топ 10 пипис чата:\n'

    for i in range(len(stats)):
        list += f'{i + 1}. {stats[i][0]}: {stats[i][1]}см\n'

    await message.answer(list)
    connectionDB.commit()


#Топ 10 пипис мира
@router.message(Command('global_top'))
async def global_stats(message: Message):
    # Обновление данных пользователя, если пользователь существует
    update_user(message)

    globalStats = cursor.execute('select first_name, length from users order by length DESC limit 10').fetchall()

    list = 'Топ 10 пипис мира:\n'

    for i in range(len(globalStats)):
        list += f'{i + 1}. {globalStats[i][0]}: {globalStats[i][1]}см\n'

    await message.answer(list)


#Топ 100 пипис мира
@router.message(Command('gay_top'))
async def global_stats(message: Message):
    # Обновление данных пользователя, если пользователь существует
    update_user(message)

    globalStats = cursor.execute('select first_name, length from users order by length DESC limit 100').fetchall()

    list = 'Топ 100 пипис мира:\n'

    for i in range(len(globalStats)):
        list += f'{i + 1}. {globalStats[i][0]}: {globalStats[i][1]}см\n'

    await message.answer(list)


#Передача сантиметов пользователю
@router.message(Command('give'))
async def give_pipisa(message: Message):
    # Обновление данных пользователя, если пользователь существует
    update_user(message)

    send_message = re.match(r'^\/give(?:\S* .* (\d+))', message.text)

    for i in message.entities:
        if 'mention' == i.type: 
            username = message.text[i.offset:i.length + i.offset][1:]
        elif 'text_mention' == i.type:
            username = i.user.id
    
    if username is None:
        return await message.reply('Вызов команды должен выглядеть как <a href="/give @username">/give @username 5</a> или <a href="/give@xxlpensilbot @username">/give@xxlpensilbot @username 5</a>, где <a href="@username">@username</a> - имя получателя, а 5 - кол-во см', parse_mode='HTML')    

    if cursor.execute('select user_id from users where username = ?', (username,)).fetchone() is None:
        return await message.answer('Пользователя нет в базе!')
    
    length = cursor.execute('select length from users where user_id = ?', (message.from_user.id,)).fetchone()[0]

    if length < int(send_message[1]):
        return await message.answer(f'У тебя недостаточно писюна!\nТвой размер: {length}см')
    else:
        cursor.execute('update users set length = length + ? where username = ?', (send_message[1], username))
        cursor.execute('update users set length = length - ? where user_id = ?', (send_message[1], message.from_user.id))

        first_name = message.from_user.first_name
        length = cursor.execute('select length from users where user_id = ?', (message.from_user.id,)).fetchone()[0]
        nd_name = cursor.execute('select first_name from users where username = ?', (username,)).fetchone()[0]
        nd_length = cursor.execute('select length from users where username = ?', (username,)).fetchone()[0]

        await message.answer(f'{first_name} теперь твой писюн равен: {length}см\nПисюн {nd_name} равен: {nd_length}см!')

        connectionDB.commit()


#Создание реферальной ссылки  
@router.message(Command('ref'))
async def create_ref(message: Message, bot: Bot):
    # Обновление данных пользователя, если пользователь существует
    update_user(message)

    # Провека на существование пользователя в БД
    if user_check(message.from_user.id):
        add_user(message)

    link = await create_start_link(bot, str(message.from_user.id), encode=True)

    await message.answer(f'{link}\nПримкните к гонке "Пипис" и покажи всем свое лидерство, заняв первые места в глобальном топе!\nПолучи 1см за кажого приведенного друга!\nПрисоединись по ссылке и получи 5см!')


#Промокоды
@router.message(Command('promo'))
async def uses_promo(message: Message):
    promo_match = re.match(r'^\/promo (\d+)', message.text)

    if promo_match is None:
        return await message.answer('Вызов команды должен выглядеть как <code>/promo ВАШ_ПРОМИК</code>')
    promocode = promo_match[1]

    if cursor.execute('select code_id from promocode where code_id = ?', (promocode,)).fetchone() is None:
        return await message.answer('Данного промокода не существует!')
    
    if cursor.execute('select uses_left from promocode where code_id = ? and uses_left > 0', (promocode,)).fetchone() is None:
        return await message.answer('Активаций больше нет!')
    
    if cursor.execute('select user_id from uses_of_promo where user_id = ? and code_id = ?', (message.from_user.id, promocode)).fetchone():
        return await message.answer('Ты уже использовал промокод!')
    
    cursor.execute('begin')

    cursor.execute('''
                    update users
                    set length = length + (
                        select length
                        from promocode
                        where code_id = ?
                    )
                    where user_id = ?
                    ;
                ''', (promocode, message.from_user.id))
    
    cursor.execute('''
                    update promocode
                    set uses_left = uses_left - 1
                    where code_id = ?
                    ;
                    ''', (promocode,))
    
    cursor.execute('''
                    insert into uses_of_promo(user_id, code_id)
                    values (?, ?)
                    ;
                    ''', (message.from_user.id, promocode))
    
    cursor.execute('end')

    connectionDB.commit()

    length = cursor.execute('select length from users where user_id = ?', (message.from_user.id,)).fetchone()[0]
    
    await message.answer(f'{message.from_user.first_name}, теперь твоя пиписа равна {length}см!')


#Удаление пользователя из топа группы, при его выходе
@router.message()
async def on_user_leave(message: Message):
    if message.left_chat_member:
        cursor.execute('delete from chats where user_id = ? and chat_id = ?', (message.from_user.id, message.chat.id))
        connectionDB.commit()
