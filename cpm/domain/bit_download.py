from dataclasses import dataclass


@dataclass
class BitDownload:
    bit_name: str
    version: str
    payload: str
