from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Type, Any


@dataclass(frozen=True)
class ModelInfo:
    key: str
    label: str


_REGISTRY: Dict[str, Callable[[], Any]] = {}


def register_model(key: str, label: str):
    def decorator(cls: Type[Any]):
        k = key.strip()
        if not k:
            raise ValueError("Model key cannot be empty")
        if k in _REGISTRY:
            raise ValueError(f"Model key already registered: {k}")

        def factory():
            return cls()

        setattr(factory, "_label", label)
        _REGISTRY[k] = factory
        return cls

    return decorator


def register_factory(key: str, label: str, factory: Callable[[], Any]):
    k = key.strip()
    if not k:
        raise ValueError("Model key cannot be empty")
    if k in _REGISTRY:
        raise ValueError(f"Model key already registered: {k}")
    setattr(factory, "_label", label)
    _REGISTRY[k] = factory


def list_models() -> List[ModelInfo]:
    items = [ModelInfo(key=k, label=getattr(f, "_label", k)) for k, f in _REGISTRY.items()]
    items.sort(key=lambda x: x.label.lower())
    return items


def create_model(key: str):
    if key not in _REGISTRY:
        raise KeyError(f"Unknown model: {key}")
    return _REGISTRY[key]()


def safe_list_models():
    ok = []
    for info in list_models():
        try:
            m = create_model(info.key)
            ok.append(info)
        except Exception:
            continue
    return ok
