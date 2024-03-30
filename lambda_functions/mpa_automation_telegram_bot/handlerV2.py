from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, ApplicationBuilder, ContextTypes

# Define constants for the four states in the conversation.
CREDENTIALS, AUTOMATION, INPUTS, HISTORY = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Entry point of the bot, send a message and go to the CREDENTIALS state.
    await update.message.reply_text('Hi! I am your bot. Send /Credentials, /Automation, /Inputs, /History to continue.')
    return CREDENTIALS

async def credentials(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Handle '/Credentials' command and go to the AUTOMATION state.
    await update.message.reply_text('You are in /Credentials. Send /Automation to continue.')
    return AUTOMATION

async def automation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Handle '/Automation' command and go to the INPUTS state.
    await update.message.reply_text('You are in /Automation. Send /Inputs to continue.')
    return INPUTS

async def inputs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Handle '/Inputs' command and go to the HISTORY state.
    await update.message.reply_text('You are in /Inputs. Send /History to continue.')
    return HISTORY

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Handle '/History' command and end the conversation.
    await update.message.reply_text('You are in /History. Conversation ended.')
    return ConversationHandler.END

def main() -> None:
    token = "6508013389:AAGRHD3-rUwNaKyVzNu-H-CvL1uxSf8j02w"
    application = ApplicationBuilder().token(token).build()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CREDENTIALS: [CommandHandler('Credentials', credentials)],
            AUTOMATION: [CommandHandler('Automation', automation)],
            INPUTS: [CommandHandler('Inputs', inputs)],
            HISTORY: [CommandHandler('History', history)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
