from typing import Tuple


def clean_proc_value(value: str) -> float:
    return float(value[2:].replace(".", "").replace(",", ".").strip())


def clean(value: str, dropset: str = "\n\t\r") -> str:
    dropmap = dict.fromkeys(map(ord, dropset))
    return value.translate(dropmap).strip()


def clean_general_data(value: str) -> Tuple:
    new_str = clean(value)
    label, value = new_str.split(":", maxsplit=1)
    return label.strip(), value.strip()


def format_proc_number(number):
    return clean(number, dropset=".-")
