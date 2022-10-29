#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations;

from src.thirdparty.run import time_sleep;
from src.thirdparty.code import *;
from src.thirdparty.quantum import *;
from src.thirdparty.render import *;
from src.thirdparty.types import *;

from src.api.ibm import *;
from src.api.latest import *;

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
    btn_refresh: widgets.ToggleButton;
    text_status: widgets.HTML;
    text_pending: widgets.HTML;
    output: widgets.Output;

    def __init__(
        self,
        option: Optional[BACKEND | BACKEND_SIMULATOR] = None,
        queue: bool = False,
        job: Optional[IBMQJob] = None,
    ):
        assert queue or (job is not None), 'If no queue used, then need to provide the job.';
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
                def handler(
                    backend_option: Optional[BACKEND | BACKEND_SIMULATOR],
                    job: Optional[IBMQJob],
                    refresh: bool,
                ) -> None:
                    self.show_loading();
                    time_sleep(0.5);
                    if ensure_job_done and (job is None or not job.done()):
                        self.hide_loading();
                        print('...'); # 'clears' output
                        return None;
                    action(job, **kwargs);
                    self.hide_loading();
                    return;
                display(widgets.interactive_output(
                    f = handler,
                    controls = dict(
                        backend_option = self.dropdown_backends,
                        job = self.dropdown_jobs,
                        refresh = self.btn_refresh,
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

        self.btn_refresh = widgets.ToggleButton(description='Refresh');

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

        self.btn_refresh.observe(self.handler_update, names='value');
        self.dropdown_backends.observe(self.handler_upd_backend, names='value');
        self.dropdown_jobs.observe(self.handler_upd_job, names='value');
        if self.queue:
            self.handler_upd_backend();
            self.handler_upd_job();

        ui = widgets.VBox([
            self.dropdown_backends,
            self.dropdown_jobs,
            self.btn_refresh,
            self.text_status,
            self.text_pending,
        ]);

        self.show_loading();
        display(ui);
        self.hide_loading();
        return;

    def handler_update(self, change: Optional[dict] = None):
        '''
        Handler to force update status of job (if selected).
        '''
        self.handler_upd_job(None);
        return;

    def handler_upd_backend(self, change: Optional[dict] = None):
        '''
        Handler to update list of jobs upon choice of backend.
        '''
        # skip if in simulator:
        if not self.queue:
            return;
        # only apply if in backend.
        option: BACKEND;
        try:
            option: BACKEND = change['new'];
        except:
            option = self.dropdown_backends.value;
        self.show_loading();
        jobs = get_list_of_jobs(option=option);
        self.hide_loading();
        value = self.dropdown_jobs.value;
        self.dropdown_jobs.index = 0;
        self.dropdown_jobs.options = [('—', None)] + [(job.job_id(), job) for job in jobs];
        try:
            id = value.job_id();
            index = 1 + next(i for i, job in enumerate(jobs) if job.job_id() == id);
            self.dropdown_jobs.index = index;
        except:
            pass;
        return;

    def handler_upd_job(self, change: Optional[dict] = None):
        '''
        Handler to update status upon choice of job.
        '''
        try:
            job: Optional[IBMQJob] = change['new'];
        except:
            job = self.dropdown_jobs.value;
        status = get_job_status(job);
        self.text_status.value = f'Job status: <b>{status.capitalize()}</b>';
        return;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DECORATOR
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def recover_job(
    queue: bool,
    ensure_job_done: bool = True,
    use_latest: bool = False,
) -> Callable[[Callable[Concatenate[IBMQJob, ARGS], T]], Callable[ARGS, None]]:
    '''
    Creates a decorator to ease recovery and actions with IBMQ jobs.

    @inputs
    - `queue` - <boolean> whether the decorator is to be applied to an action on jobs from the queue.
    - `ensure_job_done` - <boolean> if `true` (default) hinders action from being performed, when job does not have DONE status.
    - `use_latest` - <boolean> if `true` tries to (internally) obtain information about latest backend+job and uses thesee as default values.

    @returns
    a decorator for actions, with example usage:
    ```py
    @recover_job(queue=True, use_latest=True)
    def do_stuff(job, key1, key2, ..., keyn):
        ...;
    ```
    which allows the action to be performed without the user having to manually recover the job details.
    An example usage (for the above):
    ```py
    do_stuff(key1, key2, ..., keyn); # no longer needs `job` argument!
    ```
    which creates a widget with dropdown menus for the selection of backend + job
    (possibly preset with default values if `use_latest=True` set in decorator)
    and which performs the action upon selection.
    '''
    # optionally recover latest backend option + job:
    last_option = latest_state.get_backend(queue) if use_latest else None;
    last_job = latest_state.get_job(queue) if use_latest else None;
    # create widget:
    widget = RecoverJobWidget(option=last_option, queue=queue, job=last_job);
    widget.create();
    # create decorator for action via widget:
    dec = widget.observe(ensure_job_done);
    return dec;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_job_status(job: Optional[IBMQJob]) -> str:
    try:
        return job.status().value;
    except:
        return '—';

def get_list_of_jobs(option: Optional[BACKEND]) -> list[IBMQJob]:
    if option is None:
        return [];
    with CreateBackend(option=option) as (_, backend):
        backend.jobs()
        if backend is None:
            return [];
        return backend.jobs(limit=10, descending=True);
