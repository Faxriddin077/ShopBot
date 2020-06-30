from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, ChatAction
import telebot
from datetime import datetime, timedelta
from backend import buttons, Customers, Tovar, Razmer, Savatcha, Order, Admins, check_admin, show_razmer, sticker_crud
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler
import sqlite3
import requests
from telegraph import Telegraph

global step
bot = telebot.TeleBot('1218844571:AAHesAbLwlqKFkAUMkq2vJ5buLH3xwZqHXo')
customer_data = dict()
admin_tovar = dict()


def action(update, context):
    context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)



def reader():
    with open('step.txt', 'r') as fayl:
        step = fayl.read()
    return step


def writer(text):
    with open('step.txt', 'w') as fayl:
        fayl.write(text)


def appender(text):
    with open('step.txt', 'a') as fayl:
        fayl.write(text + "\n")


def user_xarid(id):
    obyekt = Customers()
    xarid_status = obyekt.select_user_xarid(str(id))
    if xarid_status[0] == "Optom":
        xarid_status = "optom_sum"
    else:
        xarid_status = "dona_sum"
    return xarid_status


TOGETHER = 77

STATE_FISH = 1.1
STATE_NUMBER = 1.2
STATE_LOCATION = 1.3
STATE_CARD = 1.4
STATE_XARID = 1.5
STATE_MENYU = 2
STATE_USER = 2.1
STATE_USER2 = 2.2
STATE_USER3 = 2.3
STATE_SAVDO = 3
STATE_FASL = 3.1
STATE_RAZMER = 3.2
STATE_TOVAR_RAZMER = 3.3
STATE_TOVAR_TANLASH = 3.4
STATE_TOVAR_SAVATCHA = 3.5

STATE_SAVAT_LOCATION = 3.8
STATE_SAVATCHA = 3.9
STATE_TOLOV_TURI = 4
STATE_TURI_TOLOV = 4.1
STATE_BASKET_TOLOV = 4.2
STATE_TOLOV_ORDER = 4.3
STATE_BUYURTMA = 5

ADMIN_MENYU = 10
ADMIN_TOVAR = 10.1
ADMIN_FASL = 11.1
TOVAR_RAZMER = 11.2
TOVAR_CRUD = 11.3
ADD_TOVAR = 113.1
ADD_TOVAR_NARX = 113.3
DEL_TOVAR = 113.2
ADMIN_BUYURTMA = 10.2
ADMIN_BUYURTMA_CONTROL = 102.1
ADMIN_TOVAR_STATUS = 10.3
ADMIN_RAZMER = 10.4
RAZMER_CRUD = 13
ADD_RAZMER = 13.1
DEL_RAZMER = 13.2

ADMIN_CRUD = 0.1
ADD_ADMIN = 0.2
DEL_ADMIN = 0.3

super_admin = '590924106'


