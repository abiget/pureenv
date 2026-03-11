import os
import sys
from contextlib import contextmanager
from typing import Generator

# Store references to the original int and float functions to avoid issues
#  if they are overridden in the environment
_int = int
_float = float
_bool = bool
_str = str

class Env:
    """
    Typed environment variable reader with auto .env file loading.

    Automatically loads environment variables from a .env file on initialization.
    Shell environment variables take priority and are never overwritten by .env values.

    Example:
        from pureenv import env

        PORT   = env.int("PORT",      default=8080)
        DEBUG  = env.bool("DEBUG",    default=False)
        DB_URL = env.str("DB_URL",    required=True)

        # or without casting:
        PORT   = env("PORT", default="8080")
        DEBUG  = env("DEBUG", default="false")
        DB_URL = env("DB_URL", required=True) 
    """

    def __init__(self, environ: dict = None) -> None:
        """
        Initialize the Env instance.

        Args:
            environ: Optional Custom environment dict for testing.
            Defaults to os.environ if not provided.
            When provided, .env file is not auto-loaded.

        Example:
            # production - uses os.environ + auto-loads .env
            env = Env()

            # testing - isolated, no .env loading
            env = Env(environ={"PORT": "8080"})
        """

        self._environ = environ if environ is not None else os.environ
        self._prefix = ""
        if environ is None: # only auto-load when using real os.environ
            self._load_env_file()

    @contextmanager
    def prefix(self, prefix: str) -> Generator["Env", None, None]:
        """
        Context manager to temporarily set a prefix for all env var lookups.

        Args:
            prefix: The prefix to prepend to all keys within the block.

        Example:
            with env.prefix("DB_"):
                DB_HOST = env("HOST", default="localhost")  # reads DB_HOST
                DB_PORT = env("PORT", default="5432")       # reads DB_PORT
                DB_NAME = env("NAME", default="mydb")       # reads DB_NAME

            with env.prefix("REDIS_"):
                REDIS_HOST = env("HOST", default="localhost")   # reads REDIS_HOST
                REDIS_PORT = env("PORT", default="6379")        # reads REDIS_PORT

        Note:
            Use distinct variable names across prefix blocks to avoid
            overwriting values from previous blocks.
        """

        self._prefix = prefix
        yield self
        self._prefix = ""

    
    def _load_env_file(self, filepath: str = ".env") -> None:
        """
        Auto-load environment variables from a .env file into os.environ.

        Called automatically on initialization. Only loads if the file exists,
        silent if missing. Shell environment variables always take priority  -

        existing variables are never overwritten.

        Supported syntax:
           KEY=VALUE
           KEY="VALUE" # quoted values
           KEY='VALUE' # single-quoted values
           KEY=VALUE  # with inline comment (space before #)
           # full line comments start with # and are ignored
           (empty lines are ignored)

        Args:
            filepath: Path to the .env file (default: ".env")
        
        Example .env file:
            DATABASE_URL=postgres://localhost/mydb
            PORT=8080 # the app port
            DEBUG=true # enable debug mode
        """

        if not os.path.exists(filepath):
            return
        
        with open(filepath, "r") as file:
            for line in file:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()

                # remove inline comments
                value = value.split(" #")[0]
                
                # strip whitespace and optional quotes
                value = value.strip().strip('"').strip("'")

                if key not in self._environ:
                    self._environ[key] = value

    def __call__(self, key: str, default: str = None, required: bool = False) -> str:
        """
        Get an environment variable as a string without explicit casting.
        Shorthand for env.str() - allows calling env() directly for convenience.

        Args:
            key: The name of the environment variable.
            default: The default value to return if the variable is not set (default: None).
            required: If True, raises an error if the variable is not set (default: False).
        
        Returns:
            The value as a string, or the default value if not set.


        Example:
            env("PORT", default="8080")  # equivalent to env.str("PORT", default="8080")
        """
        return self.str(key, default=default, required=required)
    
    def str(self, key: str, default: str = None,
            required: bool = False) -> str:
        """
        Get an environment variable as a string.

        Args:
            key: The name of the environment variable.
            default: The default value to return if the variable is not set (default: None).
            required: If True, raises an error if the variable is not set (default: False).

        Returns:
            The value of the environment variable as a string, or the default value if not set.
        """
        value = self._environ.get(self._prefix + key, None)

        if value is None:
            if required:
                if sys.platform.startswith("win"):
                    hint = f"set {self._prefix + key}=your_value"
                else:
                    hint = f"export {self._prefix + key}=your_value"

                raise ValueError(
                    f"Required env var '{self._prefix + key}' is not set.\n"
                    f"→ To fix: {hint}"
                )
            return _str(default) if default is not None else None
        return value
    
    def int(self, key: str, default: int = None, 
            required: bool = False) -> int:
        """
        Get an environment variable as an integer.
        Args:
            key: The name of the environment variable.
            default: The default value to return if the variable is not set (default: None).
            required: If True, raises an error if the variable is not set (default: False).

        Returns:
            The value of the environment variable as an integer, or the default value if not set.
        """
        value = self.str(key, default=default, required=required)

        if value is None:
            return None
        
        try:
            return _int(value)
        except (ValueError, TypeError):
            # did it come from an env var or the default value?
            if os.environ.get(self._prefix + key):
                raise ValueError(
                    f"Env var '{self._prefix + key}' has value {value!r} which is not a valid integer."
                )
            else:
                raise ValueError(
                    f"Default value for '{self._prefix + key}' is {value!r} which is not a valid integer."
                )
        
    def float(self, key: str, default: float = None,
                required: bool = False) -> float:
        """
        Get an environment variable as a float.

        Args:
            key: The name of the environment variable.
            default: The default value to return if the variable is not set (default: None).
            required: If True, raises an error if the variable is not set (default: False).

        Returns:
            The value of the environment variable as a float, or the default value if not set.
        """
        value = self.str(key, default=default, required=required)

        if value is None:
            return None
        try:
            return _float(value)
        except (ValueError, TypeError):
            if os.environ.get(self._prefix + key):
                raise ValueError(
                    f"Env var '{self._prefix + key}' has value {value!r} which is not a valid float."
                )
            else:
                raise ValueError(
                    f"Default value for '{self._prefix + key}' is {value!r} which is not a valid float."
                )
        
    def bool(self, key: str, default: bool = None,
                required: bool = False) -> bool:
        """
        Get an environment variable as a boolean.

        Accepted values (case-insensitive):
        - Truthy: "true", "1", "yes", "y", "on"
        - Falsy: "false", "0", "no", "n", "off"

        Args:
            key: The name of the environment variable.
            default: The default value to return if the variable is not set (default: None).
            required: If True, raises an error if the variable is not set (default: False).

        Returns:
            The value of the environment variable as a boolean, or the default value if not set.
        """
        value = self.str(key, default=default, required=required)

        if value is None:
            return None
        
        if isinstance(value, _bool):
            return value
        
        if isinstance(value, (_int, _float)):
            return _bool(value)
        
        value_lower = value.lower()
        if value_lower in ("true", "1", "yes", "y", "on"):
            return True
        elif value_lower in ("false", "0", "no", "n", "off"):
            return False
        else:
            if os.environ.get(self._prefix + key):
                raise ValueError(
                    f"Env var '{self._prefix + key}' has value {value!r} which is not a valid boolean.\n"
                    f"→ Use: true/false, 1/0, yes/no, y/n, on/off (case-insensitive)"
                )
            else:
                raise ValueError(
                    f"The default value for '{self._prefix + key}' is {value!r} which is not a valid boolean.\n"
                    f"→ Use: true/false, 1/0, yes/no, y/n, on/off (case-insensitive)"
                )

# module-level singleton instance of Env for convenience
env = Env()