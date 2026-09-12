"""Presentation language only. Stored evidence and machine identifiers are never translated."""
import json
from functools import lru_cache
from pathlib import Path

LANGUAGES = ('en', 'tr')


def preference(name='language'):
    import brain
    conf = brain.settings()
    default = 'auto' if name == 'conversation_language' else 'tr'
    value = conf.get(name, default)
    valid = ('auto', *LANGUAGES) if name == 'conversation_language' else LANGUAGES
    return value if value in valid else default


@lru_cache(maxsize=2)
def catalog(language):
    return json.loads((Path(__file__).resolve().parents[1] / 'Locales' / (language+'.json')).read_text(encoding='utf-8'))


def t(literal):
    return catalog(preference())['messages'].get(literal, literal)


def conversation_instruction():
    value = preference('conversation_language')
    if value == 'auto':
        return ''
    return 'Raven language preference: respond in '+{'en':'English','tr':'Turkish'}[value]+', unless the user asks otherwise.\n'