def start(update, context):
    chat_id = str(update.message.from_user.id)
    if chat_id == super_admin:
        admin_tovar.update({chat_id: {'tovar': dict()}})
        update.message.reply_text("Ассалому алейкум {}.".format(update.message.from_user.first_name), reply_markup=super_menyu)
        return ADMIN_MENYU
    elif check_admin(chat_id):
        admin_tovar.update({chat_id: {'tovar': dict()}})
        update.message.reply_text("Ассалому алейкум {}.".format(update.message.from_user.first_name), reply_markup=admin_menyu)
        return ADMIN_MENYU
    else:
        customer_data.update({chat_id: {'register': dict()}})
        update.message.reply_text("Ассалому алейкум {}. Ботдан фойдаланиш учун рўйхатдан ўтишингиз зарур."
                                  " \nФ. И. Ш ни киритинг.".format(update.message.from_user.first_name),
                                  reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
        return STATE_FISH


def f_i_sh(update, context):
    chat_id = str(update.message.from_user.id)
    fish = update.message.text
    test = fish.split(' ')
    customer_data[chat_id]['register'].update({'name': fish})
    contact_keyboard = KeyboardButton(text="phone", request_contact=True, resize_keyboard=True)
    reply_markup = ReplyKeyboardMarkup([[contact_keyboard]], resize_keyboard=True)
    update.message.reply_text('Энди телефон рақамингизни юборинг. Бунинг учун тугмачани босинг.', reply_markup=reply_markup)
    return STATE_NUMBER


def number(update, context):
    chat_id = str(update.message.from_user.id)
    contact = update.message.contact.phone_number
    customer_data[chat_id]['register'].update({'contact': contact})
    location_keyboard = KeyboardButton(text="location", request_location=True, resize_keyboard=True)
    reply_markup = ReplyKeyboardMarkup([[location_keyboard], ["Keyinroq yuborish"]], resize_keyboard=True)
    update.message.reply_text('Энди манзилингизни юборинг. Бунинг учун тугмачани босинг.', reply_markup=reply_markup)
    return STATE_LOCATION


def location(update, context):
    chat_id = str(update.message.from_user.id)
    locate = update.message.location
    customer_data[chat_id]['register'].update({'longitude': str(locate.longitude)})
    customer_data[chat_id]['register'].update({'latitude': str(locate.latitude)})
    update.message.reply_text("Тўлов қиладиган карта рақамингизни юборинг. (UZCARD, HUMO ва ҳ.к)",
                              reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
    return STATE_CARD


def keyinroq(update, context):
    update.message.reply_text("Тўлов қиладиган карта рақамингизни юборинг. (UZCARD, HUMO ва ҳ.к)",
                              reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
    return STATE_CARD


def card(update, context):
    chat_id = str(update.message.from_user.id)
    karta = update.message.text
    if len(karta) == 16:
        if not karta.isdigit():
            update.message.reply_text("Карта рақамни тўғри киритинг!")
            return STATE_CARD
        customer_data[chat_id]['register'].update({'card_number': karta})
        update.message.reply_text("Қайси йўналиш бўйича савдо қилишингизни танланг.",
                                  reply_markup=ReplyKeyboardMarkup([["Оптом", "Donaga"]], resize_keyboard=True))
    else:
        update.message.reply_text("Карта рақамни тўғри киритинг!")
        return STATE_CARD
    return STATE_XARID


def xarid(update, context):
    chat_id = str(update.message.from_user.id)
    xarid = update.message.text
    customer_data[chat_id]['register'].update({'xarid_status': xarid})
    # Bazaga yozish
    print(customer_data[chat_id]['register'])
    try:
        connect = sqlite3.connect("baza.db", check_same_thread=True)
        cursor = connect.cursor()
        sqlite_insert_query = "insert into customers (chat_id, name, contact, card_number, xarid_status) values " \
                              "('" + chat_id + "', '" + customer_data[chat_id]['register']['name'] + "', '" + customer_data[chat_id]['register'][
                                  'contact'] + "'," \
                                               " '" + customer_data[chat_id]['register']['card_number'] + "', '" + customer_data[chat_id]['register'][
                                  'xarid_status'] + "')"
        cursor.execute(sqlite_insert_query)
        connect.commit()
        if customer_data[chat_id]['register'].get('longitude'):
            query = "update customers set longitude='" + customer_data[chat_id]['register']['longitude'] + "'," \
                                                                                                           " latitude='" + \
                    customer_data[chat_id]['register']['latitude'] + "' where chat_id='" + chat_id + "'"
            cursor.execute(query)
            connect.commit()
    except Exception as e:
        print("error ", str(e))
    del customer_data[chat_id]['register']
    customer_data.update({chat_id: {'savdo': dict()}})
    print("Iwladi: \n", customer_data)
    update.message.reply_text("Рўйхатдан муваффақиятли ўтдингиз. Менюлардан фойдаланишингиз мумкин.", reply_markup=customer_menyu)
    return STATE_MENYU


def menyu(update, context):
    chat_id = str(update.message.from_user.id)
    if check_admin(chat_id):
        update.message.reply_text("Aсосий менюга қайтдингиз.", reply_markup=admin_menyu)
        return ADMIN_MENYU
    elif chat_id == super_admin:
        update.message.reply_text("Aсосий менюга қайтдингиз.", reply_markup=super_menyu)
        return ADMIN_MENYU
    else:
        update.message.reply_text("Aсосий меню:", reply_markup=customer_menyu)
        return STATE_MENYU


def savdo(update, context):
    update.message.reply_text("Фаслни танланг.",
                              reply_markup=ReplyKeyboardMarkup([
                                  ['Қиш', "Ёз"], ["Куз-баҳор"], ["Орқага"]
                              ], resize_keyboard=True))
    return STATE_SAVDO


def fasl(update, context):
    chat_id = str(update.message.from_user.id)
    season = update.message.text.lower()
    if check_admin(chat_id) or chat_id == super_admin:
        update.message.reply_text("Ўлчам турларидан бирини танланг.", reply_markup=razmer_category)
        return ADMIN_RAZMER
    else:
        customer_data[chat_id]['savdo'].update({'season': season})
        update.message.reply_text("Қайси тур ўлчамдан харид қилишингизни танланг.", reply_markup=razmer_category)
        return STATE_RAZMER


def razmer(update, context):
    chat_id = str(update.message.from_user.id)
    turi = update.message.text.lower()
    print(turi)
    if turi == "турк ўлчамлар":
        turi = "туркий"
    button = show_razmer(turi)
    if check_admin(chat_id) or chat_id == super_admin:
        if admin_tovar[chat_id]['tovar']['status'] == 'янги товар қўшиш':
            update.message.reply_text("Қўшиш усулини танланг", reply_markup=ReplyKeyboardMarkup([['Оптом', 'Дона']]))
            return ADMIN_TOVAR_STATUS
        else:
            update.message.reply_text("Ўлчамлар:", reply_markup=ReplyKeyboardMarkup([["Менюга қайтиш"]], resize_keyboard=True))
            obyekt = Razmer()
            razmerlar = obyekt.select_razmer(turi)
            admin_tovar[chat_id]['tovar']['add_stiker'] = {}
            for x in razmerlar:
                admin_tovar[chat_id]['tovar']['add_stiker'].update({x['razmer']: '0'})
            admin_tovar[chat_id]['tovar']['category'] = turi
            button.append([InlineKeyboardButton("Маҳсулот қўшиш", callback_data='addtovar')])
            update.message.reply_text("Керакли ўлчамингизни танланг.", reply_markup=InlineKeyboardMarkup(button))
            return TOGETHER
    else:
        update.message.reply_text("Керакли ўлчамингизни танланг.", reply_markup=InlineKeyboardMarkup(button))
        customer_data[chat_id]['savdo'].update({'category': turi})
        return STATE_TOVAR_RAZMER


def together(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    if callback.data == 'addtovar':
        if not [1 for y in admin_tovar[chat_id]['tovar']['add_stiker'].values() if y == '1']:
            print("aa")
        else:
            print("aa", admin_tovar[chat_id]['tovar']['add_stiker'])
            admin_tovar[chat_id]['tovar']['razmeri'] = []
            for x, y in admin_tovar[chat_id]['tovar']['add_stiker'].items():
                if y == '1':
                    admin_tovar[chat_id]['tovar']['razmeri'].append(x)
            nomlar = buttons(admin_tovar[chat_id]['tovar']['season'])
            callback.edit_message_text(text="Маҳсулот турларидан бирини танланг:", reply_markup=InlineKeyboardMarkup(nomlar))
            return TOVAR_CRUD
    else:
        royxat = admin_tovar[chat_id]['tovar']
        if royxat['add_stiker'][callback.data] == '0':
            royxat['add_stiker'][callback.data] = '1'
        else:
            royxat['add_stiker'][callback.data] = '0'
        knopka = sticker_crud(royxat['category'], royxat['add_stiker'])
        print(royxat['add_stiker'])
        callback.edit_message_text("Керакли ўлчамингизни танланг.", reply_markup=InlineKeyboardMarkup(knopka))


def select_mahsulot_nomi(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    if check_admin(chat_id) or chat_id == super_admin:
        print("qqq")
        admin_tovar[chat_id]['tovar']['razmeri'] = []
        for x, y in admin_tovar[chat_id]['tovar']['add_stiker'].items():
            if y == '1':
                admin_tovar[chat_id]['tovar']['razmeri'].append(x)
        nomlar = buttons(admin_tovar[chat_id]['tovar']['season'])
        callback.edit_message_text(text="Маҳсулот турларидан бирини танланг:", reply_markup=InlineKeyboardMarkup(nomlar))
        return TOVAR_CRUD
    else:
        nomlar = buttons(customer_data[chat_id]['savdo']['season'])
        callback.edit_message_text(text="Маҳсулот турларидан бирини танланг:", reply_markup=InlineKeyboardMarkup(nomlar))
        customer_data[chat_id]['savdo'].update({'razmeri': callback.data})
        return STATE_TOVAR_TANLASH


def tovar_tanlash(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    xarid_status = user_xarid(chat_id)
    customer_data[chat_id]['savdo'].update({'nomi': callback.data})
    customer_data[chat_id]['savdo'].update({'xarid_status': xarid_status})
    obyekt_tovar = Tovar()
    tovar_data = obyekt_tovar.select_tovar_user(xarid_status, customer_data[chat_id]['savdo']['nomi'], customer_data[chat_id]['savdo']['season'],
                                                customer_data[chat_id]['savdo']['category'], customer_data[chat_id]['savdo']['razmeri'])
    print(tovar_data)
    print(customer_data)
    callback.message.reply_text("Хозир мавжуд маҳсулотлар:")
    try:
        for data in tovar_data:
            context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
            context.bot.send_photo(chat_id=chat_id, photo=open(data[0], 'rb'))
            callback.message.reply_text("Маҳсулот нархи: " + str(data[1]) + " сўм", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Саватчага ташлаш", callback_data=data[2])]
            ]))
    except Exception as e:
        print(str(e))
    return STATE_TOVAR_SAVATCHA


def tovarTOsavat(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    print(callback.data, type(callback.data))
    obyekt = Savatcha()
    try:
        obyekt.insert_savat(chat_id, str(callback.data))
        callback.edit_message_text("Саватчага ташланди.")
    except Exception as e:
        print(str(e))


def user(update, context):
    update.message.reply_text("Бу ерда маълумотларингизни кўришингиз мумкин.",
                              reply_markup=customer_malumotlari)
    return STATE_USER


def userData(update, context):
    chat_id = str(update.message.from_user.id)
    customer_data[chat_id].update({'user_data': dict()})
    print(customer_data[chat_id])
    connect = sqlite3.connect("baza.db", check_same_thread=True)
    cursor = connect.cursor()
    query = None
    if update.message.text == "Ф. И. Ш":
        text = "Сизнинг исмингиз: "
        query = "select name from customers where chat_id='" + chat_id + "'"
        customer_data[chat_id]['user_data'].update({'step': 'name'})
    elif update.message.text == "Telefon raqam":
        text = "Сизнинг телефон рақамингиз: "
        query = "select contact from customers where chat_id='" + chat_id + "'"
        customer_data[chat_id]['user_data'].update({'step': 'contact'})
    elif update.message.text == "Manzil":
        text = "Сизнинг манзилингиз:"
        data = cursor.execute("select longitude, latitude from customers where chat_id='" + chat_id + "'").fetchall()[0]
        update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup([["Ўзгартириш"], ["Орқага"]], resize_keyboard=True))
        context.bot.send_location(chat_id=chat_id, longitude=data[0], latitude=data[1])
        customer_data[chat_id]['user_data'].update({'step': 'adres'})
    else:
        text = "Сизнинг карта рақамингиз: "
        query = "select card_number from customers where chat_id='" + chat_id + "'"
        customer_data[chat_id]['user_data'].update({'step': 'card_number'})

    if not text == "Сизнинг манзилингиз:":
        try:
            data = cursor.execute(query).fetchone()[0]
            update.message.reply_text(text + str(data), reply_markup=ReplyKeyboardMarkup([
                ["Ўзгартириш"], ["Орқага"]
            ], resize_keyboard=True))
        except Exception as e:
            print(str(e))
    return STATE_USER2


def change(update, context):
    chat_id = str(update.message.from_user.id)
    step = customer_data[chat_id]['user_data']['step']
    print(step)
    if step == "name":
        update.message.reply_text("Ўзгартирмоқчи бўлган исмингизни киритинг.", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
    elif step == "contact":
        location_keyboard = KeyboardButton(text="phone", request_contact=True, resize_keyboard=True)
        phone = ReplyKeyboardMarkup([[location_keyboard]], resize_keyboard=True)
        update.message.reply_text("Ўзгартирмоқчи бўлган телефон рақамингизни юборинг. Бунинг учун тугмачани босинг.", reply_markup=phone)
    elif step == "card_number":
        update.message.reply_text("Ўзгартирмоқчи бўлган карта рақамингизни киритинг.", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
    else:
        location_keyboard = KeyboardButton(text="location", request_location=True, resize_keyboard=True)
        reply_markup = ReplyKeyboardMarkup([[location_keyboard]], resize_keyboard=True)
        update.message.reply_text("Ўзгартирмоқчи бўлган манзилингизни юборинг. Бунинг учун тугмачани босинг.", reply_markup=reply_markup)
    return STATE_USER3


def change_user_data(update, context):
    chat_id = str(update.message.from_user.id)
    step = customer_data[chat_id]['user_data']['step']
    if step == "name" or step == "card_number":
        obyekt = Customers()
        print('aaa', step)
        data = update.message.text
        print(step + " " + data)
        obyekt.user_data_update(step, data, chat_id)
        update.message.reply_text("Маълумотингиз янгиланди.",
                                  reply_markup=customer_malumotlari)
        return STATE_USER


def change_user_phone(update, context):
    print("conassss")
    try:
        chat_id = str(update.message.from_user.id)
        obyekt = Customers()
        phone = update.message.contact.phone_number
        obyekt.user_data_update('contact', phone, chat_id)
    except Exception as e:
        print(str(e))
    update.message.reply_text("Телефон рақамингиз янгиланди. Маълумотларингиз:",
                              reply_markup=customer_malumotlari)
    return STATE_USER


def change_user_locate(update, context):
    chat_id = str(update.message.from_user.id)
    obyekt = Customers()
    locate = update.message.location
    try:
        longi = locate.longitude
        lati = locate.latitude
        obyekt.user_data_update('longitude', str(longi), chat_id)
        obyekt.user_data_update('latitude', str(lati), chat_id)
    except Exception as e:
        print("aa11", str(e))
    update.message.reply_text("Манзилингиз янгиланди.  Маълумотларингиз:",
                              reply_markup=customer_malumotlari)
    return STATE_USER


def savatcha(update, context):
    chat_id = str(update.message.from_user.id)
    ob = Customers()
    manzil = ob.select_location(chat_id)
    if not manzil[0][0]:
        location_keyboard = KeyboardButton(text="location", request_location=True, resize_keyboard=True)
        reply_markup = ReplyKeyboardMarkup([[location_keyboard], ["Орқага"]], resize_keyboard=True)
        update.message.reply_text('Манзилингиз киритилмаган. Юбориш учун тугмачани босинг.', reply_markup=reply_markup)
        return STATE_SAVAT_LOCATION
    else:
        xarid_s = user_xarid(chat_id)
        obyekt = Savatcha()
        tovar_data = obyekt.select_tovar(str(chat_id), xarid_s)
        print(xarid_s)
        print(tovar_data)
        update.message.reply_text("Сиз танлаган маҳсулотлар:", reply_markup=ReplyKeyboardMarkup([["Орқага"]], resize_keyboard=True))
        try:
            for data in tovar_data:
                context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
                context.bot.send_photo(chat_id=chat_id, photo=open(data[0], 'rb'))
                update.message.reply_text("Маҳсулот нархи: " + str(data[1]) + " сўм\nМаҳсулот ўлчами: " + data[2],
                                          reply_markup=InlineKeyboardMarkup(
                                              [
                                                  [InlineKeyboardButton("Сотиб олиш", callback_data='sotib' + str(data[3]))],
                                                  [InlineKeyboardButton("Бекор қилиш", callback_data='otmen' + str(data[3]))]
                                              ]))
        except Exception as e:
            print(str(e))
        return STATE_TOLOV_TURI


def savat_manzil(update, context):
    try:
        chat_id = str(update.message.from_user.id)
        locate = update.message.location
        obyekt = Customers()
        obyekt.user_data_update('longitude', str(locate.longitude), chat_id)
        obyekt.user_data_update('latitude', str(locate.latitude), chat_id)
        update.message.reply_text("Манзилингиз сақланди. Қайтадан саватчага киринг.",
                                  reply_markup=ReplyKeyboardMarkup([["Орқага"]], resize_keyboard=True))
    except Exception as e:
        print(str(e))
    return STATE_SAVATCHA


def tolov_turi(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    tovar_id = callback.data
    if tovar_id[:5] == 'otmen':
        tovar_id = tovar_id.replace('otmen', '')
        try:
            callback.edit_message_text("Маҳсулот бекор қилинди.")
            ob = Savatcha()
            ob.delete_tovar(chat_id, tovar_id)
        except Exception as e:
            print(str(e))
    else:
        print(callback.data)
        tovar_id = tovar_id.replace('sotib', '')
        callback.edit_message_text("Тўлов турини танланг: ", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Нақд', callback_data='naqd' + str(tovar_id)),
             InlineKeyboardButton('Пластик', callback_data='plastik' + str(tovar_id))]
        ]))
        return STATE_TURI_TOLOV


def savat_tolov(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    xarid_status = user_xarid(chat_id)
    obyekt = Savatcha()
    datas = obyekt.select_aralash(xarid_status, str(chat_id))
    if callback.data[:4] == 'naqd':
        tovar_id = callback.data.replace('naqd', '')
        obyekt = Order()
        obyekt.insert_order(str(chat_id), tovar_id)
        obyekt.delete_savat(str(chat_id), tovar_id)
        callback.edit_message_text("Сўровингиз қабул қилинди. Буюртмангиз ҳолатини текшириб туринг!")
        #     order ga yozish kerak
        print(tovar_id)
        return STATE_TOLOV_TURI
    else:
        try:
            tovar_id = callback.data
            print(tovar_id)
            tovar_id = tovar_id.replace('plastik', '')
            print(tovar_id)
            callback.edit_message_text("Сизнинг буюртмангиз:\nМаҳсулот номи: " + datas[0][0] + "\n" +
                                       "Маҳсулот нархи: " + str(datas[0][1]) + " сўм\n" +
                                       "Карта рақамингиз: " + str(datas[0][2]), reply_markup=InlineKeyboardMarkup([
                                        [InlineKeyboardButton("Тўлов қилиш", callback_data=str(tovar_id))]
                                        ]))
            print(tovar_id)
        except Exception as e:
            print(str(e))
        return STATE_BASKET_TOLOV


def karta_tolov(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    if callback.data == 'orqaga':
        pass
    else:
        print('aa', callback.data)
        xarid_status = user_xarid(chat_id)
        obyekt = Savatcha()
        narx = obyekt.select_narx(xarid_status, callback.data)[0]
        print("1")
        print(narx)
        print("2")
        print(xarid_status)
        print("3")
        try:
            callback.edit_message_text(
                order_caption_text1 + str(narx) + order_caption_text2,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Тўлов қилдим!", callback_data=callback.data)],
                    [InlineKeyboardButton('Бекор қилиш', callback_data='otmen' + callback.data)]
                ])
            )
        except Exception as e:
            print(str(e))
        return STATE_TOLOV_ORDER


def tolov_order(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    text = callback.data
    if text[:5] == 'otmen':
        tovar_id = text.replace('otmen', '')
        try:
            callback.edit_message_text("Маҳсулот бекор қилинди.")
            ob = Savatcha()
            ob.delete_tovar(chat_id, tovar_id)
        except Exception as e:
            print(str(e))
    elif text[:5] == 'sotib':
        print("tolov orderni sotib metodi")
        tovar_id = text.replace('sotib', '')
        callback.edit_message_text("Тўлов турини танланг: ", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton('Нақд', callback_data='naqd' + str(tovar_id)),
             InlineKeyboardButton('Пластик', callback_data='plastik' + str(tovar_id))]
        ]))
        return STATE_TURI_TOLOV
    else:
        print("aaa", text, type(text))
        obyekt = Order()
        obyekt.insert_order(str(chat_id), text)
        obyekt.delete_savat(str(chat_id), text)
        callback.edit_message_text("Сўровингиз қабул қилинди. Буюртмангиз ҳолатини текшириб туринг")
        return STATE_TOLOV_TURI


def savatTOtolov(update, context):
    pass


def order(update, context):
    chat_id = str(update.message.from_user.id)
    xarid_s = user_xarid(chat_id)
    obyekt = Order()
    tovar_data = obyekt.select_tovar(xarid_s, str(chat_id))
    print(xarid_s)
    print(tovar_data)
    update.message.reply_text("Сиз танлаган маҳсулотлар:", reply_markup=ReplyKeyboardMarkup([["Орқага"]], resize_keyboard=True))
    try:
        for data in tovar_data:
            holat = status_order(data[5])
            context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
            context.bot.send_photo(chat_id=chat_id, photo=open(data[0], 'rb'))
            update.message.reply_text("Маҳсулот номи: " + data[1] + "\nМаҳсулот нархи: " + str(data[2]) + " сўм" +
                                      "\nMahsulot o'lchami: " + data[3].capitalize() + "(" + data[4] + ")\nБуюртма ҳолати: " + holat)
    except Exception as e:
        print(str(e))
    return STATE_BUYURTMA


def status_order(data):
    if data == '-1':
        return "Бу маҳсулот бекор қилинган!"
    elif data == '0':
        return "Тасдиқланиш жараёнида."
    elif data == '1':
        return "Тасдиқланган."
    elif data == '2':
        return "Манзилга жўнатилган"
    else:
        return "Манзилга етиб борган"


def delivery(update, context):
    dostavkalar = "Bu yerda viloyatlar aro, shaharlar aro, kilometrBay bo'yicha dostavkalar haqida ma'lumot beriladi."
    update.message.reply_text(dostavkalar)


def info(update, context):
    dokonHaqida = "Bu Bek-Baraka savdo majmuasida joylashgan do'konning rasmiy boti." \
                  " Bu yerda siz turli xil kiyimlarni buyurtma berishingiz mumkin"
    update.message.reply_text(dokonHaqida)


def contact(update, context):
    dokonHaqida = "Biz bilan bog'lanish uchun tel raqamlar :\n" \
                  "+998 99 111 22 33\n..."
    update.message.reply_text(dokonHaqida)


def tovar(update, context):
    update.message.reply_text("Товарларни ўзгартириш учун",
                              reply_markup=ReplyKeyboardMarkup([
                                  ["Янги товар қўшиш"], ["Мавжуд товарни ўчириш"], ["Орқага"]
                              ], resize_keyboard=True))
    return ADMIN_TOVAR


def fasl_tanlash(update, context):
    chat_id = str(update.message.from_user.id)
    text = update.message.text.lower()
    if text == "янги товар қўшиш" or text == "мавжуд товарни ўчириш":
        admin_tovar[chat_id]['tovar'].update({'status': text})
    update.message.reply_text("Фасллардан бирини танланг.", reply_markup=ReplyKeyboardMarkup([
                                      ['Қиш', "Ёз"], ["Куз-баҳор"], ["Орқага"]
                                  ], resize_keyboard=True))
    return ADMIN_FASL


def addTovarToFasl(update, context):
    chat_id = str(update.message.from_user.id)
    admin_tovar[chat_id]['tovar'].update({'season': update.message.text.lower()})
    update.message.reply_text("Ўлчам турларидан бирини танланг.",
                              reply_markup=razmer_category)
    return TOVAR_RAZMER


def tovar_crud(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    admin_tovar[chat_id]['tovar'].update({'nomi': callback.data})
    print(admin_tovar, admin_tovar[chat_id]['tovar']['status'])
    if admin_tovar[chat_id]['tovar']['status'] == "yangi tovar qo'shish":
        try:
            callback.message.delete()
            callback.message.reply_text("Янги маҳсулот расмини юборинг.", reply_markup=ReplyKeyboardMarkup(
                [["Менюга қайтиш"]], resize_keyboard=True))
        except Exception as e:
            print(str(e))
        return ADD_TOVAR
    elif admin_tovar[chat_id]['tovar']['status'] == "mavjud tovarni o'chirish":
        obyekt = Tovar()
        tovar_data = obyekt.select_tovar(admin_tovar[chat_id]['tovar']['nomi'], admin_tovar[chat_id]['tovar']['season'],
                                         admin_tovar[chat_id]['tovar']['category'], admin_tovar[chat_id]['tovar']['razmeri'])
        # print(tovar_data)
        print(admin_tovar)
        callback.message.delete()
        callback.message.reply_text("Хозир мавжуд маҳсулотлар:")
        try:
            for data in tovar_data:
                context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
                context.bot.send_photo(chat_id=chat_id, photo=open(data[1], 'rb'))
                callback.message.reply_text("Оптом нархи: " + str(data[2]) + " сўм, дона нархи: " + str(data[3]) +
                                            " сўм\nМаҳсулотни ўчириш:", reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Ўчириш", callback_data=data[0])
                     ]]))
        except Exception as e:
            print(str(e))
        return DEL_TOVAR


