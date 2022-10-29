#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations;

from src.thirdparty.code import *;
from src.thirdparty.misc import *;
from src.thirdparty.quantum import *;
from src.thirdparty.types import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'Latest',
    'latest_info',
    'latest_state',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS / LOCAL VARIABLES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# local usage only
T = TypeVar('T');

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CLASSES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@dataclass
class LatestBasic(Generic[T]):
    backend: Optional[T] = field(default=None);
    job: Optional[IBMQJob] = field(default=None);

    def set_backend(self, option: Optional[T]):
        self.backend = option;

    def set_job(self, job: Optional[IBMQJob]):
        self.job = job;

@dataclass
class Latest():
    simulator: LatestBasic[BACKEND_SIMULATOR] = field(default_factory=lambda: LatestBasic[BACKEND_SIMULATOR]());
    queue: LatestBasic[BACKEND] = field(default_factory=lambda: LatestBasic[BACKEND]());

    def get_backend(self, queue: bool) -> Optional[BACKEND | BACKEND_SIMULATOR]:
        if queue:
            return self.queue.backend;
        return self.simulator.backend;

    def get_job(self, queue: bool) -> Optional[IBMQJob]:
        if queue:
            return self.queue.job;
        return self.simulator.job;

    def set_backend(self, option: Optional[BACKEND | BACKEND_SIMULATOR], queue: bool):
        if queue:
            self.queue.set_backend(option if isinstance(option, BACKEND) else None);
        else:
            self.simulator.set_backend(option if isinstance(option, BACKEND_SIMULATOR) else None);

    def set_job(self, job: Optional[IBMQJob], queue: bool):
        if queue:
            self.queue.set_job(job);
        else:
            self.simulator.set_job(job);

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def latest_info(backend: QkBackend, job: IBMQJob) -> str:
    return dedent(
        f'''
        \x1b[1mNOTE:\x1b[0m
        - backend used: \x1b[1m{backend}\x1b[0m
        - job index: \x1b[1m{job.job_id()}\x1b[0m
        '''
    );

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GLOBAL VARIABLE
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

latest_state = Latest();
