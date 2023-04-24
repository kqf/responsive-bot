import logging
from functools import partial

from telegram.ext import Application, MessageHandler, filters

from bot.settings import config

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def _forward_to_admins(update, context, data):
    user_id = update.message.from_user.id
    for admin_id in config.admin_ids:
        message = await update.message.forward(admin_id)
        response = await context.bot.send_message(
            chat_id=admin_id,
            text="Please respond to this message to answer the question.",
        )
        data[f"response_{admin_id}"] = {
            "original_message_id": message.message_id,
            "message_id": response.message_id,
            "user_id": user_id,
        }


async def thanks(update, context, data):
    await _forward_to_admins(update, context, data)


async def handle_admin_reply(update, context, data):
    message_id = update.message.reply_to_message.message_id
    for admin_id in config.admin_ids:
        response = data.get(f"response_{admin_id}")
        if response is None:
            return

        if response["message_id"] != message_id:
            continue

        resp = f"Admin replied: {update.message.text}"
        await context.bot.send_message(chat_id=response["user_id"], text=resp)
        del data["response_{admin_id}"]


def main():
    app = Application.builder().token(config.token).build()
    data = {}
    app.add_handler(
        MessageHandler(
            ~filters.COMMAND & ~filters.REPLY, partial(thanks, data=data)
        )
    )
    app.add_handler(
        MessageHandler(
            filters.REPLY,
            partial(handle_admin_reply, data=data),
        ),
    )
    app.run_polling()


if __name__ == "__main__":
    main()
