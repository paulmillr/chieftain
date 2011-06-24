from django.conf import settings as _settings
from board.middleware import set_session_defaults


def settings(request):
    """Adds settings dict to all requests with Context."""
    #print request
    return {"settings": _settings}


def session(request):
    # usually this is set by middleware, but
    # when user logs out, session destroys itself and we need to reinit it
    if "settings" not in request.session:
        set_session_defaults(request)
    user = request.user
    session = request.session
    settings = session["settings"]

    if session.get("no_captcha"):
        settings["no_captcha"] = True

    if user.is_authenticated():
        settings["is_mod"] = True
        if user.is_superuser:
            settings["is_admin"] = True
    return {
        "style": settings.pop("style", "photon"),
        "password": settings.pop("password", ""),
        "session": settings.copy(),
        "session_classes": " ".join(settings),
        "hidden": list(session["hidden"]),
        "feed": list(session["feed"]),
    }
