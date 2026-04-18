# Localization

WarpDesk currently supports:

- English
- Spanish
- Catalan

## Source

Strings live in:

```text
src/warpdesk/i18n.py
```

## Resolution order

The app checks:

1. `LC_ALL`
2. `LC_MESSAGES`
3. `LANG`
4. `QLocale.system()`

Neutral locales such as `C` and `POSIX` are ignored so they do not override a real user locale.

## Adding a language

1. add a new dictionary in `MESSAGES`
2. keep keys aligned with the existing `en` set
3. test by launching with the locale forced

Example:

```bash
LANG=es_ES.UTF-8 PYTHONPATH=src python3 -m warpdesk
```

