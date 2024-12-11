from lazy_object_proxy.utils import await_
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes, MessageHandler, filters, CommandHandler


from credentials import*
from gpt import ChatGptService
from util import*


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'main'
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
    await send_text(update, context, 'Без проблем! Начнем сначала.')
    await start(update, context)


async def random(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'random'
    await send_image(update, context, 'random')
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
    await send_text_buttons(update, context,
                                    answer,
                                    buttons={'stop': 'Завершить'})


async def talk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'talk'
    text = load_message('talk')
    await send_image(update, context, 'talk')
    await send_text_buttons(update, context, text, {
        'talk_cobain': 'Курт Кобейн - Солист группы Nirvana 🎸',
        'talk_hawking': 'Стивен Хокинг - Физик 🔬',
        'talk_nietzsche': 'Фридрих Ницше - Философ 🧠',
        'talk_queen': 'Елизавета II - Королева Британии👑',
        'talk_tolkien': 'Джон Толкиен - Автор "Властелина Колец" 📖',
        'talk_monroe': 'Мэрэлин Монро - Секс-символ 1950-х годов 👸',
        'talk_bulgakov': 'Михаил Булгаков -  Писатель, драматург 📚',
        'talk_gogol': 'Николай Гоголь - Классик русской литературы 🕯',
        'talk_kleopatra': 'Клеопатра - Последняя царица Египта 🛕',
        'talk_mask': 'Илон Маск - Основатель компании SpaceX 🦾',
        'talk_rasputin': 'Григорий Распутин - «Царский друг» 🔮'
    })


async def talk_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    chat_gpt.set_prompt(load_prompt(data))
    greet = await chat_gpt.add_message('Поздоровайся со мной')
    await send_image(update, context, data)
    await send_text(update, context, greet)


async def talk_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.message.text
    message = await send_text(update, context, 'Уже пишу тебе ответ. А ты пока устраивайся поудобнее.')
    answer = await chat_gpt.add_message(request)
    await message.delete()
    await send_text_buttons(update, context,
                            answer,
                            buttons={'stop': 'Завершить'})


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'quiz'
    context.user_data['score'] = 0
    chat_gpt.set_prompt(load_prompt('quiz'))
    await send_image(update, context, 'quiz')
    await send_text_buttons(update, context, 'Выберите тему: ', {'quiz_prog': 'Программирование',
                                                                'quiz_art': 'Искусство',
                                                                'quiz_literature': 'Литература',
                                                                 'quiz_music': 'Музыка',
                                                                 'quiz_fashion': 'Мода'
                                                                })


async def quiz_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query.data == 'quiz_change':
        await update.callback_query.answer()
        await quiz(update, context)
    else:
        await update.callback_query.answer()
        question = await chat_gpt.add_message(update.callback_query.data)
        await send_text(update, context, question)


async def quiz_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    answer = await chat_gpt.add_message(text)
    if answer == 'Правильно!':
        context.user_data['score'] = context.user_data.get('score', 0) + 1
    await send_text_buttons(update, context, answer + '\n\nВаш счет: ' + str(
        context.user_data['score']), {'quiz_more': 'Следующий вопрос',
                                              'quiz_change': 'Выбрать другую тему',
                                              'stop': 'Завершить'
                                              })


async def translator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'translator'
    text = load_message('translator')
    await send_image(update, context, 'translator')
    await send_text_buttons(update, context, text, {
        'translator_English': 'Английский 🇬🇧',
        'translator_German': 'Немецкий 🇩🇪',
        'translator_Turkish': 'Турецкий 🇹🇷',
        'translator_French': 'Французский 🇨🇵',
        'translator_Chinese': 'Китайский 🇨🇳',
        'translator_Japanese': 'Японский 🇯🇵',
        'translator_Korean': 'Корейский 🇰🇷'
    })


async def translator_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    data = update.callback_query.data
    chat_gpt.set_prompt(load_prompt(data))
    await translator_dialog(update, context)


async def translator_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.message.text
    message = await send_text(update, context, 'Уже перевожу, пожалуйста, подождите минутку.')
    answer = await chat_gpt.add_message(request)
    await message.delete()
    await send_text_buttons(update, context,
                            answer,
                            buttons={'stop': 'Завершить'})


async def resume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['mode'] = 'resume'
    text = load_message('resume')
    chat_gpt.set_prompt(load_prompt('resume'))
    await send_image(update, context, 'resume')
    await send_text(update, context, text)


async def resume_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.message.text
    message = await send_text(update, context, 'Буквально пару минут и ваше резюме будет готово.')
    answer = await chat_gpt.add_message(request)
    await message.delete()
    await send_text_buttons(update, context,
                            answer,
                            buttons={'stop': 'Завершить'})


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data['mode'] in ('main', 'random'):
        await start(update, context)
    elif context.user_data['mode'] == 'gpt':
        await gpt_dialog(update, context)
    elif context.user_data['mode'] == 'talk':
        await talk_dialog(update, context)
    elif context.user_data['mode'] == 'quiz':
        await quiz_dialog(update, context)
    elif context.user_data['mode'] == 'translator':
        await translator_dialog(update, context)
    elif context.user_data['mode'] == 'resume':
        await resume_dialog(update, context)


chat_gpt = ChatGptService(ChatGPT_TOKEN)
app = Application.builder().token(token).build()


app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('random', random))
app.add_handler(CommandHandler('gpt', gpt))
app.add_handler(CommandHandler('talk', talk))
app.add_handler(CommandHandler('quiz', quiz))
app.add_handler(CommandHandler('translator', translator))
app.add_handler(CommandHandler('resume', resume))


app.add_handler(CallbackQueryHandler(random_buttons, pattern='random_more'))
app.add_handler(CallbackQueryHandler(talk_buttons, pattern='^talk_.*'))
app.add_handler(CallbackQueryHandler(quiz_buttons, pattern='^quiz_.*'))
app.add_handler(CallbackQueryHandler(translator_buttons, pattern='^translator_.*'))
app.add_handler(CallbackQueryHandler(stop, pattern='stop'))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))


app.add_handler(CallbackQueryHandler(default_callback_handler))
app.run_polling()