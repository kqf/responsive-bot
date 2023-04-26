from environs import Env


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
