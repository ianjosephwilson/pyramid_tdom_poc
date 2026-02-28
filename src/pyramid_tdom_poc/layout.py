from .types import TDOM
from .components import (
    UserStatus,
    RouteDisplay,
)


def Header() -> TDOM:
    return (
        t'<div class="header pa2 ma0 w-100 bb-2 bb bw2 b--gray">'
        t"TDOM Proof of Concept"
        t"<{UserStatus} />"
        t"</div>"
    )


def Footer() -> TDOM:
    # This should pull the request from the system kwargs we put in the renderer by subclassing.
    return t"<div><{RouteDisplay} /></div>"


def make_layout_t(
    request: object, title: str, body_t: TDOM, extra_styles: TDOM | None = None
) -> TDOM:
    return (
        t"<!doctype html>"
        t"""<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel=stylesheet href="/assets/tachyons.css">
    <title>{title}</title>
    <style>
        body {{margin: 0; padding: 0}}
    </style>
    {extra_styles}
  </head>
  <body>
  <{Header} />
  {body_t}
  <{Footer} />
  </body>
</html>"""
    )
