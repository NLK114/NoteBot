import telebot
from telebot import types
TOKEN = "7974762563:AAFwGERoN8fhidsvTWbsK3-sWLhlf2lJXLQ"
bot = telebot.TeleBot(TOKEN)
notes = []
user_state = {}
temp_note = {}

@bot.message_handler(commands=["start"])
def start(message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Создать заметку", callback_data="new_note"))
    kb.add(types.InlineKeyboardButton("Список заметок", callback_data="list_notes"))
    kb.add(types.InlineKeyboardButton("Удалить заметку", callback_data="delete"))
    kb.add(types.InlineKeyboardButton("Помощь", callback_data="help"))

    bot.send_message(message.chat.id, "Привет! Выбери действие:", reply_markup=kb)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "new_note":
        bot.answer_callback_query(call.id)
        user_state[call.from_user.id] = "waiting_title"
        bot.send_message(call.message.chat.id,
                         "Введите *заголовок* заметки:",
                         parse_mode="Markdown")

    elif call.data == "list_notes":
        bot.answer_callback_query(call.id)
        if not notes:
            bot.send_message(call.message.chat.id, "Список заметок пуст.")
            return

        text = "*Ваши заметки:*\n\n"
        for i, note in enumerate(notes, start=1):
            text += f"{i}. *{note['title']}*\n{note['content']}\n\n"

        bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

    elif call.data == "delete":
        bot.answer_callback_query(call.id)
        if not notes:
            bot.send_message(call.message.chat.id, "Удалять нечего, список заметок пуст.")
            return

        kb = types.InlineKeyboardMarkup()
        for i, n in enumerate(notes):
            kb.add(types.InlineKeyboardButton(f"Удалить: {n['title']}", callback_data=f"del_{i}"))

        bot.send_message(call.message.chat.id, "Выберите заметку для удаления:", reply_markup=kb)

    elif call.data.startswith("del_"):
        index = int(call.data.split("_")[1])

        if 0 <= index < len(notes):
            deleted_title = notes[index]["title"]
            del notes[index]
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, f"Заметка *{deleted_title}* удалена!", parse_mode="Markdown")
        else:
            bot.send_message(call.message.chat.id, "Ошибка: такой заметки не существует.")

    elif call.data == "help":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Этот бот создаёт, показывает и удаляет заметки.")

@bot.message_handler(func=lambda message: True)
def text_handler(message):
    uid = message.from_user.id

    if user_state.get(uid) == "waiting_title":
        temp_note[uid] = {"title": message.text}
        user_state[uid] = "waiting_content"
        bot.send_message(message.chat.id,
                         "Теперь введите *текст заметки*:",
                         parse_mode="Markdown")
        return

    if user_state.get(uid) == "waiting_content":
        temp_note[uid]["content"] = message.text
        notes.append(temp_note[uid])
        bot.send_message(message.chat.id, "Заметка сохранена!")

        user_state.pop(uid)
        temp_note.pop(uid)
        return

    start(message)
print("a")
bot.polling()