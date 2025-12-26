"""
Поиск ОКВЭД по окончанию номера телефона.
"""

import json
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class MatchResult:
    """Результат поиска."""

    normalized_phone: str
    code: str
    name: str
    match_length: int

    def __str__(self):
        return (
            f"Номер: {self.normalized_phone}\n"
            f"Код ОКВЭД: {self.code}\n"
            f"Название: {self.name}\n"
            f"Длина совпадения: {self.match_length}"
        )


def load_json(filepath: str) -> dict:
    """Загрузить JSON-файл."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_codes(data, result=None) -> list[tuple[str, str]]:
    """Рекурсивно извлечь все коды из вложенной структуры."""
    if result is None:
        result = []

    items = data if isinstance(data, list) else [data]

    for item in items:
        result.append((item["code"], item["name"]))
        if "items" in item:
            extract_codes(item["items"], result)

    return result


def normalize_code(code: str) -> str:
    """Убрать точки из кода: '10.86.11' → '108611'."""
    return code.replace(".", "")


def build_index(codes: list[tuple[str, str]]) -> dict[int, dict]:
    """Построить индекс по длинам кодов."""
    index = defaultdict(dict)

    for code, name in codes:
        normalized = normalize_code(code)
        index[len(normalized)][normalized] = {"code": code, "name": name}

    return dict(index)


def normalize_phone(phone: str) -> str:
    """Оставить только цифры: '+7 (920) 047-27-21' → '79200472721'."""
    return "".join(c for c in phone if c.isdigit())


def find_by_suffix(phone: str, index: dict[int, dict]) -> MatchResult | None:
    """Найти ОКВЭД с максимальным совпадением по окончанию."""
    digits = normalize_phone(phone)
    lengths = sorted(index.keys(), reverse=True)

    for length in lengths:
        if length <= len(digits):
            suffix = digits[-length:]
            if suffix in index[length]:
                match = index[length][suffix]
                return MatchResult(
                    normalized_phone=digits,
                    code=match["code"],
                    name=match["name"],
                    match_length=length,
                )

    return None


def create_matcher(filepath: str):
    """Создать функцию поиска для файла ОКВЭД."""
    data = load_json(filepath)
    codes = extract_codes(data)
    index = build_index(codes)

    def find(phone: str) -> MatchResult | None:
        return find_by_suffix(phone, index)

    return find


if __name__ == "__main__":
    find_okved = create_matcher("okved.json")

    result = find_okved(input("Введите номер телефона: "))

    if result:
        print(result)
    else:
        print("Совпадений не найдено")
