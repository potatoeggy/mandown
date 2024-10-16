from ..request_utils import requests
from .base_source import BaseSource


class CommonSource(BaseSource):
    _scripts: str | None = None

    def _get_scripts(self) -> str:
        """
        Legacy method for fetching the HTML of `self.url`.
        """
        if self._scripts:
            return self._scripts

        self._scripts = requests.get(self.url).text or ""
        return self._scripts
