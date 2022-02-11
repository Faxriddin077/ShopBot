from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup, ChatAction, LabeledPrice
from conf import TOKEN
from datetime import datetime, timedelta
from backend import buttons, Customers, Tovar, Razmer, Savatcha, Order, Admins, check_admin, show_razmer, sticker_crud
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, PreCheckoutQueryHandler
import sqlite3

global step
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


def user_xarid(id):
    obyekt = Customers()
    xarid_status = obyekt.select_user_xarid(str(id))
    if xarid_status[0] == "Оптом":
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

ANSWER_CHECKOUT = 7

ADMIN_MENYU = 10
ADMIN_TOVAR = 10.1
ADMIN_FASL = 11.1
TOVAR_RAZMER = 11.2
TOVAR_CRUD = 11.3
ADD_TOVAR = 113.1
ADD_TOVAR_NARX = 113.3
DEL_TOVAR = 113.2
ADMIN_ORDER_TYPE = 10.21
ADMIN_BUYURTMA = 10.2
ADMIN_BUYURTMA_CONTROL = 102.1
ADMIN_TOVAR_STATUS = 10.3
ADMIN_RAZMER = 10.4
RAZMER_CRUD = 13
ADD_RAZMER = 13.1
DEL_RAZMER = 13.2

DELIVERY_CRUD = 14
DELIVERY_ADD = 14.1

ADMIN_CRUD = 0.1
ADD_ADMIN = 0.2
DEL_ADMIN = 0.3

