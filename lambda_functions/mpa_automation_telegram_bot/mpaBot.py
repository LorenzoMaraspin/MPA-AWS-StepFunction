from aws_lambda_powertools import Logger
from telegram import Update,ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler
from aws_operativity import create_secret, create_dynamodb_item, get_item_dynamodb, update_item_dynamodb
logger = Logger()
token = "6508013389:AAGRHD3-rUwNaKyVzNu-H-CvL1uxSf8j02w"

API_KEY, API_SECRET_KEY = range(2)
FLAG_AUTOMATION = range(1)
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # you can add multiple options here
    custom_keyboard = [['/credentials', '/automation', '/Inputs']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard,one_time_keyboard=True, input_field_placeholder="Select a command")

    chat = update.effective_chat
    if chat:
        await context.bot.send_message(
            chat_id=chat.id,
            text="Hello! Welcome to MPA AutomationBot for Bybit Trading \n"
                 "Here you can perform some actions like setup credentials, setup inputs"
                 "Coming Soon... we will have also history and automation management",
            reply_markup=reply_markup
        )

async def add_credentials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="CREDENTIALS SECTION\n"
                                         "Inserire i secret di Bybit per la gestion dei trade MPA\n"
                                         "Inserisci la tua API KEY: ",parse_mode='MarkdownV2')
    return API_KEY

async def api_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['api_key'] = update.message.text
    await update.message.reply_text('Inserisci la tua API SECRET KEY:')
    return API_SECRET_KEY

async def api_secret_key(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['api_secret_key'] = update.message.text
    user = update.message.from_user
    secret = {"api_key": context.user_data['api_key'], "api_secret": context.user_data['api_secret_key']}
    create_secret(secret_name='telegram-bot-secret', secret=secret)
    create_dynamodb_item(user)
    await update.message.reply_text(f"USERNAME: {user} \nAPI KEY: {context.user_data['api_key']}\nAPI SECRET KEY: {context.user_data['api_secret_key']}")

    return ConversationHandler.END

async def manage_automation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    current_item = get_item_dynamodb(user.id)
    await update.message.reply_text(text=f"AUTOMATION SECTION\n"
                                         f"Bybit Trading Automation Flag: {current_item}\n", parse_mode='MarkdownV2')
    return FLAG_AUTOMATION

async def change_automation_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['flag_automation'] = update.message.text
    user = update.message.from_user
    update_item_dynamodb(user)
    await update.message.reply_text(text="Automation status change", parse_mode='MarkdownV2')
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Operazione annullata.')
    return ConversationHandler.END

if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("menu", main_menu))
    cred_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("credentials", add_credentials)],
        states={
            API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, api_key)],
            API_SECRET_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, api_secret_key)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    automation_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("automation", manage_automation)],
        states={
            FLAG_AUTOMATION: [MessageHandler(filters.Regex('^(True|False)$'), change_automation_status)]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    application.add_handler(cred_conv_handler)
    application.add_handler(automation_conv_handler)
    application.run_polling()