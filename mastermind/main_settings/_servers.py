import os

SERVER_SETTINGS = ["local", "development", "production"]


def get_server_type():
    if os.environ["ENV_NAME"] in SERVER_SETTINGS:
        return os.environ["ENV_NAME"]
    else:
        raise Exception("Settings file not defined for this environtment")
