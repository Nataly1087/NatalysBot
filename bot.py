from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, MessageHandler, filters, CommandHandler

from credentials import*
from gpt import ChatGptService
from util import*


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = load_message('main')
    await send_image(update, context, 'main')
    await send_text(update, context, text)
    await show_main_menu(update, context, {
        'start': 'Главное меню',
        'random': 'Узнать случайный интересный факт 🧠',
        'gpt': 'Задать вопрос чату GPT 🤖',
        'talk': 'Поговорить с известной личностью 👤',
        'quiz': 'Поучаствовать в квизе ❓',
        'translator': 'Перевести текст 📖',
        'resume': 'Помощь с резюме 🧑‍🎓'
    })


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await send_text(update, context, 'Начнем сначала.')
    await start(update, context)


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'random'
    answer = await chat_gpt.send_question(load_prompt('random'), '')
    await send_text_buttons(update, context, answer, buttons={
        'random_more': 'Еще факт',
        'stop': 'Завершить'
    })


async def random_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await random(update, context)


async def gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'gpt'
    chat_gpt.set_prompt(load_prompt('gpt'))
    text = load_message('gpt')
    await send_image(update, context, 'gpt')
    await send_text(update, context, text)


async def gpt_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.message.text
    message = await send_text(update, context, 'Думаю над ответом...')
    answer = await chat_gpt.add_message(request)
    await message.delete()
    await message.send_text_buttons(update, context,
                                    answer,
                                    buttons={'stop': 'Завершить'})


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data['mode'] in ('main', 'random'):
        await start(update, context)
    elif context.user_data['mode'] == 'gpt':
        await gpt_dialog(update, context)


chat_gpt = ChatGptService('ChatGPT TOKEN')
app = Application.builder().token(token).build()


app.add_handler(MessageHandler(filters.TEXT & filters.COMMAND, text_handler))
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
#app.add_handler(CommandHandler('talk', talk))
#app.add_handler(CommandHandler('quiz', quiz))
#app.add_handler(CommandHandler('translator', translator))
#app.add_handler(CommandHandler('resume', resume))


# app.add_handler(CallbackQueryHandler(app_button, pattern='^app_.*'))
app.add_handler(CallbackQueryHandler(random_buttons, pattern='random_more'))
app.add_handler(CallbackQueryHandler(stop, pattern='stop'))
app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()