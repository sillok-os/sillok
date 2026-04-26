"""Pydantic-first with stdlib dataclass fallback.

This module provides a unified ``BaseModel`` that uses Pydantic 2.x when
available, and falls back to a minimal dataclass-based shim when Pydantic
is not installed. This keeps Sillok's stdlib-friendly core principle while
still allowing Pydantic's validation when the library happens to be present.

Usage::

    from sillok.schemas._base import BaseModel, Field, HAS_PYDANTIC

    class MyProposal(BaseModel):
        id: str
        title: str
        confidence: str

When Pydantic is installed::

    MyProposal(id="x", title="t", confidence="high")  # validated

When Pydantic is NOT installed::

    MyProposal(id="x", title="t", confidence="high")  # dataclass init only
"""
from __future__ import annotations

import sys
from typing import Any, get_args, get_origin, get_type_hints

try:
    from pydantic import BaseModel as _PydanticBaseModel  # type: ignore
    from pydantic import ConfigDict, Field  # type: ignore

    HAS_PYDANTIC = True

    class BaseModel(_PydanticBaseModel):  # type: ignore[misc]
        """Sillok wrapper — shared Pydantic config for all schemas."""

        model_config = ConfigDict(
            extra="forbid",
            str_strip_whitespace=True,
            validate_assignment=True,
            frozen=False,
        )

except ImportError:  # pragma: no cover - exercised via monkey-patching in tests
    from copy import deepcopy

    HAS_PYDANTIC = False

    class _FieldSpec:
        """Fallback field metadata for stdlib-only model initialization."""

        def __init__(self, default: Any = ..., *, default_factory=None) -> None:
            self.default = default
            self.default_factory = default_factory

    def Field(default: Any = ..., *, default_factory=None, **kwargs):  # type: ignore[no-redef]
        """Minimal Field shim for stdlib-only fallback."""
        return _FieldSpec(default=default, default_factory=default_factory)

    class ConfigDict(dict):  # type: ignore[no-redef]
        pass

    class BaseModel:  # type: ignore[no-redef]
        """stdlib-only fallback. No validation, init-only contract."""

        __fields__: dict[str, tuple[bool, Any, Any]] = {}
        __field_types__: dict[str, Any] = {}

        def __init_subclass__(cls, **kwargs: Any) -> None:
            super().__init_subclass__(**kwargs)
            fields: dict[str, tuple[bool, Any, Any]] = {}
            for base in reversed(cls.__mro__[1:]):
                fields.update(getattr(base, "__fields__", {}))

            try:
                annotations = get_type_hints(cls)
            except Exception:
                annotations = dict(getattr(cls, "__annotations__", {}))
            annotations = {
                name: annotation
                for name, annotation in annotations.items()
                if not name.startswith("__")
            }
            cls.__field_types__ = dict(annotations)
            for name in annotations:
                raw_default = cls.__dict__.get(name, ...)
                required = raw_default is ...
                default = ...
                default_factory = None
                if isinstance(raw_default, _FieldSpec):
                    required = raw_default.default is ... and raw_default.default_factory is None
                    default = raw_default.default
                    default_factory = raw_default.default_factory
                elif raw_default is not ...:
                    required = False
                    default = raw_default
                fields[name] = (required, default, default_factory)

            cls.__fields__ = fields

        def __init__(self, **kwargs: Any) -> None:
            unknown = set(kwargs) - set(self.__fields__)
            if unknown:
                unknown_csv = ", ".join(sorted(unknown))
                raise TypeError(f"unexpected field(s): {unknown_csv}")

            missing: list[str] = []
            for name, (required, default, default_factory) in self.__fields__.items():
                if name in kwargs:
                    value = self._coerce_value(
                        self.__field_types__.get(name, Any),
                        kwargs[name],
                    )
                elif default_factory is not None:
                    value = self._coerce_value(
                        self.__field_types__.get(name, Any),
                        default_factory(),
                    )
                elif default is not ...:
                    value = self._coerce_value(
                        self.__field_types__.get(name, Any),
                        deepcopy(default),
                    )
                elif required:
                    missing.append(name)
                    continue
                else:
                    value = None
                setattr(self, name, value)

            if missing:
                missing_csv = ", ".join(missing)
                raise TypeError(f"missing required field(s): {missing_csv}")

        def model_dump(self) -> dict[str, Any]:
            return {
                name: self._dump_value(getattr(self, name))
                for name in self.__fields__
            }

        @classmethod
        def _coerce_value(cls, annotation: Any, value: Any) -> Any:
            if value is None:
                return None

            if isinstance(annotation, str):
                module = sys.modules.get(cls.__module__)
                compact = annotation.replace(" ", "")

                if "|" in compact:
                    non_none_parts = [
                        part for part in compact.split("|") if part != "None"
                    ]
                    if len(non_none_parts) == 1:
                        return cls._coerce_value(non_none_parts[0], value)

                if compact.startswith("list[") and compact.endswith("]"):
                    inner = compact[5:-1]
                    if isinstance(value, list):
                        return [cls._coerce_value(inner, item) for item in value]
                    return value

                if compact.startswith("dict[") and compact.endswith("]"):
                    return value

                resolved = getattr(module, compact, None) if module else None
                if isinstance(resolved, type) and issubclass(resolved, BaseModel):
                    return cls._coerce_value(resolved, value)
                return value

            origin = get_origin(annotation)
            args = get_args(annotation)

            if origin is list and args:
                inner = args[0]
                if isinstance(value, list):
                    return [cls._coerce_value(inner, item) for item in value]
                return value

            if origin is dict and args:
                key_t, val_t = args
                if isinstance(value, dict):
                    return {
                        cls._coerce_value(key_t, k): cls._coerce_value(val_t, v)
                        for k, v in value.items()
                    }
                return value

            if origin is not None and args:
                non_none = [arg for arg in args if arg is not type(None)]
                if len(non_none) == 1 and len(non_none) != len(args):
                    return cls._coerce_value(non_none[0], value)

            if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                if isinstance(value, annotation):
                    return value
                if isinstance(value, dict):
                    return annotation.model_validate(value)

            return value

        @classmethod
        def _dump_value(cls, value: Any) -> Any:
            if isinstance(value, BaseModel):
                return value.model_dump()
            if isinstance(value, list):
                return [cls._dump_value(item) for item in value]
            if isinstance(value, dict):
                return {key: cls._dump_value(item) for key, item in value.items()}
            return value

        def model_dump_json(self, *, indent: int | None = None) -> str:
            import json

            return json.dumps(
                self.model_dump(),
                default=str,
                ensure_ascii=False,
                indent=indent,
            )

        @classmethod
        def model_validate(cls, data: dict[str, Any]) -> "BaseModel":
            return cls(**data)


__all__ = ["BaseModel", "Field", "ConfigDict", "HAS_PYDANTIC"]