super_admin = '490007636'


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
        update.message.reply_text("Ассалому алейкум {}. Ботдан фойдаланиш учун рўйхатдан ўтишингиз зарур. Биз сиз билан боғланишимизда муаммо "
                                  "бўлмаслиги учун исмингизни тўлиғича киритинг!".format(update.message.from_user.first_name),
                                  reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
        return STATE_FISH


def f_i_sh(update, context):
    chat_id = str(update.message.from_user.id)
    fish = update.message.text
    if all(x.isalpha() or x.isspace() for x in fish):
        customer_data[chat_id]['register'].update({'name': fish})
        contact_keyboard = KeyboardButton(text="Рақамни юбориш", request_contact=True, resize_keyboard=True)
        reply_markup = ReplyKeyboardMarkup([[contact_keyboard]], resize_keyboard=True)
        update.message.reply_text('Энди телефон рақамингизни юборинг. Бунинг учун тугмачани босинг.', reply_markup=reply_markup)
        return STATE_NUMBER
    else:
        update.message.reply_text("Илтимос исмингизни тўғри киритинг", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
        return STATE_FISH


def number(update, context):
    chat_id = str(update.message.from_user.id)
    contact = update.message.contact.phone_number
    customer_data[chat_id]['register'].update({'contact': contact})
    location_keyboard = KeyboardButton(text="Манзилни юбориш", request_location=True, resize_keyboard=True)
    reply_markup = ReplyKeyboardMarkup([[location_keyboard], ["Кейинроқ юбориш"]], resize_keyboard=True)
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
                                  reply_markup=ReplyKeyboardMarkup([["Оптом", "Донага"]], resize_keyboard=True))
    else:
        update.message.reply_text("Карта рақамни тўғри киритинг!")
        return STATE_CARD
    return STATE_XARID


def xarid(update, context):
    chat_id = str(update.message.from_user.id)
    xarid = update.message.text
    customer_data[chat_id]['register'].update({'xarid_status': xarid})
    # Bazaga yozish
    try:
        obyekt = Customers()
        count = obyekt.check_customer(chat_id)
        if count[0] == 1:
            obyekt.delete_customer(chat_id)
            ob = Order()
            ob.delete_basket(chat_id)
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
    if turi == "турк ўлчамлар":
        turi = "туркий"
    button = show_razmer(turi)
    if check_admin(chat_id) or chat_id == super_admin:
        admin_tovar[chat_id]['tovar']['category'] = turi
        if admin_tovar[chat_id]['tovar']['status'] == 'янги товар қўшиш':
            admin_tovar[chat_id]['tovar']['add_status'] = {'Оптом': '0', 'Дона': '0'}
            update.message.reply_text("Қўшиш усулини танланг", reply_markup=ReplyKeyboardMarkup([["Менюга қайтиш"]], resize_keyboard=True))
            update.message.reply_text("Усуллар:", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton('Оптом', callback_data='Оптом'), InlineKeyboardButton('Дона', callback_data='Дона')],
                [InlineKeyboardButton('Кейингиси', callback_data='ok')]]))
            return ADMIN_TOVAR_STATUS
        else:
            update.message.reply_text("Ўлчамлар:", reply_markup=ReplyKeyboardMarkup([["Менюга қайтиш"]], resize_keyboard=True))
            update.message.reply_text("Керакли ўлчамингизни танланг.", reply_markup=InlineKeyboardMarkup(button))
            return STATE_TOVAR_RAZMER
    else:
        # ReplyKeyboardMarkup([["Менюга қайтиш"]], resize_keyboard=True)
        update.message.reply_text("Ўлчамлар:", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
        update.message.reply_text("Керакли ўлчамингизни танланг.", reply_markup=InlineKeyboardMarkup(button))
        customer_data[chat_id]['savdo'].update({'category': turi})
        return STATE_TOVAR_RAZMER


def status_together(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    x = admin_tovar[chat_id]['tovar']['add_status']
    if callback.data == 'ok':
        if not [1 for y in x.values() if y == '1']:
            callback.message.reply_text("Усулни танланг!")
        else:
            if x['Оптом'] == '1' and x['Дона'] == '0':
                nomlar = buttons(admin_tovar[chat_id]['tovar']['season'])
                callback.edit_message_text("Маҳсулот турларидан бирини танланг:", reply_markup=InlineKeyboardMarkup(nomlar))
                return TOVAR_CRUD
            else:
                button = show_razmer(admin_tovar[chat_id]['tovar']['category'])
                obyekt = Razmer()
                razmerlar = obyekt.select_razmer(admin_tovar[chat_id]['tovar']['category'])
                admin_tovar[chat_id]['tovar']['add_stiker'] = {}
                for x in razmerlar:
                    admin_tovar[chat_id]['tovar']['add_stiker'].update({x['razmer']: '0'})
                button.append([InlineKeyboardButton("Маҳсулот қўшиш", callback_data='addtovar')])
                callback.edit_message_text("Керакли ўлчамингизни танланг.", reply_markup=InlineKeyboardMarkup(button))
                return TOGETHER
    else:
        if x[callback.data] == '0':
            x[callback.data] = '1'
        else:
            x[callback.data] = '0'
        button = [[]]
        for a, b in x.items():
            if b == '1':
                button[0].append(InlineKeyboardButton(a + '☑️', callback_data=a))
            else:
                button[0].append(InlineKeyboardButton(a, callback_data=a))
        button.append([InlineKeyboardButton('Keyingisi', callback_data='ok')])
        callback.edit_message_text("Усуллар:", reply_markup=InlineKeyboardMarkup(button))


def together(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    if callback.data == 'addtovar':
        if not [1 for y in admin_tovar[chat_id]['tovar']['add_stiker'].values() if y == '1']:
            callback.message.reply_text("Улчамни танланг!")
        else:
            admin_tovar[chat_id]['tovar']['razmeri'] = []
            for x, y in admin_tovar[chat_id]['tovar']['add_stiker'].items():
                if y == '1':
                    admin_tovar[chat_id]['tovar']['razmeri'].append(x)
            nomlar = buttons(admin_tovar[chat_id]['tovar']['season'])
            callback.edit_message_text(text="Маҳсулот турларидан бирини танланг:", reply_markup=InlineKeyboardMarkup(nomlar))
            return TOVAR_CRUD
    elif callback.data == "showRazmer":
        callback.message.delete()
        callback.message.reply_text("Ўлчам турларидан бирини танланг.", reply_markup=razmer_category)
        return TOVAR_RAZMER
    else:
        royxat = admin_tovar[chat_id]['tovar']
        if royxat['add_stiker'][callback.data] == '0':
            royxat['add_stiker'][callback.data] = '1'
        else:
            royxat['add_stiker'][callback.data] = '0'
        knopka = sticker_crud(royxat['category'], royxat['add_stiker'])
        callback.edit_message_text("Керакли ўлчамингизни танланг.", reply_markup=InlineKeyboardMarkup(knopka))


def select_mahsulot_nomi(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    if check_admin(chat_id) or chat_id == super_admin:
        if callback.data != 'showRazmer':
            admin_tovar[chat_id]['tovar']['razmeri'] = callback.data
            nomlar = buttons(admin_tovar[chat_id]['tovar']['season'])
            callback.edit_message_text(text="Маҳсулот турларидан бирини танланг:", reply_markup=InlineKeyboardMarkup(nomlar))
            return TOVAR_CRUD
        else:
            callback.message.delete()
            callback.message.reply_text("Ўлчам турларидан бирини танланг.", reply_markup=razmer_category)
            return TOVAR_RAZMER
    else:
        if callback.data == "showRazmer":
            callback.message.delete()
            callback.message.reply_text("Қайси тур ўлчамдан харид қилишингизни танланг.", reply_markup=razmer_category)
            return STATE_RAZMER
        else:
            nomlar = buttons(customer_data[chat_id]['savdo']['season'])
            callback.edit_message_text(text="Маҳсулот турларидан бирини танланг:", reply_markup=InlineKeyboardMarkup(nomlar))
            customer_data[chat_id]['savdo'].update({'razmeri': callback.data})
            return STATE_TOVAR_TANLASH


def tovar_tanlash(update, context):
    callback = update.callback_query
    if callback.data == "showSize":
        callback.message.delete()
        callback.message.reply_text("Қайси тур ўлчамдан харид қилишингизни танланг.", reply_markup=razmer_category)
        return STATE_RAZMER
    else:
        chat_id = str(callback.from_user.id)
        xarid_status = user_xarid(chat_id)
        customer_data[chat_id]['savdo'].update({'nomi': callback.data})
        customer_data[chat_id]['savdo'].update({'xarid_status': xarid_status})
        obyekt_tovar = Tovar()
        tovar_data = obyekt_tovar.select_tovar_user(xarid_status, customer_data[chat_id]['savdo']['nomi'], customer_data[chat_id]['savdo']['season'],
                                                    customer_data[chat_id]['savdo']['category'], customer_data[chat_id]['savdo']['razmeri'])

        if all(tovar[1] == 0 for tovar in tovar_data):
            callback.message.reply_text("Бу турда маҳсулотлар йўқ")
        else:
            callback.message.delete()
            callback.message.reply_text("Хозир мавжуд маҳсулотлар:", reply_markup=ReplyKeyboardMarkup([["Менюга қайтиш"]], resize_keyboard=True))
            try:
                for data in tovar_data:
                    if data[1] != 0:
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
    obyekt = Savatcha()
    try:
        if callback.data.isdigit():
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
    connect = sqlite3.connect("baza.db", check_same_thread=True)
    cursor = connect.cursor()
    query = None
    if update.message.text == "Ф. И. Ш":
        text = "Сизнинг исмингиз: "
        query = "select name from customers where chat_id='" + chat_id + "'"
        customer_data[chat_id]['user_data'].update({'step': 'name'})
    elif update.message.text == "Телефон рақам":
        text = "Сизнинг телефон рақамингиз: "
        query = "select contact from customers where chat_id='" + chat_id + "'"
        customer_data[chat_id]['user_data'].update({'step': 'contact'})
    elif update.message.text == "Манзил":
        text = "Сизнинг манзилингиз:"
        data = cursor.execute("select longitude, latitude from customers where chat_id='" + chat_id + "'").fetchall()[0]
        if data[0]:
            update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup([["Ўзгартириш"], ["Орқага"]], resize_keyboard=True))
            context.bot.send_location(chat_id=chat_id, longitude=data[0], latitude=data[1])
            customer_data[chat_id]['user_data'].update({'step': 'adres'})
        else:
            location_keyboard = KeyboardButton(text="Манзилни юбориш", request_location=True, resize_keyboard=True)
            update.message.reply_text("Манзилингиз киритилмаган!", reply_markup=ReplyKeyboardMarkup([[location_keyboard], ["Орқага"]], resize_keyboard=True))
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


def add_location(update, context):
    chat_id = str(update.message.from_user.id)
    try:
        locate = update.message.location
        longitude = str(locate.longitude)
        latitude = str(locate.latitude)
        connect = sqlite3.connect("baza.db", check_same_thread=True)
        cursor = connect.cursor()
        sqlite_insert_query = "update customers set longitude='" + longitude + "', latitude='" + latitude + "' where chat_id='" + chat_id + "'"
        cursor.execute(sqlite_insert_query)
        connect.commit()
        update.message.reply_text("Манзилингиз киритилди. Менюлардан фойдаланишингиз мумкин.",
                                  reply_markup=customer_menyu)
    except Exception as e:
        print(str(e))
    return STATE_MENYU


def change(update, context):
    chat_id = str(update.message.from_user.id)
    step = customer_data[chat_id]['user_data']['step']
    if step == "name":
        update.message.reply_text("Ўзгартирмоқчи бўлган исмингизни киритинг.", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
    elif step == "contact":
        location_keyboard = KeyboardButton(text="Рақамни юбориш", request_contact=True, resize_keyboard=True)
        phone = ReplyKeyboardMarkup([[location_keyboard]], resize_keyboard=True)
        update.message.reply_text("Ўзгартирмоқчи бўлган телефон рақамингизни юборинг. Бунинг учун тугмачани босинг.", reply_markup=phone)
    elif step == "card_number":
        update.message.reply_text("Ўзгартирмоқчи бўлган карта рақамингизни киритинг.", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
    else:
        location_keyboard = KeyboardButton(text="Манзилни юбориш", request_location=True, resize_keyboard=True)
        reply_markup = ReplyKeyboardMarkup([[location_keyboard]], resize_keyboard=True)
        update.message.reply_text("Ўзгартирмоқчи бўлган манзилингизни юборинг. Бунинг учун тугмачани босинг.", reply_markup=reply_markup)
    return STATE_USER3


def change_user_data(update, context):
    chat_id = str(update.message.from_user.id)
    step = customer_data[chat_id]['user_data']['step']
    if step == "name" or step == "card_number":
        obyekt = Customers()
        data = update.message.text
        obyekt.user_data_update(step, data, chat_id)
        update.message.reply_text("Маълумотингиз янгиланди.",
                                  reply_markup=customer_malumotlari)
        return STATE_USER


def change_user_phone(update, context):
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
        print(str(e))
    update.message.reply_text("Манзилингиз янгиланди.  Маълумотларингиз:",
                              reply_markup=customer_malumotlari)
    return STATE_USER


def savatcha(update, context):
    chat_id = str(update.message.from_user.id)
    ob = Customers()
    manzil = ob.select_location(chat_id)
    if not manzil[0][0]:
        location_keyboard = KeyboardButton(text="Манзилни юбориш", request_location=True, resize_keyboard=True)
        reply_markup = ReplyKeyboardMarkup([[location_keyboard], ["Орқага"]], resize_keyboard=True)
        update.message.reply_text('Манзилингиз киритилмаган. Юбориш учун тугмачани босинг.', reply_markup=reply_markup)
        return STATE_SAVAT_LOCATION
    else:
        xarid_s = user_xarid(chat_id)
        obyekt = Savatcha()
        tovar_data = obyekt.select_tovar(str(chat_id), xarid_s)
        if not tovar_data:
            update.message.reply_text("Сиз саватчага маҳсулот қўшмагансиз!", reply_markup=customer_menyu)
            return STATE_MENYU
        else:
            update.message.reply_text("Сиз танлаган маҳсулотлар:", reply_markup=ReplyKeyboardMarkup([["Орқага"]], resize_keyboard=True))
            try:
                for data in tovar_data:
                    if str(data[1]) != '0':
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
        obyekt.insert_order(str(chat_id), tovar_id, 'нақд')
        obyekt.delete_savat(str(chat_id), tovar_id)
        callback.edit_message_text("Сўровингиз қабул қилинди. Буюртмангиз ҳолатини текшириб туринг!")
        return STATE_TOLOV_TURI
    else:
        try:
            tovar_id = callback.data.replace('plastik', '')
            customer_data[chat_id]['tovar_id'] = tovar_id
            info = "Эслатма! \n\nБот автоматик тўлов тизимига уланган. Бу ерда сиз танлаган маҳсулотларингиз пулини тўлай оласиз."
            callback.edit_message_text("Сизнинг буюртмангиз:\nМаҳсулот номи: " + datas[0][0] + "\n" +
                                       "Маҳсулот нархи: " + str(datas[0][1]) + " сўм\n" +
                                       "Карта рақамингиз: " + str(datas[0][2]) + "\n\n" + info, reply_markup=InlineKeyboardMarkup([
                                        [InlineKeyboardButton("Тўлов қилиш", callback_data=str(tovar_id))]
                                        ]))
        except Exception as e:
            print(str(e))
        return STATE_BASKET_TOLOV


def karta_tolov(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    if callback.data == 'orqaga':
        pass
    else:
        xarid_status = user_xarid(chat_id)
        obyekt = Savatcha()
        narx = obyekt.select_narx(xarid_status, callback.data)[0]
        title = "Тўлов қисм"
        description = "Пастдаги тугмачани босиш орқали сиз тўлов қилиш меюсига автоматик ўтасиз. " \
                      "У ерда сиз маълумотларингизни киритиб тўлов қилишингиз мумкин."
        payload = "PaymeMaster"
        # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
        provider_token = "387026696:LIVE:5f3c045b5b9c7f8d29bdabad"
        start_parameter = "paymeStart"
        currency = "UZS"
        # price in dollars
        price = 100
        # price * 100 so as to include 2 decimal points
        prices = [LabeledPrice("Товар нархи:", price * narx)]
        try:
            context.bot.send_invoice(chat_id, title, description, payload, provider_token, start_parameter, currency, prices)
        except Exception as e:
            print(str(e))
        return ANSWER_CHECKOUT


def answer_precheckout(update, context):
    query = update.pre_checkout_query
    if query.invoice_payload == 'PaymeMaster':
        context.bot.answer_pre_checkout_query(ok=True, pre_checkout_query_id=query.id)
        return ANSWER_CHECKOUT
    else:
        query.answer(ok=False, error_message="Xatolik mavjud...")


def successful_payment_callback(update, context):
    chat_id = str(update.message.from_user.id)
    tovar_id = customer_data[chat_id]['tovar_id']
    obyekt = Order()
    try:
        obyekt.insert_order(str(chat_id), str(tovar_id), 'пластик')
        obyekt.delete_savat(str(chat_id), str(tovar_id))
        update.message.reply_text("Раҳмат, тўловингиз мувафаққиятли ўтказилди!", reply_markup=customer_menyu)
    except Exception as e:
        print(str(e))
    return STATE_MENYU


def order(update, context):
    chat_id = str(update.message.from_user.id)
    xarid_s = user_xarid(chat_id)
    obyekt = Order()
    tovar_data = obyekt.select_tovar(xarid_s, str(chat_id))
    if not tovar_data:
        update.message.reply_text("Сиз маҳсулот буюртма бермагансиз!", reply_markup=customer_menyu)
        return STATE_MENYU
    else:
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
    chat_id = str(update.message.from_user.id)
    with open('delivery.txt', 'r') as fayl:
        dostavkalar = fayl.read()
    if not dostavkalar:
        update.message.reply_text("Маълумот топилмади. Янги маълумотларни киритинг:", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
        return DELIVERY_ADD
    if chat_id == super_admin or check_admin(chat_id):
        update.message.reply_text(dostavkalar, reply_markup=ReplyKeyboardMarkup([
                ["Ўзгартириш"], ["Орқага"]
            ], resize_keyboard=True))
        return DELIVERY_CRUD
    else:
        update.message.reply_text(dostavkalar)


def info(update, context):
    dokonHaqida = "Бу Бек-Барака савдо мажмуасида жойлашган дўконнинг расмий боти." \
                  " Бу ерда сиз турли хил аёллар кийимларини буюртма беришингиз мумкин.\nБизнинг дўконларимиз:\n" \
                  "Бек барака 2 катор 248 магазини\nУчтепа тумани г 9а Квартл,1 дом 65 кв(Арентир Фархадски бозор)"
    update.message.reply_text(dokonHaqida)


def contact(update, context):
    dokonHaqida = "Биз билан боғланиш учун телефон рақамлар:\n" \
                  "📞 +99899-828-66-58\n📞 +99894-114-14-14"
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
    update.message.reply_text("Ўлчам турларидан бирини танланг.", reply_markup=razmer_category)
    return TOVAR_RAZMER


def tovar_crud(update, context):
    callback = update.callback_query
    chat_id = str(callback.from_user.id)
    if callback.data == 'showSize':
        callback.message.delete()
        callback.message.reply_text("Ўлчам турларидан бирини танланг.", reply_markup=razmer_category)
        return TOVAR_RAZMER
    else:
        admin_tovar[chat_id]['tovar'].update({'nomi': callback.data})
        if admin_tovar[chat_id]['tovar']['status'] == "янги товар қўшиш":
            try:
                callback.message.delete()
                callback.message.reply_text("Янги маҳсулот расмини юборинг.", reply_markup=ReplyKeyboardMarkup(
                    [["Менюга қайтиш"]], resize_keyboard=True))
            except Exception as e:
                print(str(e))
            return ADD_TOVAR
        elif admin_tovar[chat_id]['tovar']['status'] == "мавжуд товарни ўчириш":
            obyekt = Tovar()
            tovar_data = obyekt.select_tovar(admin_tovar[chat_id]['tovar']['nomi'], admin_tovar[chat_id]['tovar']['season'],
                                             admin_tovar[chat_id]['tovar']['category'], admin_tovar[chat_id]['tovar']['razmeri'])
            callback.message.delete()
            if not tovar_data:
                callback.message.reply_text("Хозир бизда бу турдаги маҳсулотлар йўқ.")
            else:
                callback.message.reply_text("Хозир мавжуд маҳсулотлар:")
                try:
                    for data in tovar_data:
                        context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_PHOTO)
                        context.bot.send_photo(chat_id=chat_id, photo=open(data[1], 'rb'))
                        callback.message.reply_text("Оптом нархи: " + str(data[2]) + " сўм, дона нархи: " + str(data[3]) + " сўм\nМаҳсулотни ўчириш:",
                                                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Ўчириш", callback_data=data[0])]]))
                except Exception as e:
                    print(str(e))
                return DEL_TOVAR


def add_tovar(update, context):
    chat_id = str(update.message.from_user.id)
    today = str(datetime.now().time().second) + '-' + str(datetime.now().time().minute) + '-' + str(datetime.now().time().hour)
    date = str(datetime.now().date().day) + '-' + str(datetime.now().date().month) + '-' + str(datetime.now().date().year)
    kod = today + "_" + date
    admin_tovar[chat_id]['tovar'].update({'photoName': admin_tovar[chat_id]['tovar']['nomi'] + " " + kod})
    status = admin_tovar[chat_id]['tovar']['add_status']
    try:
        file = context.bot.getFile(update.message.photo[-1].file_id)
        file.download('images/' + admin_tovar[chat_id]['tovar']['season'] + "/" + admin_tovar[chat_id]['tovar']['category'] +
                      "/" + admin_tovar[chat_id]['tovar']['nomi'] + " " + kod + '.jpg')
        if status['Оптом'] == '1' and status['Дона'] == '0':
            update.message.reply_text("Расм қўшилди. Энди унинг оптом нархини киритинг:")
        elif status['Оптом'] == '1' and status['Дона'] == '1':
            update.message.reply_text("Расм қўшилди. Энди унинг оптом ва дона нархларини намунадагидек киритинг:\n"
                                      "Шарт: <оптом нарх> <дона нарх>\nНамуна: 1000 3000")
        elif status['Оптом'] == '0' and status['Дона'] == '1':
            update.message.reply_text("Расм қўшилди. Энди унинг дона нархини киритинг:")
    except Exception as e:
        print(str(e))
    return ADD_TOVAR_NARX


def add_tovar_narx(update, context):
    chat_id = str(update.message.from_user.id)
    status = admin_tovar[chat_id]['tovar']['add_status']
    narx = ''
    obyekt = Tovar()
    ob = Razmer()
    sizes = ob.select_razmer(admin_tovar[chat_id]['tovar']['category'])
    path = "images/" + admin_tovar[chat_id]['tovar']['season'] + "/" + admin_tovar[chat_id]['tovar']['category'] + "/" + \
           admin_tovar[chat_id]['tovar']['photoName'] + ".jpg"

    obyekt_size = Razmer()
    razmerlar = obyekt_size.select_razmer(admin_tovar[chat_id]['tovar']['category'])

    if status['Оптом'] == '1' and status['Дона'] == '1':
        narx = update.message.text.split(' ')
        if not narx[0].isdigit() and narx[1].isdigit():
            update.message.reply_text("Нархларни тўғри киритинг!")
            return ADD_TOVAR_NARX
        else:
            for size in razmerlar:
                if size[0] in admin_tovar[chat_id]['tovar']['razmeri']:
                    obyekt.insert_tovar(admin_tovar[chat_id]['tovar']['nomi'], admin_tovar[chat_id]['tovar']['season'],
                                        admin_tovar[chat_id]['tovar']['category'], size[0], path, str(narx[0]), str(narx[1]))
                else:
                    obyekt.insert_tovar(admin_tovar[chat_id]['tovar']['nomi'], admin_tovar[chat_id]['tovar']['season'],
                                        admin_tovar[chat_id]['tovar']['category'], size[0], path, str(narx[0]), '0')
    else:
        narx = update.message.text
        if not narx.isdigit():
            update.message.reply_text("Нархларни тўғри киритинг!")
            return ADD_TOVAR_NARX
        if status['Оптом'] == '1':
            for size in razmerlar:
                obyekt.insert_tovar(admin_tovar[chat_id]['tovar']['nomi'], admin_tovar[chat_id]['tovar']['season'],
                                    admin_tovar[chat_id]['tovar']['category'], size[0], path, str(narx), '0')
        else:
            for size in admin_tovar[chat_id]['tovar']['razmeri']:
                obyekt.insert_tovar(admin_tovar[chat_id]['tovar']['nomi'], admin_tovar[chat_id]['tovar']['season'],
                                    admin_tovar[chat_id]['tovar']['category'], size, path, '0', str(narx))

    update.message.reply_text("Янги маҳсулот қўшилди.", reply_markup=ReplyKeyboardMarkup([
        ["Янги товар қўшиш"], ["Мавжуд товарни ўчириш"], ["Орқага"]
    ], resize_keyboard=True))
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


def order_type(update, context):
    update.message.reply_text("Тўлов турини танланг:", reply_markup=ReplyKeyboardMarkup([
        ['Нақд', 'Пластик'], ['Орқага']
    ], resize_keyboard=True))
    return ADMIN_ORDER_TYPE


def buyurtmalar(update, context):
    chat_id = str(update.message.from_user.id)
    admin_tovar[chat_id]['order_type'] = update.message.text.lower()
    update.message.reply_text("Буюртмалар ҳолатлари:", reply_markup=ReplyKeyboardMarkup([
        ["Тасдиқлаш ҳолатидагилар"], ["Тасдиқланганлар", "Жўнатилганлар"], ["Манзилга етиб борганлар"], ["Орқага"]
    ], resize_keyboard=True))
    return ADMIN_BUYURTMA


def order_steps(update, context):
    chat_id = str(update.message.from_user.id)
    status = order_holat(update.message.text)
    obyekt = Order()
    malumotlar = obyekt.select_orders(status, admin_tovar[chat_id]['order_type'])
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
    if not malumotlar:
        update.message.reply_text("Буюртмалар йўқ", reply_markup=ReplyKeyboardMarkup([["Орқага"]], resize_keyboard=True))
    else:
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
    obyekt = Razmer()
    obyekt.razmer_add(str(size), step)
    update.message.reply_text("Янги ўлчам қўшилди. Ўлчам турларидан бирини танланг.", reply_markup=razmer_category)
    return ADMIN_RAZMER


def del_razmer(update, context):
    razmer_id = update.message.text
    obyekt = Razmer()
    obyekt.razmer_del(razmer_id)
    update.message.reply_text("Ўлчам ўчирилди. Ўлчам турларидан бирини танланг.", reply_markup=razmer_category)
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
                                      reply_markup=ReplyKeyboardMarkup([["Орқага"]], resize_keyboard=True))
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


def delivery_crud(update, context):
    update.message.reply_text("Доставкалар ҳақида маълумотларни киритинг:", reply_markup=ReplyKeyboardRemove(remove_keyboard=True))
    return DELIVERY_ADD


def delivery_add(update, context):
    chat_id = str(update.message.from_user.id)
    try:
        with open('delivery.txt', 'w') as fayl:
            fayl.write(update.message.text)
    except Exception as e:
        update.message.reply_text("Матн формати тўғри келмайди")
        return DELIVERY_ADD
    if check_admin(chat_id):
        update.message.reply_text("Маълумот киритилди.", reply_markup=admin_menyu)
    else:
        update.message.reply_text("Маълумот киритилди.", reply_markup=super_menyu)
    return ADMIN_MENYU


def dict_elements(update, context):
    context.bot.send_message(chat_id='590924106', text=str(len(admin_tovar)) + " " + str(len(customer_data)))


def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # dispatcher.add_handler(CommandHandler('start', start))

    controller = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
        ],
        states={
            ADMIN_CRUD: [
                MessageHandler(Filters.regex('^(' + "Янги админ қўшиш" + ')$'), admin_crud),
                MessageHandler(Filters.regex('^(' + "Мавжуд админни ўчириш" + ')$'), admin_crud),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
            ],
            ADD_ADMIN: [
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), admin_nazorat),
                MessageHandler(Filters.text, add_admin)
            ],
            DEL_ADMIN: [
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), admin_nazorat),
                MessageHandler(Filters.text, del_admin)
            ],
            STATE_FISH: [MessageHandler(Filters.text, f_i_sh)],
            STATE_NUMBER: [MessageHandler(Filters.contact, number)],
            STATE_LOCATION: [
                MessageHandler(Filters.location, location),
                MessageHandler(Filters.regex('^(' + "Кейинроқ юбориш" + ')$'), keyinroq)
            ],
            STATE_CARD: [MessageHandler(Filters.text, card)],
            STATE_XARID: [
                MessageHandler(Filters.regex('^(' + "Оптом" + ')$'), xarid),
                MessageHandler(Filters.regex('^(' + "Донага" + ')$'), xarid)
            ],
            STATE_MENYU: [
                MessageHandler(Filters.regex('^(' + "Савдо қилиш" + ')$'), savdo),
                MessageHandler(Filters.regex('^(' + "Маълумотларим" + ')$'), user),
                MessageHandler(Filters.regex('^(' + "Саватча" + ')$'), savatcha),
                MessageHandler(Filters.regex('^(' + "Буюртмалар ҳолатини текшириш" + ')$'), order),
                MessageHandler(Filters.regex('^(' + "Доставкалар ҳақида маълумот" + ')$'), delivery),
                MessageHandler(Filters.regex('^(' + "Биз ҳақимизда" + ')$'), info),
                MessageHandler(Filters.regex('^(' + "Aлоқа" + ')$'), contact),
            ],
            STATE_USER: [
                MessageHandler(Filters.regex('^(' + "Ф. И. Ш" + ')$'), userData),
                MessageHandler(Filters.regex('^(' + "Телефон рақам" + ')$'), userData),
                MessageHandler(Filters.regex('^(' + "Манзил" + ')$'), userData),
                MessageHandler(Filters.regex('^(' + "Карта рақам" + ')$'), userData),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
            ],
            STATE_USER2: [
                MessageHandler(Filters.regex('^(' + "Ўзгартириш" + ')$'), change),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), user),
                MessageHandler(Filters.location, add_location)
            ],
            STATE_USER3: [
                MessageHandler(Filters.location, change_user_locate),
                MessageHandler(Filters.contact, change_user_phone),
                MessageHandler(Filters.text, change_user_data)
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
            ADMIN_TOVAR_STATUS: [
                CallbackQueryHandler(status_together),
                MessageHandler(Filters.regex('^(' + "Менюга қайтиш" + ')$'), menyu)
            ],
            TOGETHER: [
                CallbackQueryHandler(together),
                MessageHandler(Filters.regex('^(' + "Менюга қайтиш" + ')$'), menyu)
            ],
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
            ANSWER_CHECKOUT: [
                PreCheckoutQueryHandler(answer_precheckout),
                MessageHandler(Filters.successful_payment, successful_payment_callback),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
            ],
            STATE_TURI_TOLOV: [
                CallbackQueryHandler(savat_tolov),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
            ],
            STATE_BASKET_TOLOV: [
                CallbackQueryHandler(karta_tolov),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
            ],
            STATE_BUYURTMA: [MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)],
            ADMIN_MENYU: [
                MessageHandler(Filters.regex('^(' + "Товарлар" + ')$'), tovar),
                MessageHandler(Filters.regex('^(' + "Буюртмалар" + ')$'), order_type),
                MessageHandler(Filters.regex('^(' + "Ўлчамлар" + ')$'), fasl),
                MessageHandler(Filters.regex('^(' + "Aдмин Назорат" + ')$'), admin_nazorat),
                MessageHandler(Filters.regex('^(' + "Доставкалар ҳақида маълумот" + ')$'), delivery),
                CommandHandler('countData', dict_elements)
            ],
            ADMIN_TOVAR: [
                MessageHandler(Filters.regex('^(' + "Янги товар қўшиш" + ')$'), fasl_tanlash),
                MessageHandler(Filters.regex('^(' + "Мавжуд товарни ўчириш" + ')$'), fasl_tanlash),
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
            ADMIN_ORDER_TYPE: [
                MessageHandler(Filters.regex('^(' + "Нақд" + ')$'), buyurtmalar),
                MessageHandler(Filters.regex('^(' + "Пластик" + ')$'), buyurtmalar),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
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
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu)
            ],
            RAZMER_CRUD: [
                MessageHandler(Filters.regex('^(' + "Янги ўлчам қўшиш" + ')$'), razmer_crud),
                MessageHandler(Filters.regex('^(' + "Мавжуд ўлчамни ўчириш" + ')$'), razmer_crud),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), fasl)
            ],
            ADD_RAZMER: [MessageHandler(Filters.text, add_razmer)],
            DEL_RAZMER: [MessageHandler(Filters.text, del_razmer)],
            DELIVERY_CRUD: [
                MessageHandler(Filters.regex('^(' + "Ўзгартириш" + ')$'), delivery_crud),
                MessageHandler(Filters.regex('^(' + "Орқага" + ')$'), menyu),
            ],
            DELIVERY_ADD: [
                MessageHandler(Filters.text, delivery_add),
            ]
        },
        fallbacks=[
            CommandHandler('start', start),
        ]
    )

    dispatcher.add_handler(controller)
    dispatcher.add_handler(PreCheckoutQueryHandler(answer_precheckout))
    dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))
    dispatcher.add_handler(MessageHandler(Filters.text, action))
    updater.start_polling()
    updater.idle()


customer_menyu = ReplyKeyboardMarkup([
    ['Савдо қилиш', "Маълумотларим"], ["Саватча"], ["Буюртмалар ҳолатини текшириш"],
    ["Доставкалар ҳақида маълумот"], ["Биз ҳақимизда", "Aлоқа"]
], resize_keyboard=True)

admin_menyu = ReplyKeyboardMarkup([["Товарлар", "Буюртмалар"], ["Ўлчамлар"], ["Доставкалар ҳақида маълумот"]], resize_keyboard=True)

super_menyu = ReplyKeyboardMarkup([["Товарлар", "Буюртмалар"], ["Ўлчамлар", "Aдмин Назорат"], ["Доставкалар ҳақида маълумот"]], resize_keyboard=True)

razmer_category = ReplyKeyboardMarkup([['Болшимерка', "Маламерка"], ["Турк ўлчамлар"], ["Орқага"]], resize_keyboard=True)

customer_malumotlari = ReplyKeyboardMarkup([['Ф. И. Ш', "Телефон рақам"], ["Карта рақам", "Манзил"], ["Орқага"]], resize_keyboard=True)

if __name__ == '__main__':
    main()