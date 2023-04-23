import logging


from telegram.ext import Application, MessageHandler, filters

from bot.settings import config


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def _forward_to_admins(update, context):
    for admin_id in config.admin_ids:
        message = await update.message.forward(admin_id)
        response = await context.bot.send_message(
            chat_id=admin_id,
            text="Please respond to this message to answer the question.",
        )
        context.user_data[f"response_{admin_id}"] = {
            "original_message_id": message.message_id,
            "message_id": response.message_id,
        }

    return "Responded"


async def thanks(update, context):
    await _forward_to_admins(update, context)


async def handle_admin_reply(update, context):
    print("Handling this")
    message_id = update.message.reply_to_message.message_id
    for admin_id in config.admin_ids:
        print(context.user_data)
        response = context.user_data.get(f"response_{admin_id}")
        # print(response)
        if response is None:
            return

        if response["message_id"] != message_id:
            continue
        original_message_id = context.user_data[f"response_{admin_id}"][
            "original_message_id"
        ]
        resp = f"Admin replied: {update.message.text}"
        await context.bot.send_message(chat_id=original_message_id, text=resp)


def main():
    app = Application.builder().token(config.token).build()
    app.add_handler(MessageHandler(~filters.COMMAND & ~filters.REPLY, thanks))
    app.add_handler(
        MessageHandler(
            filters.REPLY,
            handle_admin_reply,
        ),
    )
    app.run_polling()


if __name__ == "__main__":
    main()
