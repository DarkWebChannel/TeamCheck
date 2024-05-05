#Спасибо за использование!
#Сделано с любовью и слезами(
#by KEFRC

import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.fsm_storage.memory import MemoryStorage

admin_id =   #https://t.me/myidbot
token = "" #https://t.me/BotFather
chat_link = "" #ссылка на чат

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

question_1 = "Сколько вам лет?"
question_2 = "Сколько времени готовы уделять работе?"
question_3 = "Был ли у вас опыт в похожем проекте?"
question_4 = "Почему хотите сюда попасть?"

admin_question_1 = "Возраст"
admin_question_2 = "Сколько готов уделять времени"
admin_question_3 = "Был ли опыт"
admin_question_4 = "Причина захода"

cb = CallbackData("fabnum", "action")
main_menu = InlineKeyboardMarkup(row_width=1)
main_menu.add(InlineKeyboardButton(text='Подать заявку', callback_data=cb.new(action='start_answer')))

send_menu = InlineKeyboardMarkup(row_width=2)
send_menu.add(InlineKeyboardButton(text="Отправить💬", callback_data=cb.new(action="send")),
              InlineKeyboardButton(text="Заполнить заново", callback_data=cb.new(action='application')))

def admin_menu(ID):
    menu = InlineKeyboardMarkup(row_width=2)
    menu.add(InlineKeyboardButton(text="Принять✅", callback_data=f"#y{str(ID)}"),
             InlineKeyboardButton(text="Отклонить❌", callback_data=f'#n{str(ID)}'))
    return menu

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user (
                                user_id INTEGER PRIMARY KEY,
                                answer1 TEXT,
                                answer2 TEXT,
                                answer3 TEXT,
                                answer4 TEXT,
                                username TEXT
                              )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS client (
                                user_id INTEGER PRIMARY KEY
                              )''')
        self.connection.commit()
        print("The database is connected successfully")

    def add_user(self, ID, username):
        with self.connection:
            self.cursor.execute("INSERT INTO user VALUES (?, ?, ?, ?, ?, ?)", (ID, "null", "null", "null", "null", username))

    def add_client(self, ID):
        with self.connection:
            self.cursor.execute("INSERT INTO client VALUES (?)", (ID,))

    def update_user_data(self, ID, a1, a2, a3, a4):
        with self.connection:
            self.cursor.execute("UPDATE user SET answer1 = ?, answer2 = ?, answer3 = ?, answer4 = ? WHERE user_id = ?", (a1, a2, a3, a4, ID))

    def get_user_data(self, ID):
        with self.connection:
            return self.cursor.execute("SELECT * FROM user WHERE user_id = ?", (ID,)).fetchone()

    def delete_zayavka(self, ID):
        with self.connection:
            self.cursor.execute("DELETE FROM user WHERE user_id = ?", (ID,))

    def client_exists(self, ID):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM user WHERE user_id = ?", (ID,)).fetchone()
            return bool(result)

    def confirmed_user(self, ID):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM client WHERE user_id = ?", (ID,)).fetchone()
            return bool(result)

db = Database("data.db")

class get_answer(StatesGroup):
    answer1 = State()
    answer2 = State()
    answer3 = State()
    answer4 = State()

async def on_startup(_):
    print("Bot Started")

async def command_start(message: types.Message):
    if message.from_user.username is not None:
        if db.confirmed_user(message.from_user.id):
            await bot.send_message(message.from_user.id, "❇ Вы уже приняты 👍")
        else:
            if db.client_exists(message.from_user.id):
                await bot.send_message(message.from_user.id, "Вы уже подавали заявку ❌")
            else:
                await bot.send_message(message.from_user.id,
                                       "⭐️Добро пожаловать⭐️\n \n💫Прием заявок в MOONHAVEN💫 \n \n✅Подавай заявку✅",
                                       reply_markup=main_menu)
    else:
        await bot.send_message(message.from_user.id, "У вас не установлен <b>username</b>(имя пользователя)\n\nУстановите его и напишите /start", parse_mode=types.ParseMode.HTML)

async def send_state(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    action = callback_data["action"]
    current_state = await state.get_state()
    if current_state is None:
        return
    if action == "send":
        await bot.send_message(admin_id, f"Поступила новая заявка от @{str(db.get_user_data(call.from_user.id)[5])}\n"
                                         f"{admin_question_1}: <b>{str(db.get_user_data(call.from_user.id)[1])}</b>\n"
                                         f"{admin_question_2}: <b>{str(db.get_user_data(call.from_user.id)[2])}</b>\n"
                                         f"{admin_question_3}: <b>{str(db.get_user_data(call.from_user.id)[3])}</b>\n"
                                         f"{admin_question_4}: <b>{str(db.get_user_data(call.from_user.id)[4])}</b>", parse_mode=types.ParseMode.HTML, reply_markup=admin_menu(call.from_user.id))
        await bot.edit_message_text(chat_id=call.from_user.id, message_id=call.message.message_id, text="Заявка отправлена, ожидайте")
        await state.finish()
    if action == "application":
        db.delete_zayavka(call.from_user.id)
        await state.finish()
        await command_start(call)
    await call.answer()

async def access(call: types.CallbackQuery):
    temp = [call.data[1:2], call.data[2:]]
    if temp[0] == "y":
        db.add_client(temp[1])
        db.delete_zayavka(temp[1])
        await bot.edit_message_text(chat_id=admin_id, message_id=call.message.message_id, text="Вы приняли заявку✅")
        await bot.send_message(temp[1], f'Поздравляю, вы приняты в нашу команду ✅\n \n'
                                        f'🔖 Ссылка для вступления в чат: {chat_link} \n \n'
                                        f'❗ <b>ДОБРО ПОЖАЛОВАТЬ В ТИМУ ❗</b>', disable_web_page_preview=True, parse_mode=types.ParseMode.HTML)
    elif temp[0] == "n":
        await bot.edit_message_text(chat_id=admin_id, message_id=call.message.message_id, text="Вы отклонили заявку❌")
        await bot.send_message(temp[1], 'Извините, вы нам не подходите ❌')
    await call.answer()

async def start_state(call: types.CallbackQuery, callback_data: dict):
    action = callback_data["action"]
    if action == "start_answer":
        db.add_user(call.from_user.id, call.from_user.username)
        await bot.send_message(call.from_user.id, f"Ответьте на несколько вопросов:\n1) <b>{question_1}</b>", parse_mode=types.ParseMode.HTML)
        await get_answer.answer1.set()

async def answer1(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["answer1"] = message.text
    await bot.send_message(message.from_user.id, f'2) <b>{question_2}</b>', parse_mode=types.ParseMode.HTML)
    await get_answer.next()

async def answer2(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["answer2"] = message.text
    await bot.send_message(message.from_user.id, f'3) <b>{question_3}</b>', parse_mode=types.ParseMode.HTML)
    await get_answer.next()

async def answer3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["answer3"] = message.text
    await bot.send_message(message.from_user.id, f'4) <b>{question_4}</b>', parse_mode=types.ParseMode.HTML)
    await get_answer.next()

async def answer4(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["answer4"] = message.text
    await bot.send_message(message.from_user.id, f'Ответы на наши вопросы:\n\n'
                                                 f'1) <b>{data["answer1"]}</b>\n'
                                                 f'2) <b>{data["answer2"]}</b>\n'
                                                 f'3) <b>{data["answer3"]}</b>\n'
                                                 f'4) <b>{data["answer4"]}</b>', parse_mode=types.ParseMode.HTML, reply_markup=send_menu)
    db.update_user_data(message.from_user.id, data["answer1"], data["answer2"], data["answer3"], data["answer4"])

def register_handlers_client(dp: Dispatcher):
    dp.register_callback_query_handler(send_state, cb.filter(action=["send", "application"]), state="*")
    dp.register_message_handler(command_start, commands=["start"])
    dp.register_callback_query_handler(access, text_contains="#")
    dp.register_callback_query_handler(start_state, cb.filter(action=["start_answer"]))
    dp.register_message_handler(answer1, state=get_answer.answer1)
    dp.register_message_handler(answer2, state=get_answer.answer2)
    dp.register_message_handler(answer3, state=get_answer.answer3)
    dp.register_message_handler(answer4, state=get_answer.answer4)

register_handlers_client(dp)

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
