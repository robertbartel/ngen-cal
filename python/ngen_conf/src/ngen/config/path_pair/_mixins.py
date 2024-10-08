from __future__ import annotations

from itertools import zip_longest
from pathlib import Path

from ._abc_mixins import AbstractPathPairMixin, AbstractPathPairCollectionMixin
from ._utils import path_unlink_37

from typing import Iterable
from typing_extensions import Self
from .typing import StrPath, T


class PathPairMixin(AbstractPathPairMixin[T]):
    def __truediv__(self, key: StrPath) -> Self:
        return self.with_path(Path(self).joinpath(Path(key)))

    def __rtruediv__(self, key: StrPath) -> Self:
        return self.with_path(Path(key).joinpath(self))

    @property
    def parent(self) -> Path:
        return Path(self).parent

    @property
    def inner(self) -> T | None:
        return self._inner

    def with_path(self, *args: StrPath) -> Self:
        return self.with_object(
            self.inner,
            path=Path(*args),
            reader=self._reader,
            writer=self._writer,
            serializer=self._serializer,
            deserializer=self._deserializer,
        )

    def serialize(self) -> bytes | None:
        if self._serializer is None or self._inner is None:
            return None

        return self._serializer(self.inner)

    def deserialize(self, data: bytes) -> bool:
        if self._deserializer is None or self._reader is None:
            return False

        self._inner = self._deserializer(data)
        return True

    def read(self) -> bool:
        return self.deserialize(self._reader(self))

    def write(self) -> bool:
        if self._serializer is None or self._inner is None:
            return False

        self._writer(self, self.serialize())
        return True

    def unlink(self, missing_ok: bool = False):
        path_unlink_37(Path(self), missing_ok=missing_ok)


class PathPairCollectionMixin(AbstractPathPairCollectionMixin[T]):
    def __truediv__(self, key: StrPath) -> Self:
        # noop
        return self

    def __rtruediv__(self, key: StrPath) -> Self:
        # avoid circular import
        from .path_pair import PathPairCollection

        inner = [key / item for item in self._inner]
        new_path = Path(key).joinpath(self)
        return PathPairCollection(
            new_path,
            pattern=self._pattern,
            inner=inner,
            reader=self._reader,
            writer=self._writer,
            serializer=self._serializer,
            deserializer=self._deserializer,
        )

    def _get_filenames(self) -> Iterable[Path]:
        prefix, _, suffix = self.name.partition(self.pattern)
        glob_term = f"{prefix}*{suffix}"
        yield from self.parent.glob(glob_term)

    @property
    def parent(self) -> Path:
        return Path(self).parent

    @property
    def pattern(self) -> str:
        return self._pattern

    @property
    def inner(self) -> Iterable[T]:
        for item in self._inner:
            yield item.inner

    @property
    def inner_pair(
        self,
    ) -> Iterable[AbstractPathPairMixin[T]]:
        for item in self._inner:
            yield item

    def with_pattern(self, pattern: str) -> Self:
        # avoid circular import
        from .path_pair import PathPairCollection

        return PathPairCollection[T](
            self,
            pattern=pattern,
            inner=self._inner,
            reader=self._reader,
            writer=self._writer,
            serializer=self._serializer,
            deserializer=self._deserializer,
        )

    def serialize(self) -> Iterable[bytes]:
        if self._serializer is None or self._inner is None:
            return None

        for item in self.inner:
            yield self._serializer(item)

    def deserialize(
        self, data: Iterable[bytes], *, paths: Iterable[StrPath] | None = None
    ) -> bool:
        """
        Deserialize collection of bytes into T's and wrap each T as a `PathPair[T]`. Replace
        `self`'s inner collection with the deserialized collection. Returns `False` if there is no
        deserializer on `self`.

        If `paths` is None, the inner `PathPair[T]`'s have `self`'s path.
        """
        # avoid circular import
        from .path_pair import PathPair

        if self._deserializer is None:
            return False

        if paths is None:
            deserialized_path = Path(self)
            deserialized = [
                PathPair.with_object(
                    self._deserializer(item),
                    path=deserialized_path,
                    reader=self._reader,
                    writer=self._writer,
                    serializer=self._serializer,
                    deserializer=self._deserializer,
                )
                for item in data
            ]
        else:
            error_message = (
                "Iterators `data` and `paths` have different stopping points."
            )
            deserialized = []
            for item, path in zip_longest(data, paths, fillvalue=ValueError):
                if item == ValueError or path == ValueError:
                    raise ValueError(error_message)

                path_pair = PathPair.with_object(
                    self._deserializer(item),
                    path=path,
                    reader=self._reader,
                    writer=self._writer,
                    serializer=self._serializer,
                    deserializer=self._deserializer,
                )
                deserialized.append(path_pair)

        self._inner = deserialized
        return True

    def read(self) -> bool:
        data = (self._reader(path) for path in self._get_filenames())
        return self.deserialize(data, paths=self._get_filenames())

    def write(self) -> bool:
        if self._serializer is None or self._inner is None or self._writer is None:
            return False

        for item in self._inner:
            self._writer(item, item.serialize())

        return True

    def unlink(self, missing_ok: bool = False):
        for item in self._inner:
            item.unlink(missing_ok=missing_ok)
