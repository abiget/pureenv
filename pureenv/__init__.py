import os
import sys

# Store references to the original int and float functions to avoid issues
#  if they are overridden in the environment
_int = int
_float = float
_bool = bool
_str = str

class Env:
    def __init__(self, environ: dict = None):
        self._environ = environ if environ is not None else os.environ
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
        value = self._environ.get(key, None)

        if value is None:
            if required:
                if sys.platform.startswith("win"):
                    hint = f"set {key}=your_value"
                else:
                    hint = f"export {key}=your_value"

                raise ValueError(
                    f"Required env var '{key}' is not set.\n"
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
            if os.environ.get(key):
                raise ValueError(
                    f"Env var '{key}' has value {value!r} which is not a valid integer."
                )
            else:
                raise ValueError(
                    f"Default value for '{key}' is {value!r} which is not a valid integer."
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
            if os.environ.get(key):
                raise ValueError(
                    f"Env var '{key}' has value {value!r} which is not a valid float."
                )
            else:
                raise ValueError(
                    f"Default value for '{key}' is {value!r} which is not a valid float."
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
            if os.environ.get(key):
                raise ValueError(
                    f"Env var '{key}' has value {value!r} which is not a valid boolean.\n"
                    f"→ Use: true/false, 1/0, yes/no, y/n, on/off (case-insensitive)"
                )
            else:
                raise ValueError(
                    f"The default value for '{key}' is {value!r} which is not a valid boolean.\n"
                    f"→ Use: true/false, 1/0, yes/no, y/n, on/off (case-insensitive)"
                )

# module-level singleton instance of Env for convenience
env = Env()