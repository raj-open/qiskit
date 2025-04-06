#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# IMPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import SkipValidation

from src._core.env import *
from src.api.latest import *
from src.thirdparty.code import *
from src.thirdparty.config import *
from src.thirdparty.misc import *
from src.thirdparty.quantum import *
from src.thirdparty.render import *
from src.thirdparty.system import *
from src.thirdparty.types import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# EXPORTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__all__ = [
    "CreateBackend",
    "connect_to_backend",
    "display_backends",
    "get_ibm_account",
]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# CONSTANTS / LOCAL VARIABLES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# local usage only
_provider: QkAccountProvider | None = None
T = TypeVar("T")
ARGS = ParamSpec("ARGS")


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# METHODS: backend
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


class CreateBackend(BaseModel):
    """
    Creates connection to IBM `qiskit` backend.

    @inputs
    - `nr_qubits`    - <integer> default=1; Number of qubits required (only relevant for cloud computations).
    - `option`       - enum<BACKEND | BACKEND_SIMULATOR>; choice of simulator/backend.
    - `force_reload` - <boolean> default=false; Whether to force reload IBM account. Only relevant for cloud computations.

    NOTE: to be used with `with`-blocks.
    """

    model_config = ConfigDict(
        extra="forbid",
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    option: BACKEND | BACKEND_SIMULATOR
    nr_qubits: int = Field(default=1)
    force_reload: bool = Field(default=False)

    provider: SkipValidation[IBMProvider] | None = Field(default=None, init=False)
    be: SkipValidation[QkBackend] | None = Field(default=None, init=False)

    def model_post_init(self, __context: Any):
        if isinstance(self.option, BACKEND):
            self.provider = get_ibm_account(force_reload=self.force_reload)

        return

    def __enter__(self) -> tuple[BACKEND | BACKEND_SIMULATOR, QkBackend | None]:
        option = self.option

        match option, self.provider:
            case BACKEND_SIMULATOR():
                self.be = QkBasicProvider.get_backend(option.value)
                latest_state.set_backend(option=option, queue=False)

            case BACKEND.LEAST_BUSY, QkAccountManager():

                def filt(x: Back) -> bool:
                    return (
                        x.configuration().n_qubits >= self.nr_qubits
                        and x.configuration().simulator == False
                        and x.status().operational == True
                    )

                self.be = ibm_least_busy(self.provider.backends(filters=filt))
                option = backend_from_name(name=str(self.be))
                latest_state.set_backend(option=option, queue=True)

            case BACKEND(), QkAccount():
                try:
                    self.be = self.provider.get_backend(option.value)
                    latest_state.set_backend(option=option, queue=True)

                except Exception as _:
                    self.be = None
                    latest_state.set_backend(option=None, queue=True)

            case _:
                # NOTE: this should not occur
                value = option.value if isinstance(option, Enum) else option
                raise Exception(f"invalid option {value} or no account provider found")

        return option, self.be

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if isinstance(self.be, QkBackend):
            del self.be
            self.be = None

        return


# decorator
def connect_to_backend(
    option: BACKEND | BACKEND_SIMULATOR,
    n: int = 1,
    force_reload: bool = False,
) -> Callable[
    [Callable[Concatenate[BACKEND | BACKEND_SIMULATOR, QkBackend, ARGS], T]],
    Callable[ARGS, T | None],
]:
    """
    Decorator to ease connection to IBM backend.
    """

    def dec(
        action: Callable[Concatenate[BACKEND | BACKEND_SIMULATOR, QkBackend, ARGS], T],
    ) -> Callable[ARGS, T | None]:
        be = CreateBackend(option=option, nr_qubits=n, force_reload=force_reload)

        @wraps(action)
        def wrapped_action(**kwargs) -> T | None:
            with be as (option, backend):
                if backend is None:
                    return
                return action(option, backend, **kwargs)

        return wrapped_action

    return dec


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def connect_to_ibm_account_force_reload() -> IBMProvider:
    """
    Connects to IBM Lab session with force reload of credentials.
    """
    load_dotenv(dotenv_path="." or os.getcwd())
    env = dotenv_values(".env")
    token = env.get("TOKEN")
    hub = env.get("HUB")
    group = env.get("GROUP")
    project = env.get("PROJECT")
    url = env.get("URL")

    # QISKIT_IBM_TOKEN, QISKIT_IBM_URL and QISKIT_IBM_INSTANCE
    provider = IBMProvider(
        token=token,
        url=url,
        # TODO: update to latest
        hub=hub,
        group=group,
        project=project,
        overwrite=True,
        warnings=False,
    )
    IBMProvider.save_account(
        token=token,
        url=url,
        # TODO: update these
        # instance=instance,
        # name=name,
        # proxies=proxies,
        # verify=verify,
        # overwrite=overwrite,
    )

    return provider


def display_backends():
    provider = get_ibm_account(force_reload=False)
    backends = provider.backends()
    names_simulator = [str(be) for be in backends if be.configuration().simulator]  # fmt: skip
    names_queue = [str(be) for be in backends if not be.configuration().simulator]  # fmt: skip
    items_simulator = "\n".join([f"<li>{item}</li>" for item in names_simulator])
    items_queue = "\n".join([f"<li>{item}</li>" for item in names_queue])
    display(
        HTML(
            dedent(
                f"""
                <b>AVAILABLE BACKENDS (SIMULATOR):</b>
                <ul>
                {items_simulator}
                </ul>
                </br>
                <b>AVAILABLE BACKENDS (QUEUE):</b>
                <ul>
                {items_queue}
                </ul>
                """
            )
        )
    )


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# AUXILIARY METHODS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def get_ibm_account(*, force_reload: bool = False) -> IBMProvider:
    """
    Connects to IBM Lab session.

    Note:
    - Requires .env file in root folder of project with TOKEN entry.
    - use `force_reload=True` to reload credentials. Otherwise only reloads credentials if current ones do not work.

    """
    global _provider

    match force_reload, _provider:
        case True, _:
            _provider = connect_to_ibm_account_force_reload()

        case _, None:
            try:
                # NOTE: if saved, should load from state
                _provider = IBMProvider()

            except Exception as _:
                _provider = connect_to_ibm_account_force_reload()

    return _provider
