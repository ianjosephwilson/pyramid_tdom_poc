from .types import TDOM


def UserStatus(request, classes=("dib", "tr")) -> TDOM:
    user_info = request.session.get("user", None)
    if user_info:
        user = dict(user_info)
        status_t = t"""<div class={classes}>
    <span>Logged in as {user["name"]}</span>
    <form style="display: inline-block" method=post action={request.route_path("logout")}><button type=submit>Logout</button></form>
</div>"""
    else:
        status_t = t"""<div class={classes}>
    <span>Not logged in</span>
    <a href={request.route_path("login")}>Log.. me.. in..!</a>
</div>"""
    return status_t


def RouteDisplay(request) -> TDOM | None:
    if request.matched_route:
        return t"<div>The current route is {request.matched_route.name}.</div>"
    else:
        return None