def add_tovar(update, context):
    chat_id = str(update.message.from_user.id)
    today = str(datetime.now().time().second) + '-' + str(datetime.now().time().minute) + '-' + str(datetime.now().time().hour)
    date = str(datetime.now().date().day) + '-' + str(datetime.now().date().month) + '-' + str(datetime.now().date().year)
    kod = today + "_" + date
    admin_tovar[chat_id]['tovar'].update({'photoName': admin_tovar[chat_id]['tovar']['nomi'] + " " + kod})
    print(admin_tovar[chat_id]['tovar'])
    try:
        file = context.bot.getFile(update.message.photo[-1].file_id)
        file.download('images/' + admin_tovar[chat_id]['tovar']['season'] + "/" + admin_tovar[chat_id]['tovar']['category'] +
                      "/" + admin_tovar[chat_id]['tovar']['nomi'] + " " + kod + '.jpg')
        update.message.reply_text("Расм қўшилди. Энди унинг оптом ва дона нархларини намунадагидек киритинг:\n"
                                  "Шарт: <оптом нарх> <дона нарх>\nНамуна: 1000 3000")
    except Exception as e:
        print(str(e))
    return ADD_TOVAR_NARX


def add_tovar_narx(update, context):
    chat_id = str(update.message.from_user.id)
    narx = update.message.text.split(' ')
    try:
        narx[0] = int(narx[0])
        narx[1] = int(narx[1])
    except Exception as e:
        update.message.reply_text("Нархларни тўғри киритинг!")
        return ADD_TOVAR_NARX
    path = "images/" + admin_tovar[chat_id]['tovar']['season'] + "/" + admin_tovar[chat_id]['tovar']['category'] + "/" + \
           admin_tovar[chat_id]['tovar']['photoName'] + ".jpg"
    print(admin_tovar)
    print(path)
    try:
        obyekt = Tovar()
        obyekt.insert_tovar(admin_tovar[chat_id]['tovar']['nomi'], admin_tovar[chat_id]['tovar']['season'], admin_tovar[chat_id]['tovar']['category'],
                            admin_tovar[chat_id]['tovar']['razmeri'], path, str(narx[0]), str(narx[1]))
        update.message.reply_text("Янги маҳсулот қўшилди.",
                                  reply_markup=ReplyKeyboardMarkup([
                                      ["Янги товар қўшиш"], ["Мавжуд товарни ўчириш"], ["Орқага"]
                                  ], resize_keyboard=True))
    except Exception as e:
        print(str(e))
    return ADMIN_TOVAR


