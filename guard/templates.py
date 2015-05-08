from . import model

from typing import Iterable

from lxml.builder import E
from lxml import etree
from flask import url_for


def _html(title: str, body: etree.Element) -> str:
    return etree.tostring(E.html(
        E.head(E.title(title)),
        E.body(body)
    ), encoding='utf-8')


def login() -> str:
    return _html("Login", E.form(
        E.input(type="password", name="secret", placeholder="Secret admin token"),
        E.button("login", type="submit"),
        method="POST"
    ))


def _index_access(accesses: Iterable[model.Access]):
    return map(lambda access: (
        E.tr(
            E.td(access.token),
            E.td(access.pattern),
            E.td(str(access.create_date)),
            E.td(access.comment),
            E.td(
                E.form(
                    E.input(type="hidden", name="id", value=str(access.id)),
                    E.button("X", title="Delete", type="submit"),
                    method="POST", action=url_for("delete")))
        )
    ), accesses)


def index(serverport: str, cookiename: str) -> str:
    return _html(
        "Manage access tokens",
        E.div(
            E.p(E.a("Logout", href=url_for("logout"))),
            E.p("Call the write-service like: ",
                E.pre("http://thisMachine:{}/write".format(serverport)),
                "with the token in a cookie named {}".format(cookiename)),
            E.p("Or directly in the url: ",
                E.pre("http://thisMachine:{}/write/<token>".format(serverport))),
            E.form(
                E.input(type="hidden", name="action", value="create"),
                E.input(name="token", placeholder="Token secret"),
                E.input(name="pattern", placeholder="Paths pattern"),
                E.input(name="comment", placeholder="Comment"),
                E.button("Create", type="submit"), method="POST"),
            E.hr(),
            E.table(
                E.tr(
                    E.th("cookie: " + cookiename + " value"), E.th("Pattern"),
                    E.th("Create Date"), E.th("Comment"), E.th()
                ), border="1", style="width: 100%",
                *_index_access(model.Access.select().order_by(model.Access.create_date))
            ))
    )
