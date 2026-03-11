# pureenv

Typed environment variable parsing for Python. Zero dependencies. Pure stdlib.

---

## The Problem

Every Python project ends up writing this:
```python
PORT   = int(os.environ.get("PORT", 8080))
DEBUG  = os.environ.get("DEBUG", "false").lower() == "true"
DB_URL = os.environ["DATABASE_URL"] # KeyError with no helpful message
```

Manual casting. No validation. Cryptic error. Every. Single. Project.

## The solution
```python
from pureenv import env
PORT   = env.int("PORT",            default=8080)
DEBUG  = env.bool("DEBUG",          default=False)
DB_URL = env.str("DATABASE_URL",    required=True)
```

Typed. Validated. Clear errors when something is wrong.


## Install
```bash
pip install pureenv
```

## Usage
```python
from pureenv import env

# strings
NAME = env.str("APP_NAME", default="myapp")

# numbers
PORT  = env.int("PORT",    default=8080)
RATIO = env.float("RATIO", default=0.5)

# booleans - accepts "true/false", "1/0", "yes/no", "y/n", "on/off"
DEBUG = env.bool("DEBUG", default=False)

# required - raises a clear error if missing
DB_URL = env.str("DATABASE_URL", required=True)
```

## Why not `environs` or `python-dotenv`?

| | pureenv | python-dotenv | environs |
|---|---|---|---|
| Typed casting       | ✅ | ❌ | ✅ |
| Zero dependencies   | ✅ | ✅ | ❌ |
| Required validation | ✅ | ❌ | ✅ |
| Loads .env file     | ❌ | ✅ | ✅ |
