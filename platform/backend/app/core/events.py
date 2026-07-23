"""Внутриплатформенная шина событий.

Модули общаются между собой только через события — это сохраняет их
изоляцию и позволяет позже вынести модуль в отдельный сервис, заменив
шину на брокер сообщений.
"""
from collections import defaultdict
from typing import Any, Callable

_subscribers: dict[str, list[Callable[..., Any]]] = defaultdict(list)


def subscribe(event: str, handler: Callable[..., Any]) -> None:
    _subscribers[event].append(handler)


def publish(event: str, **payload: Any) -> None:
    for handler in _subscribers[event]:
        handler(**payload)
