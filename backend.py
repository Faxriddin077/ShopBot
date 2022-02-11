import sqlite3
from telegram import InlineKeyboardButton
from conf import DB_NAME


class Customers:
    def __init__(self):
        self.con = sqlite3.connect(DB_NAME, check_same_thread=True)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

    def user_data_update(self, data, value, chat_id):
        query = "update customers set '" + data + "'='" + value + "' where chat_id='" + str(chat_id) + "'"
        self.cur.execute(query)
        self.con.commit()

    def select_user_xarid(self, chat_id):
        query = "select xarid_status from customers where chat_id='" + chat_id + "'"
        return self.cur.execute(query).fetchone()

    def select_location(self, chat_id):
        query = "select longitude, latitude from customers where chat_id='"+chat_id+"'"
        return self.cur.execute(query).fetchall()

    def check_customer(self, chat_id):
        query = "select count(chat_id) from customers where chat_id='" + chat_id + "'"
        return self.cur.execute(query).fetchone()

    def delete_customer(self, chat_id):
        query = "delete from customers where chat_id='"+chat_id+"'"
        self.cur.execute(query)
        self.con.commit()


class Razmer:
    def __init__(self):
        self.con = sqlite3.connect(DB_NAME, check_same_thread=True)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

    def select_razmer(self, turi):
        query = "select razmer from razmer where category='" + turi + "'"
        return self.cur.execute(query).fetchall()

    def select_razmer2(self, turi):
        query = "select razmer_id, razmer from razmer where category='" + turi + "'"
        return self.cur.execute(query).fetchall()

    def razmer_add(self, size, turi):
        query = "insert into razmer (category, razmer) values ('" + turi + "', '" + size + "')"
        self.cur.execute(query)
        self.con.commit()

    def razmer_del(self, id):
        query = "delete from razmer where razmer_id='" + id + "'"
        self.cur.execute(query)
        self.con.commit()


class Tovar:
    def __init__(self):
        self.con = sqlite3.connect(DB_NAME, check_same_thread=True)
        # self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

    def select_tovar(self, nomi, season, category, size):
        query = "select id, path, optom_sum, dona_sum from tovar where " \
                "nomi='"+nomi+"' and season='" + season + "' and category='" + category + "' and size='" + size + "'"
        return self.cur.execute(query).fetchall()

    def select_tovar_user(self, xarid_status, nomi, season, category, size):
        query = "select path, " + xarid_status + ", id from tovar where " \
                "nomi='" + nomi + "' and season='" + season + "' and category='" + category + "' and size='" + size + "' and '"+xarid_status+"'!=0"
        return self.cur.execute(query).fetchall()

    def delete_tovar(self, id):
        query = "delete from tovar where id='" + id + "'"
        self.cur.execute(query)
        self.con.commit()

    def insert_tovar(self, nomi, fasl, category, size, path, optom_s, dona_s):
        query = "insert into tovar (nomi, season, category, size, path, optom_sum, dona_sum) " \
                "values('" + nomi + "', '" + fasl + "', '" + category + "', '" + size + "','" + path + "', '" + optom_s + "', '" + dona_s + "')"
        self.cur.execute(query)
        self.con.commit()

    def select_tovar_nomlari(self, season):
        query = "select nomi from tovar_names where season='" + season + "'"
        return self.cur.execute(query).fetchall()


class Savatcha:
    def __init__(self):
        self.con = sqlite3.connect(DB_NAME, check_same_thread=True)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

    def insert_savat(self, user_id, tovar_id):
        query = "insert into basket (customer_id, tovar_id) values('" + user_id + "', '" + tovar_id + "')"
        self.cur.execute(query)
        self.con.commit()

    def select_tovar(self, user_id, xarid_turi):
        query = "SELECT path, " + xarid_turi + ", size, tovar_id from tovar INNER JOIN basket on " \
                                               "tovar.id=basket.tovar_id and basket.customer_id='" + user_id + "'"
        return self.cur.execute(query).fetchall()

    def select_aralash(self, xarid_turi, user_id):
        query = "SELECT tovar.nomi, tovar." + xarid_turi + ", customers.card_number from tovar inner join basket on tovar.id=basket.tovar_id " \
                                                "inner join customers on customers.chat_id=basket.customer_id and basket.customer_id='"+user_id+"'"
        return self.cur.execute(query).fetchall()

    def select_narx(self, xarid_turi, tovar_id):
        query = "select " + xarid_turi + " from tovar where id=" + tovar_id
        return self.cur.execute(query).fetchone()

    def delete_tovar(self, chat_id, tovar_id):
        query = "delete from basket where customer_id='"+chat_id+"' and tovar_id='"+tovar_id+"'"
        self.cur.execute(query)
        self.con.commit()


