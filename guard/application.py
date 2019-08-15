from .model import Access
from . import templates

import logging
from fnmatch import fnmatchcase
from urllib.request import urlopen
from urllib.parse import urlencode

from pyinflux.parser import LineParser
from flask import request, redirect, session, url_for, make_response, Response
from werkzeug.exceptions import InternalServerError, Forbidden, Unauthorized, PreconditionFailed


def make_app(app, config):
    cookiename = config['cookiename']

    @app.route("/", methods=["POST", "GET"])
    def index():
        if "valid" not in session:
            return redirect(url_for("login"))

        if request.method == "POST":
            Access.create(token=request.form["token"],
                          pattern=request.form["pattern"],
                          comment=request.form["comment"])
        return templates.index(config)

    @app.route("/delete", methods=["POST"])
    def delete():
        if "valid" not in session:
            return redirect(url_for("login"))
        Access.delete().where(Access.id == int(request.form["id"])).execute()
        return redirect(url_for("index"))

    @app.route("/logout")
    def logout():
        del session["valid"]
        return redirect(url_for("login"))

    @app.route("/login", methods=["POST", "GET"])
    def login():
        if request.method == "POST":
            if "secret" in request.form and \
                            request.form["secret"] == config["adminsecret"]:
                logging.info("Login successful")
                session["valid"] = True
                return redirect(url_for("index"))
            else:
                logging.info("Login failed")
                return redirect(url_for("login"))
        else:
            return templates.login()

    @app.route("/write/<token>", methods=["POST"])
    @app.route("/write", methods=["POST"])
    def write(token=None):
        # Find token cookie in request
        if not token:
            token = request.cookies.get(cookiename)

        valid_access_patterns = tuple(map(lambda x: x[0],
                                        Access.select(Access.pattern).where(Access.token == token).tuples()))
        if not valid_access_patterns:
            return make_response("Token {} is not configured\n".format(token), Forbidden.code)

        # Read request
        database = request.args.get("db")
        if not database:
            return make_response("No database name given in parameter 'db'\n", PreconditionFailed.code)

        # Read data
        data = request.get_data(as_text=False)
        data_text = data.decode(request.charset, request.encoding_errors)

        # validate access
        for line in data_text.split("\n"):
            identifier = database + '.' + LineParser.parse_identifier(line)
            if not any(map(lambda pattern: fnmatchcase(identifier, pattern), valid_access_patterns)):
                logging.info("Reject write to %s", identifier)
                return make_response("Invalid path: {}\n".format(identifier), Unauthorized.code)


        # checks passed, forward the request
        params = {'db': database}
        if request.args.get("rp"):
            params["rp"] = request.args.get("rp")
        if request.args.get("precision"):
            params["precision"] = request.args.get("precision")
        if request.args.get("consistency"):
            params["consistency"] = request.args.get("consistency")

        if config.get("username"):
            params["u"] = config["username"]
        if config.get("password"):
            params["p"] = config["password"]

        url = config['url'] + "?" + urlencode(params)
        try:
            with urlopen(url, data) as resp:
                if logging.root.isEnabledFor(logging.INFO):
                    logging.info("Forwarded request to database '%s' for '%s' with '%s': %s",
                                 database, request.remote_addr, token, data_text)
                return Response(resp.fp, status=resp.getcode())
        except:
            logging.exception("Request failed for:\n%s", data)
            return make_response("Failed", InternalServerError.code)
