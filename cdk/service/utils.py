import os
from pathlib import Path

from git import Repo

import cdk.service.constants as constants


def get_username() -> str:
    try:
        return os.getlogin().replace('.', '-')
    except Exception:
        return 'github'


def get_stack_name() -> str:
    repo = Repo(Path.cwd())
    username = get_username()
    try:
        return f'{username}-{repo.active_branch}-{constants.SERVICE_NAME}'
    except TypeError:
        return f'{username}-{constants.SERVICE_NAME}'


def get_construct_name(stack_prefix: str, construct_name: str) -> str:
    return f'{stack_prefix}{construct_name}'[0:64]
