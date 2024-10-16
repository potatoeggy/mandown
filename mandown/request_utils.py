import requests as RealRequests

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"  # noqa: E501


class requests:
    @staticmethod
    def get(url: str) -> RealRequests.Response:
        return RealRequests.get(url, headers={"User-Agent": USER_AGENT}, timeout=5)
