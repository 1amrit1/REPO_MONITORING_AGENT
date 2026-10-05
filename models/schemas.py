from typing import Literal

from pydantic import BaseModel


class IssueClassification(BaseModel):
    type: Literal["bug", "feature", "question"]
    priority: Literal["high", "med", "low"]
    summary: str
