import os


def get_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing environment variable: {name}")
    return value


def get_kma_auth_key() -> str:
    return get_env("KMA_AUTH_KEY")
