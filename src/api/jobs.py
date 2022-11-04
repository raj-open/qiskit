#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations;

from src.thirdparty.run import time_sleep;
from src.thirdparty.misc import *;
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
    'retrieve_job'
];

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS / LOCAL VARIABLES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

LIMIT_NUM_JOBS: int = 10;

# local usage only
T = TypeVar('T');
ARGS = ParamSpec('ARGS');

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def retrieve_job(
    queue: bool,
    job_id: Optional[str] = None,
    backend_option: Optional[BACKEND | BACKEND_SIMULATOR] = None,
) -> Optional[IBMQJob]:
    '''
    Retrieves an IBMQ job by id or else the latest job.
    If not possible, returns None.

    @inputs
    - `queue`           - <boolean> `true` if job is from backend queue, `false` if from simulator.
    - `job_id`          - <string | None> optional job id.
    - `backend_option`  - <enum | None> only needed to retrieve jobs from backend queue.

    NOTE: if `queue = False` is used (i.e. simulator), then will simply attempt to retrieve the last job,
    since `qiskit` does not currently have a method to obtain jobs by id from the simulated backends.
    '''
    if not queue:
        return latest_state.get_job(queue);
    # Backend option must be from the BACKEND enum.
    if backend_option is None or not isinstance(backend_option, BACKEND):
        return None;
    # Must provide a job id.
    if job_id is None:
        return None;
    with CreateBackend(option=backend_option) as (_, backend):
        if backend is None:
            return None;
        try:
            return backend.retrieve_job(job_id);
        except:
            return None;

