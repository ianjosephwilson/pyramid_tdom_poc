import time
import os

from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPFound, HTTPException

from pyramid.session import SignedCookieSessionFactory
from .types import TDOM
from .layout import make_layout_t


def home_view(request: object) -> TDOM:
    seconds = time.time()
    theme_name = "theme-new-year" if int(seconds) % 3 == 1 else "theme-default"
    return make_layout_t(
        request, "Home", t"<{Body} theme_name={theme_name}>Extra Text</{Body}>"
    )


def Body(children, theme_name="theme-default") -> TDOM:
    styles = {"color": "red"} if theme_name == "theme-new-year" else {"color": "blue"}

    def runtime_callback():
        return "TDOM"

    return t"<div><h1 style={styles}>Welcome to {runtime_callback:callback} Proof of Concept!</h1>{children}</div>"


def prompt_login(request: object) -> TDOM | HTTPException:
    if request.session.get("user", None):
        return HTTPFound(request.route_path("home"))
    else:
        login_url = request.route_path("login")
        body_t = (
            t'<div class="w-7 ma2">'
            t"<h2>Login Form</h2>"
            t"<form method=post action={login_url}>"
            t"<p>A random account will be created for you.</p>"
            t'<div><button type="submit">Login</button></div>'
            t"</form>"
            t"</div>"
        )
        return make_layout_t(request, "Login", body_t)


def process_login(request: object) -> HTTPException:
    request.session["user"] = (("name", f"User #{int(time.time())}"),)
    return HTTPFound(request.route_path("home"))


def logout(request: object) -> HTTPException:
    request.session.pop("user", None)
    return HTTPFound(request.route_path("home"))


def main():
    app_session_factory = SignedCookieSessionFactory(os.environ["SESSION_SECRET"])
    with Configurator() as config:
        config.set_session_factory(app_session_factory)

        config.include("pyramid_tdom")

        config.add_route("logout", "/logout")
        config.add_route("login", "/login")
        config.add_route("home", "/")
        config.add_route("usage", "/usage")

        config.add_view(
            prompt_login, route_name="login", renderer="tdom", request_method="GET"
        )
        config.add_view(
            process_login, route_name="login", renderer="tdom", request_method="POST"
        )
        config.add_view(logout, route_name="logout", request_method="POST")
        config.add_view(home_view, route_name="home", renderer="tdom")
        config.add_view(".usage.usage_view", route_name="usage", renderer="tdom")

        config.include(".asset")
        app = config.make_wsgi_app()

    return app
