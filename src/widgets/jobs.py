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

from src.api.ibm import *;

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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# WIDGET Recover Job
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RecoverJobWidget():
    kind: Optional[BACKEND];
    provider: QkAccountProvider;

    # widget components
    dropdown_backends: widgets.Dropdown;
    dropdown_jobs: widgets.Dropdown;
    text_status: widgets.HTML;
    text_pending: widgets.HTML;
    output: widgets.Output;

    def __init__(
        self,
        kind: Optional[BACKEND] = None,
    ):
        self.kind = kind;
        return;

    def show_loading(self):
        self.text_pending.layout.visibility = 'visible';

    def hide_loading(self):
        self.text_pending.layout.visibility = 'hidden';

    def observe(self, ensure_job_done: bool = False) -> Callable[[Callable[[IBMQJob], T]], Callable[[], None]]:
        '''
        decorator
        '''
        def dec(action: Callable[[IBMQJob], None]) -> Callable[[], None]:
            @wraps(action)
            def wrapped_action() -> None:
                def handler(job: IBMQJob) -> Optional[T]:
                    if ensure_job_done and (job is None or not job.done()):
                        print('...'); # clears output
                        return None;
                    self.show_loading();
                    result = action(job);
                    self.hide_loading();
                    return result;
                out = widgets.interactive_output(
                    f = handler,
                    controls = dict(
                        job = self.dropdown_jobs,
                    ),
                );
                display(out);
                return;
            return wrapped_action;
        return dec;

    def create(self):
        '''
        Method to create and link widgets
        '''
        try:
            index = BACKEND.index(self.kind)
        except:
            index = 0;
        self.output = widgets.Output();
        self.dropdown_backends = widgets.Dropdown(
            description='backend',
            options = [('—', None)] + [ (e.value, e) for e in BACKEND if e != BACKEND.LEAST_BUSY ],
            index = index,
            style = {
                'description_width': 'initial',
            },
            visible = True,
        );
        self.dropdown_jobs = widgets.Dropdown(
            description='job',
            options = [('—', None)],
            index = 0,
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

    def handler_upd_backend(self, change):
        '''
        Handler to update list of jobs upon choice of backend.
        '''
        backend_option: BACKEND = change['new'];
        self.show_loading();
        jobs = get_list_of_jobs(kind=backend_option);
        self.hide_loading();
        value = self.dropdown_jobs.value;
        self.dropdown_jobs.index = 0;
        self.dropdown_jobs.options = [('—', None)] + [(job.job_id(), job) for job in jobs];
        if value is not None and value not in jobs:
            self.dropdown_jobs.value = None;
        return;

    def handler_upd_job(self, change):
        '''
        Handler to update status upon choice of job.
        '''
        job: Optional[IBMQJob] = change['new'];
        status = '—' if job is None else job.status().value;
        self.text_status.value = f'Job status: <b>{status.capitalize()}</b>';
        return;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DECORATOR
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def recover_job(
    ensure_job_done: bool = False,
    kind: Optional[BACKEND] = None,
    job: Optional[IBMQJob] = None,
) -> Callable[[Callable[[IBMQJob], T]], Callable[[], None]]:
    '''
    Decorator to ease recover and working with IBMQ jobs.
    '''
    if job is not None and job.done():
        def dec(action: Callable[[IBMQJob], T]) -> Callable[[], T]:
            action(job);
            return;
    else:
        widget = RecoverJobWidget(kind=kind);
        widget.create();
        dec = widget.observe(ensure_job_done);
    return dec;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_list_of_jobs(kind: Optional[BACKEND]) -> list[IBMQJob]:
    if kind is None:
        return [];
    with CreateBackend(kind=kind) as (_, backend):
        if backend is None:
            return [];
        return backend.jobs(limit=10, descending=True);
