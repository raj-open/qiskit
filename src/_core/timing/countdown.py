#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ----------------------------------------------------------------
# IMPORTS
# ----------------------------------------------------------------

from __future__ import annotations

from datetime import datetime
from datetime import timedelta
from datetime import timezone

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

# ----------------------------------------------------------------
# EXPORTS
# ----------------------------------------------------------------

__all__ = [
    "Countdown",
]

# ----------------------------------------------------------------
# CLASSES
# ----------------------------------------------------------------


class Countdown(BaseModel):
    """
    Allows one to set events based on a timer.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
        arbitrary_types_allowed=True,
    )

    label: str
    duration: float = Field(gt=0.0)
    time_finished: datetime = Field(default=datetime.now, init=False)

    def model_post_init(self, __context):
        self.restart()

    @property
    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    @property
    def remaining(self) -> timedelta:
        """
        Returns time remaining
        """
        return self.time_finished - self.now

    @property
    def overdue(self) -> timedelta:
        """
        Returns time overdue
        """
        return self.now - self.time_finished

    @property
    def done(self) -> bool:
        """
        Checks if countdown timer is finished.

        - if done, returns `true`.
        - otherwise returns `false`.
        """
        return self.now >= self.time_finished

    def restart(self):
        """
        Restarts the timer.
        """
        self.time_finished = self.now + timedelta(seconds=self.duration)
        return
