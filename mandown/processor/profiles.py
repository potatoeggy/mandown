from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True, frozen=True)
class OutputProfile:
    id: str
    name: str
    size: tuple[int, int]


SupportedProfiles = Literal[
    "kindle",
    "kintouch",
    "paper",
    "voyage",
    "oasis2",
    "kobotouch",
    "glo",
    "glohd",
    "aura",
    "aurahd",
    "aurah2o",
    "aurah2o2",
    "auraone",
    "clarahd",
    "librah2o",
    "nia",
    "clara2e",
    "libra2",
    "sage",
]
_ProfileType = tuple[str, tuple[int, int]]

__all_profiles_data: dict[SupportedProfiles, _ProfileType] = {
    # Kindles
    "kindle": ("Kindle", (600, 800)),
    "kintouch": ("Kindle Touch", (600, 800)),
    "paper": ("Kindle Paperwhite 1/2", (758, 1024)),
    "voyage": ("Kindle Voyage, Oasis, Paperwhite 3/4", (1072, 1448)),
    "oasis2": ("Kindle Oasis 2/3", (1264, 1680)),
    # Kobos
    "kobotouch": ("Kobo Mini/Touch", (600, 800)),
    "glo": ("Kobo Glo", (768, 1024)),
    "glohd": ("Kobo Glo HD", (1072, 1448)),
    "aura": ("Kobo Aura", (758, 1024)),
    "aurahd": ("Kobo Aura HD", (1080, 1440)),
    "aurah2o": ("Kobo Aura H2O", (1080, 1430)),
    "aurah2o2": ("Kobo Aura H2O 2", (1080, 1430)),
    "auraone": ("Kobo Aura One", (1404, 1872)),
    "clarahd": ("Kobo Clara HD", (1072, 1448)),
    "librah2o": ("Kobo Libra H2O", (1264, 1680)),
    "nia": ("Kobo Nia", (758, 1024)),
    "clara2e": ("Kobo Clara 2E", (1072, 1448)),
    "libra2": ("Kobo Libra 2", (1264, 1680)),
    "sage": ("Kobo Sage", (1440, 1920)),
}

all_profiles = {id: OutputProfile(id, *profile) for id, profile in __all_profiles_data.items()}
