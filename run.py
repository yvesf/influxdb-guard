#!/usr/bin/env python3
import os
import sys
import logging
from configparser import ConfigParser

from flask import Flask

from guard import application, model, proxyfix


def make_app(config):
    app = Flask("Guard")
    app.secret_key = config["Guard"]["Adminsecret"] + os.uname()[1]

    model.db.init(os.path.join(os.path.dirname(__file__), "db.sqlite"))
    model.db.connect()
    model.db.create_tables(filter(lambda t: not t.table_exists(), [model.Access]))

    log_format = "%(asctime)-15s %(levelname)s [%(module) 15s] %(message)s"
    if config["Guard"]["Debug"] == "true":
        logging.basicConfig(level=logging.INFO, format=log_format)
        logging.info("Running in DEBUG mode!")
    else:
        logging.basicConfig(level=logging.ERROR, format=log_format)
        logging.info("Running in production mode!")

    application.make_app(app, config["Guard"])

    app.wsgi_app = proxyfix.fix(app.wsgi_app)
    return app


def get_config(path: str = None) -> ConfigParser:
    config = ConfigParser()
    config["Guard"] = {
        'url': "http://localhost:8086/write",
        "port": "8001",
        "cookiename": "token",
        "adminsecret": "changeme",
        "gen_token_len": 22,
        "debug": "false",
    }
    if path is not None:
        config.read(path)
    return config


def start():
    if len(sys.argv) == 2:
        config = get_config(sys.argv[1])
        app = make_app(config)
        app.run(host="0.0.0.0", port=int(config["Guard"]["Port"]),
                debug=config["Guard"]["Debug"] == "true",
                use_reloader=config["Guard"]["Debug"] == "true")
    else:
        print("# {} >config.defaults.ini".format(sys.argv[0]))
        get_config().write(sys.stdout)
        sys.exit(1)


if __name__ == "__main__":
    start()
else:  # for running gunicorn3
    config = get_config('config')
    application = make_app(config)
