from typing import Optional


def clean_proc_number(number: str) -> str:
    return number.replace(".", "").replace("-", "")


def clean_proc_value(value: str) -> float:
    return float(value[2:].replace(".", "").replace(",", ".").strip())


def clean(value: str, dropset: str = "\n\t\r:-.") -> str:
    dropmap = dict.fromkeys(map(ord, dropset))
    return value.translate(dropmap).strip()
