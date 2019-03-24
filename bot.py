import os
import requests
import logging
from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.utils.helpers import escape_markdown

# Enable logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.WARNING)
logger = logging.getLogger(__name__)

# Define a few command handlers

def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def start(update, context):
    update.message.reply_text("""
        This bot operates similar to the @wiki bot.
        Type the bot's name, then type your search term.
        """)

def help(update, context):
    update.message.reply_text("""
        In fact, the bot just uses the '''wbsearchentitis''' module of the Wikibase MediaWiki API extension.
        The bot is not able to search for properties (P-entities) and lexemes (L-entities)
        """)
    
def construct(json_result):
    return InlineQueryResultArticle(
        id=uuid4(),
        title = json_result['label']  + ' (' + json_result['match']['text'] + ')',
        description = json_result.get('description'),
        url = json_result['concepturi'],
        input_message_content=InputTextMessageContent(json_result['concepturi'], parse_mode=ParseMode.HTML)
    )
    
def inlinequery(update, context):
    query = update.inline_query.query
    url = 'https://www.wikidata.org/w/api.php?'
    params = dict(
        action='wbsearchentities',
        format='json',
        language='en',
        uselang='en',
        type='item',
        search=query
    )
    response = requests.get(url=url, params=params).json() 
    json_results = response['search']
    
    results = map(construct, json_results)
    update.inline_query.answer(results)


def main():
    updater = Updater(os.environ['TELEGRAM_TOKEN'], use_context=True)
    dp = updater.dispatcher

    dp.add_error_handler(error)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(InlineQueryHandler(inlinequery))

    updater.start_polling()
    updater.idle()

    
if __name__ == '__main__':
    main()