class Order:
    def __init__(self):
        self.con = sqlite3.connect(DB_NAME, check_same_thread=True)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

    def select_orders(self, status, type):
        query = "select user_id, tovar_id, id from order_table where status_order='"+status+"' and type_order='"+type+"'"
        return self.cur.execute(query).fetchall()

    def select_tovar(self, xarid_turi, user_id):
        query = "SELECT path, nomi, " + xarid_turi + ", category, size, status_order from tovar INNER JOIN order_table on " \
                                               "tovar.id=order_table.tovar_id and order_table.user_id='" + user_id + "'"
        return self.cur.execute(query).fetchall()

    def tovar_data(self, xarid_turi, tovar_id):
        query = "select path, nomi, " + xarid_turi + ", category, size from tovar where id='"+tovar_id+"'"
        return self.cur.execute(query).fetchall()

    def select_data(self, qaysi_data, order_id):
        query = "select " + qaysi_data + " from order_table where id='"+order_id+"'"
        return self.cur.execute(query).fetchone()

    def insert_order(self, user_id, tovar_id, type_order):
        query = "insert into order_table (user_id, tovar_id, type_order) values ('"+user_id+"', '"+tovar_id+"', '"+type_order+"')"
        self.cur.execute(query)
        self.con.commit()

    def update_status(self, status, order_id):
        query = "update order_table set status_order='"+status+"' where id='"+order_id+"'"
        self.cur.execute(query)
        self.con.commit()

    def delete_savat(self, user_id, tovar_id):
        query = "delete from basket where customer_id='"+user_id+"' and tovar_id='"+tovar_id+"'"
        self.cur.execute(query)
        self.con.commit()

    def delete_basket(self, user_id):
        query = "delete from basket where customer_id='"+user_id+"'"
        self.cur.execute(query)
        self.con.commit()


class Admins:
    def __init__(self):
        self.con = sqlite3.connect(DB_NAME, check_same_thread=True)
        self.con.row_factory = sqlite3.Row
        self.cur = self.con.cursor()

    def select_admin(self):
        query = "select * from admins"
        return self.cur.execute(query).fetchall()

    def insert_admin(self, admin_id):
        query = "insert into admins (admin_id) values ('"+admin_id+"')"
        self.cur.execute(query)
        self.con.commit()

    def delete_admin(self, admin_id):
        query = "delete from admins where id='"+admin_id+"'"
        self.cur.execute(query)
        self.con.commit()


def check_admin(admin_id):
    con = sqlite3.connect(DB_NAME, check_same_thread=True)
    cur = con.cursor()
    checker = cur.execute("select admin_id from admins where admin_id='"+admin_id+"'").fetchall()
    con.commit()
    if len(checker) == 1:
        return True
    else:
        return False


def show_razmer(turi):
    obyekt = Razmer()
    razmer = obyekt.select_razmer(turi)
    button = []
    tmp = []
    for x in razmer:
        button.append([InlineKeyboardButton(str(x['razmer']), callback_data=x['razmer'])])
    button.append([InlineKeyboardButton('Орқага', callback_data='showRazmer')])
    return button


def sticker_crud(category, statuses):
    obyekt = Razmer()
    razmer = obyekt.select_razmer(category)
    button = []
    tmp = []
    for x in razmer:
        for size, status in statuses.items():
            if x['razmer'] == size:
                if status == '1':
                    button.append([InlineKeyboardButton(str(x['razmer']) + '☑️', callback_data=x['razmer'])])
                    break
                else:
                    button.append([InlineKeyboardButton(str(x['razmer']), callback_data=x['razmer'])])
                    break
        else:
            button.append([InlineKeyboardButton(str(x['razmer']), callback_data=x['razmer'])])
    button.append([InlineKeyboardButton("Маҳсулот қўшиш", callback_data='addtovar')])
    return button


