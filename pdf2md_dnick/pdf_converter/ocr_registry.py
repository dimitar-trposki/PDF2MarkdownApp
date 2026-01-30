"""
Model Registry for PDF-to-text models.

Usage:
    from .ocr_registry import register_model, create_model

    @register_model("my_model", "My Model Display Name")
    class MyModel(BasePDFModel):
        def predict()
            ...


    # Create and use:
    model = create_model("my_model")
    text = model.predict(pdf_bytes)
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Dict, List, Type, Any

if TYPE_CHECKING:
    from .ocr_models import BasePDFModel


class ModelInfo:
    """Metadata about a registered model."""
    key: str
    label: str

    def __init__(self, key: str, label: str):
        self.key = key
        self.label = label


_REGISTRY: Dict[str, Callable[[], "BasePDFModel"]] = {}


def register_model(key: str, label: str):
    """
    Decorator to register a model class.

    Args:
        key: Unique identifier for the model (e.g., "easyocr_en")
        label: Human-readable name (e.g., "EasyOCR")

    Returns:
        Decorator that registers the class and returns it unchanged.
    """
    def decorator(cls: Type["BasePDFModel"]) -> Type["BasePDFModel"]: # in cls there is the class model(EasyOCRModel,PyTesseractModel...)
        k = key.strip()
        if not k:
            raise ValueError("Model key cannot be empty")
        if k in _REGISTRY:
            raise ValueError(f"Model key already registered: {k}")

        def factory() -> "BasePDFModel":
            return cls()

        setattr(factory, "_label", label)
        _REGISTRY[k] = factory
        return cls

    return decorator





def list_models() -> List[ModelInfo]:
    """Return all registered models sorted by label."""
    items = [ModelInfo(key=k, label=getattr(f, "_label", k)) for k, f in _REGISTRY.items()]
    items.sort(key=lambda x: x.label.lower())
    return items


def create_model(key: str) -> "BasePDFModel":
    """
    Instantiate a model by its registry key.

    Args:
        key: The model's unique identifier

    Returns:
        An instance of the requested model

    Raises:
        KeyError: If the model key is not registered
    """
    if key not in _REGISTRY:
        raise KeyError(f"Unknown model: {key}")
    return _REGISTRY[key]()


def safe_list_models() -> List[ModelInfo]:
    """
    Return only models that can be successfully instantiated.

    Filters out models with missing dependencies.
    """
    ok = []
    for info in list_models():
        try:
            create_model(info.key)
            ok.append(info)
        except Exception:
            continue
    return ok
