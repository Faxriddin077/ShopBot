# from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, ChatAction, LabeledPrice
# from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters, CallbackQueryHandler, PreCheckoutQueryHandler
#
#
# def action(update, context):
#     context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
#
#
# def start(update, context):
#     chat_id = update.message.from_user.id
#     context.bot.send_message(chat_id, text="lalala")
#     try:
#         context.bot.send_invoice(
#             chat_id=chat_id, title="Sinov uchun", description='tafsilot', payload='some-invoice-payload-for-our-internal-use',
#             provider_token='371317599:TEST:1593104247527',
#             start_parameter='time-machine-example', currency='UZS', prices=[LabeledPrice("Tesst", 100 * 10000)]
#             # need_email=True, need_name=True, need_phone_number=True, need_shipping_address=True, is_flexible=True
#         )
#     except Exception as e:
#         print(str(e))
#     context.bot.send_message(chat_id, text="lalalaaaaaaaa")
#     return 1
#
#
# def precheckout(update, context):
#     query = update.pre_checkout_query
#     if query.invoice_payload != 'some-invoice-payload-for-our-internal-use':
#         query.answer(ok=False, error_message="Something went wrong...")
#     else:
#         print(query, query.id)
#         query.answer(ok=True, pre_checkout_query_id=query.id)
#     return 2
#
#
# def success_payment(update, context):
#     update.message.reply_text("TAngkoyyy")
#
#
# def main():
#     updater = Updater('1146484244:AAHDSkZ9Xw7Sb1BU0HXaik-X_UUQaVcgu64', use_context=True)
#     dp = updater.dispatcher
#     dp.add_handler(CommandHandler("start", start))
#
#     # Add command handler to start the payment invoice
#     # dp.add_handler(CommandHandler("shipping", start_with_shipping_callback))
#     # dp.add_handler(CommandHandler("noshipping", start_without_shipping_callback))
#
#     # Optional handler if your product requires shipping
#     # dp.add_handler(ShippingQueryHandler(shipping_callback))
#
#     # Pre-checkout handler to final check
#     dp.add_handler(PreCheckoutQueryHandler(precheckout))
#
#     # Success! Notify your user!
#     dp.add_handler(MessageHandler(Filters.successful_payment, success_payment))
#
#     # controller = ConversationHandler(
#     #     entry_points=[CommandHandler('start', start)],
#     #     states={
#     #         1: PreCheckoutQueryHandler(precheckot),
#     #         2: MessageHandler(Filters.successful_payment, succes_payment)
#     #     },
#     #     fallbacks=[CommandHandler('start', start)]
#     # )
#     #
#     # dispatcher.add_handler(controller)
#     dp.add_handler(MessageHandler(Filters.text, action))
#     updater.start_polling()
#     updater.idle()
#
#
# if __name__ == '__main__':
#     main()


import logging

from telegram import (LabeledPrice, ShippingOption)
from telegram.ext import (Updater, CommandHandler, MessageHandler,
                          Filters, PreCheckoutQueryHandler, ShippingQueryHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start_callback(update, context):
    msg = "Use /shipping to get an invoice for shipping-payment, "
    msg += "or /noshipping for an invoice without shipping."
    update.message.reply_text(msg)


def start_with_shipping_callback(update, context):
    chat_id = update.message.chat_id
    title = "Payment Example"
    description = "Payment Example using python-telegram-bot"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    provider_token = "387026696:LIVE:5f3c045b5b9c7f8d29bdabad"
    start_parameter = "test-payment"
    currency = "UZS"
    price = 1
    # price * 100 so as to include 2 decimal points
    # check https://core.telegram.org/bots/payments#supported-currencies for more details
    prices = [LabeledPrice("Test", price * 12000)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    context.bot.send_invoice(chat_id, title, description, payload,
                             provider_token, start_parameter, currency, prices,
                             need_name=True, need_phone_number=True,
                             need_email=True, need_shipping_address=True, is_flexible=True)


def start_without_shipping_callback(update, context):
    chat_id = update.message.chat_id
    title = "Payment Example"
    description = "Пастдаги тугмачани босиш орқали сиз тўлов қилиш меюсига автоматик ўтасиз. У ерда сиз маълумотларингизни киритиб тўлов қилишингиз мумкин."
    # select a payload just for you to recognize its the donation from your bot
    payload = "Custom-Payload"
    # In order to get a provider_token see https://core.telegram.org/bots/payments#getting-a-token
    provider_token = "387026696:LIVE:5f3d00225b9c7f8d29bdabae"
    start_parameter = "PaymeStart"
    currency = "UZS"
    # price in dollars
    price = 100
    # price * 100 so as to include 2 decimal points
    prices = [LabeledPrice("Test", price * 12000)]

    # optionally pass need_name=True, need_phone_number=True,
    # need_email=True, need_shipping_address=True, is_flexible=True
    context.bot.send_invoice(chat_id, title, description, payload,
                             provider_token, start_parameter, currency, prices)


def shipping_callback(update, context):
    query = update.shipping_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'Custom-Payload':
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        options = list()
        # a single LabeledPrice
        options.append(ShippingOption('1', 'Shipping Option A', [LabeledPrice('A', 100)]))
        # an array of LabeledPrice objects
        price_list = [LabeledPrice('B1', 150), LabeledPrice('B2', 200)]
        options.append(ShippingOption('2', 'Shipping Option B', price_list))
        query.answer(ok=True, shipping_options=options)


# after (optional) shipping, it's the pre-checkout
def precheckout_callback(update, context):
    query = update.pre_checkout_query
    # check the payload, is this from your bot?
    if query.invoice_payload != 'Custom-Payload':
        # answer False pre_checkout_query
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        context.bot.answer_pre_checkout_query(ok=True, pre_checkout_query_id=query.id)
        # query.answer(ok=True, pre_checkout_query=query.id)


# finally, after contacting the payment provider...
def successful_payment_callback(update, context):
    # do something after successfully receiving payment?
    update.message.reply_text("Thank you for your payment!")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1356540633:AAEZapMeLvTNGtldPqW6ip0wd12kQ4fcuJo", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # simple start function
    dp.add_handler(CommandHandler("start", start_callback))

    # Add command handler to start the payment invoice
    dp.add_handler(CommandHandler("shipping", start_with_shipping_callback))
    dp.add_handler(CommandHandler("noshipping", start_without_shipping_callback))

    # Optional handler if your product requires shipping
    dp.add_handler(ShippingQueryHandler(shipping_callback))

    # Pre-checkout handler to final check
    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))

    # Success! Notify your user!
    dp.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
