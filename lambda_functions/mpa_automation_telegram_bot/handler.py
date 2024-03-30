import logging
from telegram import Update,ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger()
token = "6508013389:AAGRHD3-rUwNaKyVzNu-H-CvL1uxSf8j02w"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # you can add multiple options here
    custom_keyboard = [['/Credentials', '/Automation'], ['/Inputs', '/History']]
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
                                   "Inserisci API KEY e API SECRET in un messaggio separando le informazioni con | \n"
                                   "e.g: (*****|*****)",parse_mode='MarkdownV2')
async def handle_credentials(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_reply = update.message.text
    api_key, api_secret = user_reply.split('|')
    credentials = {}
    credentials['API_KEY'] = api_key
    credentials['API_SECRET'] = api_secret
    logging.info(credentials)
    await update.message.reply_text(text="Credentials stored successfully.")
async def manage_automation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="AUTOMATION SECTION\n",parse_mode='MarkdownV2')

async def manage_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="HISTORY SECTION\n",parse_mode='MarkdownV2')

async def manage_inputs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text="INPUTS SECTION\n",parse_mode='MarkdownV2')
if __name__ == '__main__':
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", main_menu))
    application.add_handler(CommandHandler("Credentials", add_credentials))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_credentials))
    application.add_handler(CommandHandler("Automation", manage_automation))
    application.add_handler(CommandHandler("Inputs", manage_inputs))
    application.add_handler(CommandHandler("History", manage_history))
application.run_polling()
