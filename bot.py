import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, File
from telegram.ext import  Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async
import ghandvis
import modes as m1

import random

TOKEN = 'there once was a token'


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


@run_async
def command_start(update, context):

    update.message.reply_text('Привет! Я BookAnalyzerBot ᕙ( ͡° ͜ʖ ͡°)ᕗ\nЯ умею визуализировать связи персонажей и не только!')

    update.message.reply_text('Если вас интересует\n\n☆ анализ связей конкретных персонажей\n--- нажмите /analyze_characters\n\n'
        '☆ поиск всех персонажей\n--- нажмите /all_characters\n\n'
        '☆ частотность имен собственных по главам / томам / частям\n--- нажмите /frequency',
    )



def function_name(update, context):
    global waiting_for_response
    if waiting_for_response:
        pass


# mode1

FILENAME, DELIMITER, MIN_WEIGHT, WORKLIST_1 = range(4)

filename = ''
abzinfo = ''
min_weight = 0
worklist_1 = ''


def start_cmd(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Пришлите мне файл с текстом произведения\nв формате .txt и кодировке UTF-8")
    return FILENAME

def mode1_getfile(update, context):
    chat_id = update.message.chat_id

    global filename
    filename = 'newfile'+str(chat_id)+ '.txt'
    f = open(filename, 'wb')
    context.bot.get_file(update.message.document).download(out=f)
    f.close()

    reply_keyboard = [['отступ', 'пустая строка']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(
        'Хорошо! А чем в тексте разделяются абзацы?\n\n'
        'Доступные варианты ответа: отступ, пустая строка',
        reply_markup=markup_key,
    )
    return DELIMITER

def mode1_delimiter(update, context):
    chat_id = update.message.chat_id

    global delimiter
    if update.message.text == 'отступ':
        delimiter = '\t'
    else:
        delimiter = '\n\n'

    update.message.reply_text(
        'Введите минимальный вес связи между персонажами\n'
        '(вес связи равен количеству взаимодействий между героями)'
    )
    return MIN_WEIGHT

def mode1_weight(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user

    global min_weight
    min_weight = int(update.message.text)

    update.message.reply_text('Введите интересующих вас персонажей через пробел')
    return WORKLIST_1

def mode1_chrtrs(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user

    global worklist_1
    worklist_1 =  update.message.text
    update.message.reply_text('Принял! Теперь нужно немного подождать')
    writecsv1 = m1.mode1(filename, delimiter, min_weight, worklist_1)

    f = open(writecsv1, 'rb')
    link2gh = ghandvis.ghvis(f)
    context.bot.send_document(chat_id=chat_id, document=open(writecsv1,'rb'), caption='Вот csv-файл со статистикой взаимодействий!')

    update.message.reply_text('И вот ссылка, перейдя по которой, Вы увидите граф: ' + link2gh)
    f.close()
    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text(
        'Мое дело предложить - Ваше отказаться\n'
        'Будет скучно - пиши!',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


# mode2

FILENAME_2, DELIMITER_2, FREQUENCY, WORKLIST_2, MIN_WEIGHT_2 = range(5)

def start_cmd_2(update, context):
        chat_id = update.message.chat_id
        context.bot.send_message(chat_id=chat_id, text="Пришлите мне файл с текстом произведения\nв формате .txt и кодировке UTF-8")
        return FILENAME_2

def mode2_getfile(update, context):
    chat_id = update.message.chat_id
    global filename2
    filename2 = 'newfile'+str(chat_id)+ '.txt'
    f = open(filename2, 'wb')
    context.bot.get_file(update.message.document).download(out=f)
    f.close()

    reply_keyboard = [['отступ', 'пустая строка']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(
        'Хорошо! А чем в тексте разделяются абзацы?\n\n'
        'Доступные варианты ответа: отступ, пустая строка',
        reply_markup=markup_key,
    )
    return DELIMITER_2

def mode2_delimiter(update, context):
    chat_id = update.message.chat_id

    global delimiter_2
    if update.message.text == 'отступ':
        delimiter_2 = '\t'
    else:
        delimiter_2 = '\n\n'

    update.message.reply_text('С какой минимальной частотой должны встречаться персонажи?')
    return FREQUENCY

def mode2_min_frequency(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user

    global frequency
    frequency = int(update.message.text)

    update.message.reply_text('Ок! Подождите пару минут, я выведу всех персонажей')
    global totallist
    totallist = m1.mode2_1(filename2, delimiter_2, frequency)
    update.message.reply_text('Вот все персонажи, по моему мнению:')
    msg = totallist[2]
    if len(msg) > 4096:
        for x in range(0, len(msg), 4096):
            update.message.reply_text(msg[x:x+4096])
    else:
        update.message.reply_text(msg)

    update.message.reply_text('Введите имена героев, которые Вас интересуют, через пробел.\n\n'
        'Если разные имена в списке - варианты имени одного персонажа, то введите их через \'_\'\n\n'
        'Первым впишите то имя, которое хотите видеть на графе'
    )
    return WORKLIST_2

def mode2_chrtrs(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user

    global worklist_2
    worklist_2 =  update.message.text
    
    update.message.reply_text(
        'Введите минимальный вес связи между персонажами\n'
        '(вес связи равен количеству взаимодействий между героями)'
    )
    return MIN_WEIGHT_2
    
def mode2_min_weight(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user

    global min_weight_2
    min_weight_2 = int(update.message.text)
    
    update.message.reply_text('Принял! Теперь нужно немного подождать')
    writecsv2 = m1.mode2_2(worklist_2, totallist[0], totallist[1], filename2, min_weight_2)
    f = open(writecsv2, 'rb')
    link2gh = ghandvis.ghvis(f)
    f.close()
    context.bot.send_document(chat_id=chat_id, document=open(writecsv2,'rb'), caption='Вот csv-файл со статистикой взаимодействий!')
    update.message.reply_text('И вот ссылка, перейдя по которой, Вы увидите граф: ' + link2gh)
    
    return ConversationHandler.END

# mode3

FILENAME_3, DELIMITER_3, CHRTR_NUM, CONT = range(4)

filename_3 = ''
delimiter_3 = ''
num = 0
cont = False

def start_cmd_3(update, context):
    chat_id = update.message.chat_id
    context.bot.send_message(chat_id=chat_id, text="Пришлите мне файл с текстом произведения\nв формате .txt и кодировке UTF-8")
    return FILENAME_3

def mode3_getfile(update, context):
    chat_id = update.message.chat_id

    global filename_3
    filename_3 = 'newfile'+str(chat_id)+ '.txt'
    f = open(filename_3, 'wb')
    context.bot.get_file(update.message.document).download(out=f)
    f.close()

    update.message.reply_text(
        'Хорошо! А чем разделены отрывки текста, по которым \nбудет производиться поиск?\n\n'
        '☆ Если пустой строкой --- введите "строка"\n\n'
        '☆ Если словом --- введите слово (ex. "Page" или "CHAPTER"), как оно указано в тексте',
    )
    return DELIMITER_3

def mode3_delimiter(update, context):
    chat_id = update.message.chat_id

    global delimiter_3
    delimiter_3 = update.message.text
    if "строка" in delimiter_3:
        delimiter_3 = '\n\n'

    update.message.reply_text('Какое количество имен мне вывести для каждого отрывка?')
    return CHRTR_NUM

def mode3_num(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user

    global num
    num = int(update.message.text)

    reply_keyboard = [['да', 'нет']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True)
    update.message.reply_text(
        'Учту! И последний вопрос: хотите ли Вы, чтобы\nя предположил, кто является главным героем?\n\n'
        'Доступные варианты ответа: да, нет',
        reply_markup=markup_key,
    )
    return CONT

def mode3_cont(update, context):
    chat_id = update.message.chat_id
    user = update.message.from_user
    global cont
    if update.message.text == 'да':
        cont = True
    update.message.reply_text('Принял! Теперь нужно немного подождать')
    writecsv3 = m1.mode3(filename_3, delimiter_3, num, cont)
    f = open(writecsv3[0], 'rb')
    context.bot.send_document(chat_id=chat_id, document=f, caption='Вот файл с результатами!')
    f.close()
    if cont == True:
        update.message.reply_text('Главный герой: '+writecsv3[1])
    return ConversationHandler.END



@run_async
def help_command(update, context):
    update.message.reply_text(
        'Чтобы запустить бота, напишите /start\n'
        'Чтобы прекратить работу бота, напишите /cancel'
    )

@run_async
def ans(update, context):
    message = 'Я вроде бы должен выдать что-то осмысленное, но ничего не понял :с\n Попробуйте /start или /help'
    update.message.reply_text(message)


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    conv_handler1 = ConversationHandler(
        entry_points=[CommandHandler('analyze_characters', start_cmd)],
        states={
            FILENAME: [MessageHandler(Filters.document, mode1_getfile)],
            DELIMITER: [MessageHandler(Filters.regex('^(отступ|пустая строка)$'), mode1_delimiter)],
            MIN_WEIGHT: [MessageHandler(Filters.text, mode1_weight)],
            WORKLIST_1: [MessageHandler(Filters.text, mode1_chrtrs)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )


    conv_handler2 = ConversationHandler(
        entry_points=[CommandHandler('all_characters', start_cmd_2)],
        states={
            FILENAME_2: [MessageHandler(Filters.document, mode2_getfile)],
            DELIMITER_2: [MessageHandler(Filters.regex('^(отступ|пустая строка)$'), mode2_delimiter)],
            FREQUENCY: [MessageHandler(Filters.text, mode2_min_frequency)],
            WORKLIST_2: [MessageHandler(Filters.text, mode2_chrtrs)],
            MIN_WEIGHT_2: [MessageHandler(Filters.text, mode2_min_weight)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )


    conv_handler3 = ConversationHandler(
        entry_points=[CommandHandler('frequency', start_cmd_3)],
        states={
            FILENAME_3: [MessageHandler(Filters.document,mode3_getfile)],
            DELIMITER_3: [MessageHandler(Filters.text, mode3_delimiter)],
            CHRTR_NUM: [MessageHandler(Filters.text, mode3_num)],
            CONT: [MessageHandler(Filters.regex('^(да|нет)$'), mode3_cont)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )


    dp.add_handler(CommandHandler('start', command_start))
    dp.add_handler(CommandHandler('help', help_command))

    dp.add_handler(conv_handler1)
    dp.add_handler(conv_handler2)
    dp.add_handler(conv_handler3)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
