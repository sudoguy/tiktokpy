from pathlib import Path
from typing import Optional

from dynaconf import loaders, settings

from tiktokpy.utils.logger import logger

DEFAULT_PATH = "settings.toml"
BASE_SETTINGS = {
    "BASE_URL": "https://www.tiktok.com/",
    "HEADLESS": True,
    "LANG": "en",
    "HOME_DIR": str(Path().absolute()),
}


def load_or_create_settings(path: Optional[str]):
    path = path or DEFAULT_PATH

    if not Path(path).exists():
        default_settings_path = str(Path.cwd() / Path(DEFAULT_PATH))
        logger.info(
            f'🔧 Settings in path directory not found "{Path(path).absolute()}". '
            f"I'll create default settings here: {default_settings_path}",
        )
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        loaders.write(default_settings_path, BASE_SETTINGS, env="default")

    settings.load_file(path=path)

    logger.info("🔧 Settings successfully loaded")
