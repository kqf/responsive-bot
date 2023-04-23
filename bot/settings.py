from environs import Env


class Config:
    def __init__(self):
        env = Env()
        env.read_env()
        self.token = env("TOKEN")
        self.admin_ids = env.list("ADMIN_IDS")
        self.thanks_stickers = env.list("THANKS_STICKERS")

        self.message_thanks = env.str("MESSAGE_THANKS")
        self.message_start = env.str("MESSAGE_START")
        self.message_help = env.str("MESSAGE_HELP")

        self.port = env.int("PORT", 8443)

        self.webhook = env.str("WEBHOOK_URL", None)
        if self.webhook is not None:
            self.webhook = f"{self.webhook}/{self.token}"


config = Config()