def del_tovar(update, context):
    callback = update.callback_query
    obyekt = Tovar()
    try:
        obyekt.delete_tovar(callback.data)
        callback.edit_message_text("Бу маҳсулот очирилди!")
    except Exception as e:
        print(str())


def order_holat(text):
    if text == "Тасдиқлаш ҳолатидагилар":
        return '0'
    elif text == "Тасдиқланганлар":
        return '1'
    elif text == "Жўнатилганлар":
        return '2'
    elif text == "Манзилга етиб борганлар":
        return '3'


def buyurtmalar(update, context):
    update.message.reply_text("Буюртмалар ҳолатлари:", reply_markup=ReplyKeyboardMarkup([
        ["Тасдиқлаш ҳолатидагилар"], ["Тасдиқланганлар", "Жўнатилганлар"], ["Манзилга етиб борганлар"], ["Орқага"]
    ], resize_keyboard=True))
    return ADMIN_BUYURTMA


def order_steps(update, context):
    chat_id = str(update.message.from_user.id)
    status = order_holat(update.message.text)
    print(status)
    obyekt = Order()
    malumotlar = obyekt.select_orders(status)
    inline_text = "inline text error"
    text = "reply text error"
    if status == '0':
        text = "Тасдиқланиши кутилаётган маҳсулотлар:"
        inline_text = "Тасдиқлаш"
    elif status == '1':
        text = "Тасдиқланган маҳсулотлар:"
        inline_text = "Манзилга жўнатилди"
    elif status == '2':
        text = "Жўнатилган маҳсулотлар:"
        inline_text = "Манзилга етказилди"
    elif status == '3':
        text = "Манзилга муваффақиятли етиб борган маҳсулотлар:"

    update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup([["Орқага"]], resize_keyboard=True))
    try:
        for malumot in malumotlar:
            xarid_turi = user_xarid(str(malumot[0]))
            tovar_datas = obyekt.tovar_data(xarid_turi, str(malumot[1]))
            for data in tovar_datas:
                context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
                context.bot.send_photo(chat_id=chat_id, photo=open(data[0], 'rb'))
                if status == '1':
                    update.message.reply_text(
                        "Маҳсулот номи: " + data[1] + "\nНархи: " + str(data[2]) + " сўм\nЎлчами: " + data[3].capitalize() + "(" + data[4] + ")",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("Етказиш манзили", callback_data="manzil" + str(malumot[0]))],
                            [
                                InlineKeyboardButton("Бекор қилиш", callback_data='otmen'),
                                InlineKeyboardButton(inline_text, callback_data=str(malumot[2]))
                            ]
                        ]))
                elif status == '3':
                    print("stepp")
                    update.message.reply_text("Маҳсулот номи: " + data[1] + "\nНархи: " + str(data[2]) +
                                              " сўм\nЎлчами: " + data[3] + "(" + data[4] + ") " + "\nМаҳсулот манзилга етказилган.")
                else:
                    update.message.reply_text(
                        "Маҳсулот номи: " + data[1] + "\nНархи: " + str(data[2]) + " сўм\nЎлчами: " + data[3] + "(" + data[4] + ")",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("Бекор қилиш", callback_data='otmen'),
                             InlineKeyboardButton(inline_text, callback_data=str(malumot[2]))
                             ]]))
    except Exception as e:
        print(str(e))
    return ADMIN_BUYURTMA_CONTROL


