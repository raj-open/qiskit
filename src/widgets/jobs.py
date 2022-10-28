#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations;

from src.thirdparty.code import *;
from src.thirdparty.quantum import *;
from src.thirdparty.render import *;
from src.thirdparty.types import *;

from src.api import *;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    'RecoverJobWidget',
    'recover_job',
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS / LOCAL VARIABLES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# local usage only
T = TypeVar('T');
ARGS = ParamSpec('ARGS');

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# WIDGET Recover Job
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RecoverJobWidget():
    option: Optional[BACKEND];
    queue: bool;
    job: Optional[IBMQJob];

    # widget components
    dropdown_backends: widgets.Dropdown;
    dropdown_jobs: widgets.Dropdown;
    text_status: widgets.HTML;
    text_pending: widgets.HTML;
    output: widgets.Output;

    def __init__(
        self,
        option: Optional[BACKEND | BACKEND_SIMULATOR] = None,
        queue: bool = False,
        job: Optional[IBMQJob] = None,
    ):
        assert queue or (job is not None), 'If no queue use, then need to provide the job.';
        self.option = option;
        self.queue = queue;
        self.job = job;
        return;

    def show_loading(self):
        self.text_pending.layout.visibility = 'visible';

    def hide_loading(self):
        self.text_pending.layout.visibility = 'hidden';

    def observe(self, ensure_job_done: bool = False) -> Callable[
        [Callable[Concatenate[IBMQJob, ARGS], T]],
        Callable[ARGS, None],
    ]:
        '''
        decorator
        '''
        def dec(action: Callable[Concatenate[IBMQJob, ARGS], None]) -> Callable[ARGS, None]:
            @wraps(action)
            def wrapped_action(**kwargs) -> None:
                def handler(job: IBMQJob) -> None:
                    if ensure_job_done and (job is None or not job.done()):
                        print('...'); # clears output
                        return None;
                    self.show_loading();
                    action(job, **kwargs);
                    self.hide_loading();
                    return;
                display(widgets.interactive_output(
                    f = handler,
                    controls = dict(
                        job = self.dropdown_jobs,
                    ),
                ));
                return;
            return wrapped_action;
        return dec;

    def create(self):
        '''
        Method to create and link widgets
        '''
        if self.queue:
            enums = list(BACKEND);
            options_backend = [('—', None)] + [ (e.value, e) for e in enums if e != BACKEND.LEAST_BUSY ];
            options_jobs = [('—', None)] + ([] if self.job is None else [(self.job.job_id(), self.job)]);
            try:
                index_backend = enums.index(self.option)
            except:
                index_backend = 0;
            index_jobs = 0 if self.job is None else 1;
        else:
            enums = list(BACKEND_SIMULATOR);
            if isinstance(self.option, BACKEND_SIMULATOR):
                enums = [ self.option ];
            options_backend = [ (e.value, e) for e in enums ];
            options_jobs = [(self.job.job_id(), self.job)];
            try:
                index_backend = enums.index(self.option)
            except:
                index_backend = 0;
            index_jobs = 0;

        self.output = widgets.Output();

        self.dropdown_backends = widgets.Dropdown(
            description='backend',
            options = options_backend,
            index = index_backend,
            style = {
                'description_width': 'initial',
            },
            visible = True,
        );

        self.dropdown_jobs = widgets.Dropdown(
            description='job',
            options = options_jobs,
            index = index_jobs,
            style = {
                'description_width': 'initial',
            },
            visible = True,
        );

        self.text_status = widgets.HTML(
            value = f'Job status: —'
        );

        self.text_pending = widgets.HTML(
            value = '<span style="color:red;font-weight:bold;"><b>loading...</b></span>',
        );

        self.dropdown_backends.observe(self.handler_upd_backend, names='value');
        self.dropdown_jobs.observe(self.handler_upd_job, names='value');
        if self.queue:
            self.handler_upd_backend();
            self.handler_upd_job();

        ui = widgets.VBox([
            self.dropdown_backends,
            self.dropdown_jobs,
            self.text_status,
            self.text_pending,
        ]);

        self.show_loading();
        display(ui);
        self.hide_loading();
        return;

    def handler_upd_backend(self, change: Optional[dict] = None):
        '''
        Handler to update list of jobs upon choice of backend.
        '''
        option = self.dropdown_backends.value;
        if change is not None:
            option: BACKEND = change['new'];
        if not self.queue:
            return;
        self.show_loading();
        jobs = get_list_of_jobs(option=option);
        self.hide_loading();
        value = self.dropdown_jobs.value;
        self.dropdown_jobs.index = 0;
        self.dropdown_jobs.options = [('—', None)] + [(job.job_id(), job) for job in jobs];
        if value is not None and value not in jobs:
            self.dropdown_jobs.value = None;
        return;

    def handler_upd_job(self, change: Optional[dict] = None):
        '''
        Handler to update status upon choice of job.
        '''
        job = self.dropdown_jobs.value;
        if change is not None:
            job: Optional[IBMQJob] = change['new'];
        status = '—' if job is None else job.status().value;
        self.text_status.value = f'Job status: <b>{status.capitalize()}</b>';
        return;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DECORATOR
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def recover_job(
    option: Optional[BACKEND] = None,
    queue: bool = False,
    job: Optional[IBMQJob] = None,
    ensure_job_done: bool = False,
) -> Callable[[Callable[Concatenate[IBMQJob, ARGS], T]], Callable[ARGS, None]]:
    '''
    Decorator to ease recover and working with IBMQ jobs.
    '''
    widget = RecoverJobWidget(option=option, queue=queue, job=job);
    widget.create();
    dec = widget.observe(ensure_job_done);
    return dec;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_list_of_jobs(option: Optional[BACKEND]) -> list[IBMQJob]:
    if option is None:
        return [];
    with CreateBackend(option=option) as (_, backend):
        backend.jobs()
        if backend is None:
            return [];
        return backend.jobs(limit=10, descending=True);
