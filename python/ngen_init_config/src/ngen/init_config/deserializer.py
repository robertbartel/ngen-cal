from __future__ import annotations

from abc import ABC, abstractmethod

from .core import Base
from .utils import merge_class_attr
from ._deserializers import (
    from_ini_str,
    from_ini_no_section_header_str,
    from_namelist_str,
    from_yaml_str,
    from_toml_str,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import Self
    from pathlib import Path


class IniDeserializer(Base):
    """Blanket implementation for deserializing from ini format. Python's standard library
    `configparser` package is used to handle deserialization.

    Subtype specific configuration options:
        Optionally provide configuration options in `Config` class of types that inherits from
        `IniDeserializer`.

        - `no_section_headers`: bool
            Denotes that ini file does not have section headers (default: `False`)
    """

    class Config(Base.Config):
        no_section_headers: bool = False

    @classmethod
    def from_ini(cls, p: Path) -> Self:
        no_section_headers = merge_class_attr(cls, "Config.no_section_headers", False)
        if no_section_headers:
            return from_ini_no_section_header_str(p.read_text(), cls)
        return from_ini_str(p.read_text(), cls)

    @classmethod
    def from_ini_str(cls, s: str) -> Self:
        no_section_headers = merge_class_attr(cls, "Config.no_section_headers", False)
        if no_section_headers:
            return from_ini_no_section_header_str(s, cls)
        return from_ini_str(s, cls)


class NamelistDeserializer(Base):
    """Blanket implementation for deserializing from FORTRAN namelist format. The `f90nml` package
    is used to handle deserialization. `f90nml` is not included in default installations of
    `ngen.init_config`. Install `ngen.init_config` with `f90nml` using the extra install option,
    `namelist`.
    """

    @classmethod
    def from_namelist(cls, p: Path) -> Self:
        return from_namelist_str(p.read_text(), cls)

    @classmethod
    def from_namelist_str(cls, s: str) -> Self:
        return from_namelist_str(s, cls)


class YamlDeserializer(Base):
    """Blanket implementation for deserializing from yaml format. The `PyYAML` package is used to
    handle deserialization. `PyYAML` is not included in default installations of `ngen.init_config`.
    Install `ngen.init_config` with `PyYAML` using the extra install option, `yaml`.
    """

    @classmethod
    def from_yaml(cls, p: Path) -> Self:
        return from_yaml_str(p.read_text(), cls)

    @classmethod
    def from_yaml_str(cls, s: str) -> Self:
        return from_yaml_str(s, cls)


class TomlDeserializer(Base):
    """Blanket implementation for deserializing from `toml` format. The `tomli` package is used to
    handle deserialization. `tomli` is not included in default installations of `ngen.init_config`.
    Install `ngen.init_config` with `tomli` using the extra install option, `toml`.
    """

    @classmethod
    def from_toml(cls, p: Path) -> Self:
        return from_toml_str(p.read_text(), cls)

    @classmethod
    def from_toml_str(cls, s: str) -> Self:
        return from_toml_str(s, cls)


class JsonDeserializer(Base):
    """Blanket implementation for deserializing from `json` format. This functionality is provided
    by `pydantic`. See `pydantic`'s documentation for other configuration options.
    """

    @classmethod
    def from_json(cls, p: Path) -> Self:
        return cls.parse_file(p)

    @classmethod
    def from_json_str(cls, s: str) -> Self:
        return cls.parse_raw(s)


class GenericDeserializer(Base, ABC):
    """
    Stub for deserializing from a generic format.
    Subclasses must implement the `from_file` and `from_str` abstract class methods.
    See `ngen.init_config.core.Base` and `pydantic`'s documentation for configuration options.
    """

    @classmethod
    @abstractmethod
    def from_file(cls, p: Path, *_) -> Self:
        ...

    @classmethod
    @abstractmethod
    def from_str(cls, s: str, *_) -> Self:
        ...