def update_order(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    order_id = callback.data
    obyekt = Order()
    if order_id == 'otmen':
        pass
    elif order_id[:6] == 'manzil':
        print(order_id)
        user_id = order_id.replace('manzil', '')
        ob = Customers()
        data = ob.select_location(user_id)[0]
        context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.FIND_LOCATION)
        context.bot.send_location(chat_id=chat_id, longitude=data[0], latitude=data[1])
    else:
        status = obyekt.select_data('status_order', order_id)[0]
        status = str(int(status) + 1)
        obyekt.update_status(status, order_id)
        callback.edit_message_text("Кейинги босқичга ўтказилди.")


def admin_razmer(update, context):
    sonlar = ""
    tur = update.message.text
    if tur == "Турк ўлчамлар":
        tur = "туркий"
    tur = tur.lower()
    writer(tur)
    obyekt = Razmer()
    razmerlar = obyekt.select_razmer(tur)

    if not razmerlar:
        update.message.reply_text("Сизда хозир ўлчамлар мавжуд эмас. Янги ўлчам қўшишингиз мумкин.",
                                  reply_markup=ReplyKeyboardMarkup([
                                      ["Янги ўлчам қўшиш"], ["Орқага"]
                                  ], resize_keyboard=True))
        return RAZMER_CRUD
    else:
        i = 1
        for x in razmerlar:
            for y in x:
                sonlar += str(i) + ". " + str(y) + "\n"
                i += 1
        update.message.reply_text("Хозир сиздаги мавжуд ўлчамлар:\n" + sonlar,
                                  reply_markup=ReplyKeyboardMarkup([
                                      ["Янги ўлчам қўшиш"], ["Мавжуд ўлчамни ўчириш"], ["Орқага"]
                                  ], resize_keyboard=True))
        return RAZMER_CRUD