def buttons(text):
    qish = [
        [
            InlineKeyboardButton('Виязиний кофта', callback_data='виязиний кофта'),
            InlineKeyboardButton('Кардиган', callback_data='кардиган')
        ],
        [
            InlineKeyboardButton('Туника', callback_data='туника'),
            InlineKeyboardButton('Виязиний платье', callback_data='виязиний платье')
        ],
        [
            InlineKeyboardButton('Куртка', callback_data='куртка'),
            InlineKeyboardButton('Шим', callback_data='шим')
        ],
        [
            InlineKeyboardButton('Орқага', callback_data='showSize')
        ]
    ]

    yoz = [
        [
            InlineKeyboardButton('Кофта', callback_data='кофта'),
            InlineKeyboardButton('Туника', callback_data='туника')
        ],
        [
            InlineKeyboardButton('Рубашка', callback_data='рубашка'),
            InlineKeyboardButton('Футболка', callback_data='футболка')
        ],
        [
            InlineKeyboardButton('Платье', callback_data='платье'),
            InlineKeyboardButton('Шим', callback_data='шим')
        ],
        [
            InlineKeyboardButton('Орқага', callback_data='showSize')
        ]
    ]

    kuz_bahor = [
        [
            InlineKeyboardButton('Виязиний кофта', callback_data='виязиний платье'),
            InlineKeyboardButton('Кардиган', callback_data='кардиган')
        ],
        [
            InlineKeyboardButton('Туника', callback_data='туника'),
            InlineKeyboardButton('Виязиний платье', callback_data='виязиний платье')
        ],
        [
            InlineKeyboardButton('Шим', callback_data='шим')
        ],
        [
            InlineKeyboardButton('Орқага', callback_data='showSize')
        ]
    ]

    if text == "қиш":
        return qish
    elif text == "ёз":
        return yoz
    elif text == "куз-баҳор":
        return kuz_bahor


# obyekt = Admins()
# a = obyekt.select_admin()
# for x in a:
#     print(x[1])


# path = "images/qish/bolshimerka/2712231362020.jpg"
# obyekt = Tovar()
# obyekt.insert_tovar('tunika', 'yoz', 'malamerka', '44', 'path', '11', '22')
# obyekt.insert_tovar('tunika', 'qish', 'bolshimerka', '56', path, str(11), str(22))
# connect = sqlite3.connect("baza.db", check_same_thread=True)
# cursor = connect.cursor()
# data = cursor.execute("select longitude, latitude from customers where chat_id=590924106").fetchall()[0]
# print(data)
# obyekt = Order()
# print(obyekt.select_tovar("optom_sum", '590924106'))
# obyekt = Savatcha()
# narx = obyekt.select_narx('optom_sum', '22')[0]
# print(narx)
# a = """8600 1111 2222 3333 -> Sotuvchining karta raqami.\n
#             To'lovingiz muvaffaqiyatli bajarilishi uchun quyidagi amallarni bajaring:
#             1. Payme.uz yoki Click.uz dan ro'yxatdan o'ting.
#             2. Pastda ko'rsatilgan to'lov miqdorini - (8600 1111 2222 3333) "Abduraim" karta raqamiga o'tkazing.
#             3. "To'lov qildim!" tugmasini bosing.
#             4. Admin tomonidan karta raqamingiz va ismingiz mos kelishi tasdiqlanishini kuting.
#
#                 To'lov miqdori: 150000\n
#             Ushbu o'tkazma admin tomonidan navbati bilan 2 daqiqadan 1 soatgacha oraliqda tekshirilishi mumkin."""
#
# print(a)
# obyekt_razmer = Savatcha()
# a = obyekt_razmer.select_aralash('optom_sum', "590924106")
# print(a[0][0])
# # tovar_data = dict()
# tovar_data = obyekt.select_tovar('qish', 'bolshimerka', '56')
# for row in tovar_data:
#     print("id ", row[0], "ss")
#     print("path ", row[1], "ss")
#     print("optom ", row[2], "aa")
#     print("dona ", row[3])
#     print("\n")

# i = 1
# for x in razmerlar:
#     for y in x:
#         sonlar += str(i) + ". " + str(y) + "\n"
#         i += 1
# print(sonlar)