def retrieve_last_job_and_backend(queue: bool) -> tuple[
    Optional[IBMQJob],
    Optional[BACKEND | BACKEND_SIMULATOR],
]:
    '''
    Retrieves latest job + backend which were internally noted.
    '''
    job = latest_state.get_job(queue);
    backend_option = latest_state.get_backend(queue)
    return job, backend_option;

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# DECORATOR
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def recover_job(
    queue: bool,
    job_id: Optional[str] = None,
    backend_option: Optional[BACKEND | BACKEND_SIMULATOR] = None,
    use_latest: bool = True,
    ensure_job_done: bool = True,
    wait: bool = False,
    as_widget: bool = False,
) -> Callable[
    [Callable[Concatenate[IBMQJob, ARGS], T]],
    Callable[ARGS, None],
]:
    '''
    Creates a decorator to ease recovery and actions with IBMQ jobs.

    @inputs
    - `queue` - <boolean> whether the decorator is to be applied to an action on jobs from the queue.
    - `job_id` - <string | None> if set, will attempt to obtain job by this id. (Only applicable if not used as widget.)
    - `backend_option` - <enum | None> if set, will be used in combination with `job_id` to retrieve job.
    - `use_latest` - <boolean> if `true` tries to (internally) obtain information about latest backend + job and uses these as default values.
      - Option (semi-)ignored, if a job can be recovered from `backend_option` + `job_id`.
      - Option completely ignored, if `as_widget=True` is used.
    - `ensure_job_done` - <boolean> if `true` (default) hinders action from being performed, when job does not have DONE status.
    - `wait` - <boolean> if `true` waits for job to be finished.
    - `as_widget` - <boolean> if `true` displays a widget interface so that use can select backend + job before carrying out action.
        If `false` (default), attempts to retrieve job and carry out action if job exists and is done.

    NOTE: It is advisible to only use `wait=True` in the simulator.

    @returns
    a decorator for actions, with example usage:
    ```py
    @recover_job(queue=True, use_latest=True, as_widget=True)
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
    last_job, last_backend = retrieve_last_job_and_backend(queue) if use_latest else (None, None);
    backend_option = backend_option or last_backend;
    if as_widget:
        # retrieve job or else use latest job:
        job = retrieve_job(queue=queue, job_id=job_id, backend_option=backend_option) or last_job;
        # create widget:
        widget = RecoverJobWidget(option=backend_option, queue=queue, job=job);
        widget.create();
        # create decorator for action via widget:
        dec = widget.observe(ensure_job_done);
    else:
        def dec(action: Callable[Concatenate[IBMQJob, ARGS], T]) -> Callable[ARGS, None]:
            # modify action to obtain job first and then perform action:
            @wraps(action)
            def wrapped_action(**kwargs) -> None:
                # retrieve job or else use latest job:
                job = retrieve_job(queue=queue, job_id=job_id, backend_option=backend_option) or last_job;
                # if in simulator, forcibly wait until job is done:
                if wait:
                    display(HTML('<p style="color:blue;"><b>[INFO]</b> Wait for job to finish...</b>'));
                    job.wait_for_final_state();
                # carry out action only if done, unless `ensure_job_done=False`:
                if not ensure_job_done or is_job_done(job=job, queue=queue):
                    action(job, **kwargs);
                # otherwise optionally display feedback:
                else:
                    aspects = get_job_aspects(job=job, backend_option=backend_option);
                    display(HTML(dedent(
                        f'''
                        Job either could not be recovered or is not done.
                        Details of recovered job:
                        <ul>
                            <li>backend: <b>{aspects.backend}</b></li>
                            <li>label:   <b>{aspects.label}</b></li>
                            <li>id:      <b>{aspects.id}</b></li>
                            <li>tag:     <b>{aspects.tags}</b></li>
                            <li>status:  <b>{aspects.status}</b></li>
                        </ul>
                        Try again later or use <b><code>as_widget=True</code></b>.
                        '''
                    )));
                return;
            return wrapped_action;

    return dec;

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
        Decorator to connect a method to be performed/updated when the widget changes.
        '''
        def dec(action: Callable[Concatenate[IBMQJob, ARGS], T]) -> Callable[ARGS, None]:
            # modify action, so that it is triggered by events:
            @wraps(action)
            def wrapped_action(**kwargs) -> None:
                # embed action into an event handle:
                def handler(
                    backend_option: Optional[BACKEND | BACKEND_SIMULATOR],
                    job: Optional[IBMQJob],
                    refresh: bool,
                ) -> None:
                    self.show_loading();
                    if not ensure_job_done or is_job_done(job=job, queue=self.queue):
                        action(job, **kwargs);
                        self.hide_loading();
                    else:
                        time_sleep(0.5);
                        print('...'); # 'clears' output
                    self.hide_loading();
                    return;
                # connect event handle to react to changes to controls:
                display(widgets.interactive_output(
                    f = handler,
                    controls = dict(
                        backend_option = self.dropdown_backends,
                        job = self.dropdown_jobs,
                        refresh = self.btn_refresh,
                    ),
                ));
                return;
            # return modified action:
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
            value = self.text_status_value(),
        );

        self.text_pending = widgets.HTML(
            value = '<span style="color:red;font-weight:bold;"><b>loading...</b></span>',
        );

        self.btn_refresh.observe(self.handler_update, names='value');
        self.dropdown_backends.observe(self.handler_upd_backend, names='value');
        self.dropdown_jobs.observe(self.handler_upd_job, names='value');
        if self.queue:
            self.handler_update();

        ui = widgets.VBox([
            widgets.HBox([
                widgets.VBox([
                    self.dropdown_backends,
                    self.dropdown_jobs,
                ]),
                self.text_status,
            ], layout={
                'display': 'flex',
                'align_items': 'center',
            }),
            self.btn_refresh,
            self.text_pending,
        ], layout = {
            'padding': '10pt 10pt',
        });

        self.show_loading();
        display(ui);
        self.hide_loading();
        return;

    def handler_update(self, change: Optional[dict] = None):
        '''
        Handler to force update status of job (if selected).
        '''
        self.handler_upd_backend(None);
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
        self.text_status.value = self.text_status_value(job);
        return;

    def text_status_value(self, job: Optional[IBMQJob] = None) -> str:
        aspects = get_job_aspects(job=job);
        return f'''
        <div style='padding:0pt 10pt;'>
            Job label: <b>{aspects.label.capitalize()}</b>
            </br>
            id: <tt>{aspects.id}</tt>
            </br>
            tags: <i><tt>{aspects.tags}</i></tt>
            </br>
            status: <b><tt>{aspects.status.capitalize()}</tt></b>
        </div>
        ''';

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_list_of_jobs(option: Optional[BACKEND | BACKEND_SIMULATOR]) -> list[IBMQJob]:
    if not isinstance(option, BACKEND):
        return [];
    with CreateBackend(option=option) as (_, backend):
        if backend is None:
            return [];
        try:
            return backend.jobs(limit=LIMIT_NUM_JOBS, descending=True);
        except:
            return [];

@dataclass
class JobAspects():
    backend: str = field(default='—');
    label: str = field(default='—');
    id: str = field(default='—');
    tags: str = field(default='—');
    status: str = field(default='—');

def get_job_aspects(
    job: Optional[IBMQJob] = None,
    backend_option: Optional[BACKEND | BACKEND_SIMULATOR] = None,
) -> JobAspects:
    return JobAspects(
        backend = get_backend_name(backend_option),
        label = get_job_name(job),
        id = get_job_id(job),
        tags = get_job_tags(job),
        status = get_job_status(job),
    );

def get_job_id(job: Optional[IBMQJob]) -> str:
    try:
        return job.job_id();
    except:
        pass;
    return '—';

def get_job_name(job: Optional[IBMQJob]) -> str:
    try:
        label = job.name() or '';
        if label != '':
            return label;
    except:
        pass;
    return '—';

def get_job_tags(job: Optional[IBMQJob]) -> str:
    try:
        tags = job.tags();
        if len(tags) > 0:
            return '#' + ', #'.join(tags);
    except:
        pass;
    return '—';

def get_job_status(job: Optional[IBMQJob]) -> str:
    try:
        return str(job.status().value);
    except:
        pass;
    return '—';

def get_backend_name(backend_option: Optional[BACKEND | BACKEND_SIMULATOR]):
    if backend_option is not None:
        return str(backend_option.value);
    return '—';

def is_job_done(job: Optional[IBMQJob], queue: bool) -> bool:
    if job is None:
        return False;
    return job.done();
