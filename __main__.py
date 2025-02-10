import json
import html
import logging
import os
import traceback

from typing import List
from pathlib import Path
from tempfile import NamedTemporaryFile

from telegram import ForceReply, Update, File
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import file_helper
import elo_calculator
import excel_util
from player_info import PlayerInfo

logger = logging.getLogger(__name__)

WAIT_CURRENT_RATING_INFO, WAIT_GAME_RECORDS = range(2)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)

    # traceback.format_exception returns the usual python message about an exception, but as a
    # list of strings rather than a single string, so we have to join them together.
    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    update_str = update.to_dict() if isinstance(update, Update) else str(update)
    message = (
        "An exception was raised while handling an update\n"
        f"<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
        "</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(tb_string)}</pre>"
    )

    # Finally, send the message
    await context.bot.send_message(
        chat_id=update.message.chat_id,
        text=message,
        parse_mode=ParseMode.HTML
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send a message when the command /start is issued."""
    user = update.effective_user

    await context.bot.send_document(
        update.message.chat_id,
        caption=f"{user.mention_html()}, привет !"
                f"\n\n"
                f"Пришли excel файл с текущим рейтингом. "
                f"\n\n"
                f"Если ранее уже считал рейтинг - можешь переслать сообщение с итоговым файлом."
                f"\n\n"
                f"Начать заново: /start"
                f"\n\n"
                f"Формат данных должен быть такой.",
        reply_markup=ForceReply(selective=True),
        document=open('example_current_rating_file.xlsx', 'rb'),
        parse_mode=ParseMode.HTML
    )

    return WAIT_CURRENT_RATING_INFO


async def on_current_rating_file_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    file: File = await context.bot.get_file(update.message.document)
    if not file_helper.is_file_size_ok(file.file_size):
        await update.message.reply_text(f'Слишком большой файл. Пришли другой.')
        return WAIT_CURRENT_RATING_INFO

    context.chat_data['rating_file_id'] = update.message.document.file_id

    await context.bot.send_document(
        update.message.chat_id,
        caption=f"Файл получил. Теперь пришли файл с результатами турнира."
                f"\n\n"
                f"Формат данных должен быть такой.",
        reply_markup=ForceReply(selective=True),
        document=open('example_game_record_file.xlsx', 'rb'),
        parse_mode=ParseMode.HTML
    )
    return WAIT_GAME_RECORDS


async def on_game_record_file_received(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    rating_file_id = context.chat_data['rating_file_id']
    rating_file: File = await context.bot.get_file(rating_file_id)

    known_players: List[PlayerInfo] = []
    with NamedTemporaryFile(suffix=Path(rating_file.file_path).name) as tmp_rating_file:
        tmp_rating_file_path = tmp_rating_file.name
        await rating_file.download_to_drive(custom_path=tmp_rating_file.name)
        known_players.extend(excel_util.read_players_from_excel(tmp_rating_file.name))

    game_record_file: File = await context.bot.get_file(update.message.document)
    # TODO: validate file size!!!

    game_records = []
    with NamedTemporaryFile(suffix=Path(game_record_file.file_path).name) as tmp_game_record_file:
        await game_record_file.download_to_drive(custom_path=tmp_game_record_file.name)
        game_records.extend(excel_util.read_game_records_from_excel(tmp_game_record_file.name))

    elo_calc = elo_calculator.EloCalculator(known_players)
    new_players = elo_calc.evaluate_game_records(game_records)

    with excel_util.players_to_excel(new_players) as excel_file_stream:
        await context.bot.send_document(
            update.message.chat_id,
            caption=f"Готово. Результат в файле",
            reply_markup=ForceReply(selective=True),
            document=excel_file_stream,
            parse_mode=ParseMode.HTML
        )

        return WAIT_CURRENT_RATING_INFO


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Что-то не то прислал. Давай начнем заново. Пришли файл с текущим рейтингом.')
    return WAIT_CURRENT_RATING_INFO


def main():
    # Enable logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    # set higher logging level for httpx to avoid all GET and POST requests being logged
    logging.getLogger("httpx").setLevel(logging.WARNING)

    token = os.environ['SECRET_BOT_TOKEN']

    application = Application.builder().token(token).build()

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAIT_CURRENT_RATING_INFO: [
                MessageHandler(filters.Document.ALL, on_current_rating_file_received)
            ],
            WAIT_GAME_RECORDS: [
                MessageHandler(filters.Document.ALL, on_game_record_file_received)
            ],
        },
        fallbacks=[MessageHandler(filters.ALL, fallback)],
    )

    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
