#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations;

from src.thirdparty.code import *;
from src.thirdparty.quantum import *;
from src.thirdparty.types import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'Latest',
    'LatestQueue',
    'LatestSimulator',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dataclass
class LatestSimulator():
    backend: Optional[BACKEND_SIMULATOR] = field(init=None);
    job: Optional[IBMQJob] = field(init=None);

@dataclass
class LatestQueue():
    backend: Optional[BACKEND] = field(init=None);
    job: Optional[IBMQJob] = field(init=None);

@dataclass
class Latest():
    simulator: LatestSimulator = field(default_factory=LatestSimulator);
    queue: LatestQueue = field(default_factory=LatestQueue);

    def get_backend(self, simulated: bool = True) -> Optional[BACKEND | BACKEND_SIMULATOR]:
        if simulated:
            return self.simulator.backend;
        return self.queue.backend;

    def get_job(self, simulated: bool = True) -> Optional[IBMQJob]:
        if simulated:
            return self.simulator.job;
        return self.queue.job;

    def set_backend(self, option: Optional[BACKEND | BACKEND_SIMULATOR], simulated: bool = True):
        if simulated:
            self.simulator.backend = option if isinstance(option, BACKEND_SIMULATOR) else None;
        else:
            self.queue.backend = option if isinstance(option, BACKEND) else None;
        return;

    def set_job(self, job: Optional[IBMQJob], simulated: bool = True):
        if simulated:
            self.simulator.job = job;
        else:
            self.queue.job = job;
        return;