def razmer_crud(update, context):
    text = update.message.text
    if text == "Янги ўлчам қўшиш":
        update.message.reply_text("Янги ўлчамни киритинг.", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
        return ADD_RAZMER
    else:
        step = reader()
        obyekt = Razmer()
        razmer = obyekt.select_razmer2(step)
        button = ""
        if not razmer:
            update.message.reply_text("Сизда хозирча ўлчамлар йўқ")
        else:
            for x in razmer:
                button += "Ўлчам: " + str(x[1]) + " Тартиб рақами: " + str(x[0]) + "\n"
            update.message.reply_text(button + "Рўйхатдаги ўлчамнинг тартиб рақамини киритинг.",
                                      reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
            return DEL_RAZMER


def add_razmer(update, context):
    size = update.message.text
    step = reader()
    print(size, step)
    obyekt = Razmer()
    obyekt.razmer_add(str(size), step)
    update.message.reply_text("Янги ўлчам қўшилди. Ўлчам турларидан бирини танланг.",
                              reply_markup=razmer_category)
    return ADMIN_RAZMER


def del_razmer(update, context):
    razmer_id = update.message.text
    obyekt = Razmer()
    obyekt.razmer_del(razmer_id)
    update.message.reply_text("Ўлчам ўчирилди. Ўлчам турларидан бирини танланг.",
                              reply_markup=razmer_category)
    return ADMIN_RAZMER


def admin_nazorat(update, context):
    update.message.reply_text("Aдминлар бошқаруви:", reply_markup=ReplyKeyboardMarkup([
        ["Янги админ қўшиш"], ["Мавжуд админни ўчириш"], ["Орқага"]
    ], resize_keyboard=True))
    return ADMIN_CRUD


def admin_crud(update, context):
    text = update.message.text
    if text == 'Янги админ қўшиш':
        update.message.reply_text("Янги админнинг ид рақамини юборинг!", reply_markup=ReplyKeyboardMarkup([["Орқага"]], resize_keyboard=True))
        return ADD_ADMIN
    else:
        obyekt = Admins()
        admins = obyekt.select_admin()
        if not admins:
            update.message.reply_text("Сизда админлар йўқ", reply_markup=ReplyKeyboardMarkup([["Янги админ қўшиш"], ["Орқага"]],
                                                                                             resize_keyboard=True))
            return ADMIN_CRUD
        else:
            adminlar = ""
            for x in admins:
                adminlar += "Aдмин ИД: " + str(x[1]) + " Тартиб рақами: " + str(x[0]) + "\n"
            update.message.reply_text(adminlar + "Рўйхатдаги админнинг тартиб рақамини киритинг.",
                                      reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
            return DEL_ADMIN


def add_admin(update, context):
    admin_id = update.message.text
    if admin_id.isdigit() and len(admin_id) >= 5:
        obyekt = Admins()
        obyekt.insert_admin(admin_id)
        update.message.reply_text("Янги админ қўшилди.", reply_markup=ReplyKeyboardMarkup([
            ["Янги админ қўшиш"], ["Мавжуд админни ўчириш"], ["Орқага"]
        ], resize_keyboard=True))
        return ADMIN_CRUD
    else:
        update.message.reply_text("Raqamni to'g'ri kiriting!")


def del_admin(update, context):
    admin_id = update.message.text
    obyekt = Admins()
    obyekt.delete_admin(admin_id)
    update.message.reply_text("Ушбу админ ўчирилди.", reply_markup=ReplyKeyboardMarkup([
        ["Янги админ қўшиш"], ["Мавжуд админни ўчириш"], ["Орқага"]
    ], resize_keyboard=True))
    return ADMIN_CRUD


def main():
    updater = Updater('1218844571:AAHesAbLwlqKFkAUMkq2vJ5buLH3xwZqHXo', use_context=True)
    dispatcher = updater.dispatcher

    # dispatcher.add_handler(CommandHandler('start', start))

    controller = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ADMIN_CRUD: [
                MessageHandler(Filters.regex('^(' + "Янги админ қўшиш" + ')$'), admin_crud),
                MessageHandler(Filters.regex('^('+"Мавжуд админни ўчириш"+')$'), admin_crud),
                MessageHandler(Filters.regex('^('+"Орқага"+')$'), menyu)
            ],
            ADD_ADMIN: [MessageHandler(Filters.text, add_admin)],
            DEL_ADMIN: [MessageHandler(Filters.text, del_admin)],
            STATE_FISH: [MessageHandler(Filters.text, f_i_sh)],
            STATE_NUMBER: [MessageHandler(Filters.contact, number)],
            STATE_LOCATION: [
                MessageHandler(Filters.location, location),
                MessageHandler(Filters.regex('^(' + "Keyinroq yuborish" + ')$'), keyinroq)
            ],
            STATE_CARD: [MessageHandler(Filters.text, card)],
            STATE_XARID: [
                MessageHandler(Filters.regex('^(' + "Оптом" + ')$'), xarid),
                MessageHandler(Filters.regex('^(' + "Donaga" + ')$'), xarid)
            ],
            STATE_MENYU: [
                MessageHandler(Filters.regex('^(' + "Savdo qilish" + ')$'), savdo),
                MessageHandler(Filters.regex('^(' + "Ma'lumotlarim" + ')$'), user),
                MessageHandler(Filters.regex('^(' + "Savatcha" + ')$'), savatcha),
                MessageHandler(Filters.regex('^(' + "Буюртмалар holatini tekshirish" + ')$'), order),
                MessageHandler(Filters.regex('^(' + "Dostavkalar haqida ma'lumot" + ')$'), delivery),
                MessageHandler(Filters.regex('^(' + "Biz haqimizda" + ')$'), info),
                MessageHandler(Filters.regex('^(' + "Aloqa" + ')$'), contact),
            ],
            STATE_USER: [
                MessageHandler(Filters.regex('^(' + "Ф. И. Ш" + ')$'), userData),
                MessageHandler(Filters.regex('^(' + "Телефон рақам" + ')$'), userData),
                MessageHandler(Filters.regex('^(' + "Manzil" + ')$'), userData),
                MessageHandler(Filters.regex('^(' + "Karta raqam" + ')$'), userData),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
            ],
            STATE_USER2: [
                MessageHandler(Filters.regex('^(' + "Ўзгартириш" + ')$'), change),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), user)
            ],
            STATE_USER3: [
                MessageHandler(Filters.text, change_user_data),
                MessageHandler(Filters.location, change_user_locate),
                MessageHandler(Filters.contact, change_user_phone)
            ],
            STATE_SAVDO: [
                MessageHandler(Filters.regex('^(' + "Қиш" + ')$'), fasl),
                MessageHandler(Filters.regex('^(' + "Ёз" + ')$'), fasl),
                MessageHandler(Filters.regex('^(' + "Куз-баҳор" + ')$'), fasl),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
            ],
            STATE_RAZMER: [
                MessageHandler(Filters.regex('^(' + "Болшимерка" + ')$'), razmer),
                MessageHandler(Filters.regex('^(' + "Маламерка" + ')$'), razmer),
                MessageHandler(Filters.regex('^(' + "Турк ўлчамлар" + ')$'), razmer),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), savdo),
            ],
            TOGETHER: [CallbackQueryHandler(together)],
            STATE_TOVAR_RAZMER: [
                CallbackQueryHandler(select_mahsulot_nomi),
                MessageHandler(Filters.regex('^(' + "Менюга қайтиш" + ')$'), menyu)
            ],
            STATE_TOVAR_TANLASH: [
                CallbackQueryHandler(tovar_tanlash),
                MessageHandler(Filters.regex('^(' + "Менюга қайтиш" + ')$'), menyu)
            ],
            STATE_TOVAR_SAVATCHA: [
                CallbackQueryHandler(tovarTOsavat),
                MessageHandler(Filters.regex('^(' + "Менюга қайтиш" + ')$'), menyu)
            ],
            STATE_SAVAT_LOCATION: [
                MessageHandler(Filters.location, savat_manzil),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
            ],
            STATE_SAVATCHA: [MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)],
            STATE_TOLOV_TURI: [
                CallbackQueryHandler(tolov_turi),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
            ],
            STATE_TURI_TOLOV: [CallbackQueryHandler(savat_tolov)],
            STATE_BASKET_TOLOV: [
                CallbackQueryHandler(karta_tolov),
                MessageHandler(Filters.regex('^(' + "Barchasini sotib olish" + ')$'), savatTOtolov)
            ],
            STATE_TOLOV_ORDER: [CallbackQueryHandler(tolov_order)],
            STATE_BUYURTMA: [MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)],
            ADMIN_MENYU: [
                MessageHandler(Filters.regex('^(' + "Товарлар" + ')$'), tovar),
                MessageHandler(Filters.regex('^(' + "Буюртмалар" + ')$'), buyurtmalar),
                MessageHandler(Filters.regex('^(' + "Ўлчамлар" + ')$'), fasl),
                MessageHandler(Filters.regex('^(' + "Aдмин Назорат" + ')$'), admin_nazorat),
            ],
            ADMIN_TOVAR: [
                MessageHandler(Filters.regex('^(' + "Янги товар қўшиш" + ')$'), fasl_tanlash),
                MessageHandler(Filters.regex('^(' + "Mavjud tovarni o'chirish" + ')$'), fasl_tanlash),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
            ],
            ADMIN_FASL: [
                MessageHandler(Filters.regex('^(' + "Қиш" + ')$'), addTovarToFasl),
                MessageHandler(Filters.regex('^(' + "Ёз" + ')$'), addTovarToFasl),
                MessageHandler(Filters.regex('^(' + "Куз-баҳор" + ')$'), addTovarToFasl),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), tovar)
            ],
            TOVAR_RAZMER: [
                MessageHandler(Filters.regex('^(' + "Болшимерка" + ')$'), razmer),
                MessageHandler(Filters.regex('^(' + "Маламерка" + ')$'), razmer),
                MessageHandler(Filters.regex('^(' + "Турк ўлчамлар" + ')$'), razmer),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), fasl_tanlash),
            ],
            TOVAR_CRUD: [
                CallbackQueryHandler(tovar_crud),
                MessageHandler(Filters.regex('^(' + "Менюга қайтиш" + ')$'), menyu)
            ],
            ADD_TOVAR: [
                MessageHandler(Filters.photo, add_tovar),
                MessageHandler(Filters.regex('^(' + "Менюга қайтиш" + ')$'), menyu)
            ],
            ADD_TOVAR_NARX: [MessageHandler(Filters.text, add_tovar_narx)],
            DEL_TOVAR: [
                CallbackQueryHandler(del_tovar),
                MessageHandler(Filters.regex("Менюга қайтиш"), tovar)
            ],
            ADMIN_BUYURTMA: [
                MessageHandler(Filters.regex('^(' + "Тасдиқлаш ҳолатидагилар" + ')$'), order_steps),
                MessageHandler(Filters.regex('^(' + "Тасдиқланганлар" + ')$'), order_steps),
                MessageHandler(Filters.regex('^(' + "Жўнатилганлар" + ')$'), order_steps),
                MessageHandler(Filters.regex('^(' + "Манзилга етиб борганлар" + ')$'), order_steps),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
            ],
            ADMIN_BUYURTMA_CONTROL: [
                CallbackQueryHandler(update_order),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), buyurtmalar)
            ],
            ADMIN_RAZMER: [
                MessageHandler(Filters.regex('^(' + "Болшимерка" + ')$'), admin_razmer),
                MessageHandler(Filters.regex('^(' + "Маламерка" + ')$'), admin_razmer),
                MessageHandler(Filters.regex('^(' + "Турк ўлчамлар" + ')$'), admin_razmer),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), start)
            ],
            RAZMER_CRUD: [
                MessageHandler(Filters.regex('^(' + "Янги ўлчам қўшиш" + ')$'), razmer_crud),
                MessageHandler(Filters.regex('^(' + "Мавжуд ўлчамни ўчириш" + ')$'), razmer_crud),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), fasl)
            ],
            ADD_RAZMER: [MessageHandler(Filters.text, add_razmer)],
            DEL_RAZMER: [MessageHandler(Filters.text, del_razmer)]
        },
        fallbacks=[CommandHandler('start', start)]
    )

    dispatcher.add_handler(controller)
    dispatcher.add_handler(MessageHandler(Filters.text, action))
    updater.start_polling()
    updater.idle()


