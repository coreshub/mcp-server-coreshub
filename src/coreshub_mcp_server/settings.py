import os


class Settings:
    base_url = "https://ai.coreshub.cn"

    access_key = os.getenv("QY_ACCESS_KEY_ID","")
    secret_key = os.getenv("QY_SECRET_ACCESS_KEY","")
    user_id = os.getenv("CORESHUB_USER_ID","")


# 创建单例配置实例
settings = Settings()
