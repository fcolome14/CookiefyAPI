import gettext
import os
from fastapi import Request

# Path to the locales directory
LOCALES_DIR = os.path.join(os.path.dirname(__file__), "../locales")

def get_locale(request: Request) -> str:
    """Get user language from the Accept-Language header (default to 'en')."""
    if isinstance(request, Request):
        return request.headers.get("Accept-Language", "en").split(",")[0].strip()
    else:
        return "en"

def get_translator(locale: str):
    """Return the translation object based on the user's locale."""
    return gettext.translation(
        "messages", localedir=LOCALES_DIR, languages=[locale], fallback=True
    )

def translate(request: Request):
    """Install the translator for the current request."""
    locale = get_locale(request)
    translator = get_translator(locale)
    translator.install()
    return translator.gettext  # Shortcut for translation (_)