customer_menyu = ReplyKeyboardMarkup([
    ['Савдо қилиш', "Маълумотларим"], ["Саватча"], ["Буюртмалар ҳолатини текшириш"],
    ["Доставкалар ҳақида маълумот"], ["Биз ҳақимизда", "Aлоқа"]
], resize_keyboard=True)

admin_menyu = ReplyKeyboardMarkup([["Товарлар", "Буюртмалар"], ["Ўлчамлар"]], resize_keyboard=True)

super_menyu = ReplyKeyboardMarkup([["Товарлар", "Буюртмалар"], ["Ўлчамлар", "Aдмин Назорат"]], resize_keyboard=True)

razmer_category = ReplyKeyboardMarkup([['Болшимерка', "Маламерка"], ["Турк ўлчамлар"], ["Орқага"]], resize_keyboard=True)

customer_malumotlari = ReplyKeyboardMarkup([['Ф. И. Ш', "Телефон рақам"], ["Карта рақам", "Манзил"], ["Орқага"]], resize_keyboard=True)

order_caption_text1 = """8600 1111 2222 3333 -> Sotuvchining karta raqami.\n
To'lovingiz muvaffaqiyatli bajarilishi uchun quyidagi amallarni bajaring:
1. Payme.uz yoki Click.uz dan ro'yxatdan o'ting.
2. Pastda ko'rsatilgan to'lov miqdorini - (8600 1111 2222 3333) "Abduraim" karta raqamiga o'tkazing.
3. "To'lov qildim!" tugmasini bosing.
4. Admin tomonidan karta raqamingiz va ismingiz mos kelishi tasdiqlanishini kuting.
                
        To'lov miqdori: """

order_caption_text2 = """ сўм\n
Ushbu o'tkazma admin tomonidan navbati bilan 2 daqiqadan 1 soatgacha oraliqda tekshirilishi mumkin."""

if __name__ == '__main__':
    main()
