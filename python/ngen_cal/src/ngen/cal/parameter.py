from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Sequence

class Parameter(BaseModel, allow_population_by_field_name = True):
    """
        The data class for a given parameter
    """
    name: str = Field(alias='param')
    min: float
    max: float
    init: float

Parameters = Sequence[Parameter]
