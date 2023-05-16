import logging
from functools import partial

from environs import Env
from telegram.ext import Application, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        env = Env()
        env.read_env()
        self.token = env("TOKEN", None)
        self.admin_ids = env.list("ADMIN_IDS", [])
        self.port = env.int("PORT", 8443)
        self.webhook = env.str("WEBHOOK_URL", None)
        if self.webhook is not None:
            self.webhook = f"{self.webhook}/{self.token}"


config = Config()


async def message(update, context, data):
    user_id = update.message.from_user.id
    for admin_id in config.admin_ids:
        message = await update.message.forward(admin_id)
        response = await context.bot.send_message(
            chat_id=admin_id,
            text="Please respond to this message to answer the question.",
        )
        data[admin_id] = {
            "original_message_id": message.message_id,
            "message_id": response.message_id,
            "user_id": user_id,
        }


async def handle_admin_reply(update, context, data):
    message_id = update.message.reply_to_message.message_id
    for admin_id in config.admin_ids:
        response = data.get(admin_id)
        if response is None:
            return

        # Make sure admins don't mix up
        if response["message_id"] != message_id:
            continue

        resp = f"Admin replied: {update.message.text}"
        await context.bot.send_message(chat_id=response["user_id"], text=resp)
        del data[admin_id]


def main():
    app = Application.builder().token(config.token).build()
    data = {}
    app.add_handler(
        MessageHandler(
            ~filters.COMMAND & ~filters.REPLY, partial(message, data=data)
        )
    )
    app.add_handler(
        MessageHandler(
            ~filters.COMMAND & filters.REPLY,
            partial(handle_admin_reply, data=data),
        ),
    )

    # No webhook -- run in the debug mode
    if config.webhook is None:
        app.start_polling()
        app.idle()
        return

    app.run_webhook(
        listen="0.0.0.0",
        port=config.port,
        url_path=config.token,
        webhook_url=config.webhook,
    )


if __name__ == "__main__":
    main()
