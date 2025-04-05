# NOTE: shell does not work for both unix and windows
# set shell := [ "bash", "-c" ]

_default:
    @- just --unsorted --list

menu:
    @- just --unsorted --choose

# ----------------------------------------------------------------
# Justfile
# Recipes for various workflows.
# ----------------------------------------------------------------

set dotenv-load := true
set positional-arguments := true

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# VARIABLES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PATH_ROOT := justfile_directory()
CURRENT_DIR := invocation_directory()
OS := if os_family() == "windows" { "windows" } else { "linux" }
PYVENV_ON := if os_family() == "windows" { ". .venv/Scripts/activate" } else { ". .venv/bin/activate" }
PYVENV := if os_family() == "windows" { "python" } else { "python3" }
LINTING := "ruff"
GEN_MODELS := "datamodel_code_generator"
GEN_MODELS_DOCUMENTATION := "openapi-generator-cli"

# --------------------------------
# Macros
# --------------------------------

_clean-all-files path pattern:
    #!/usr/bin/env bash
    find {{path}} -type f -name "{{pattern}}" -exec basename {} \; 2> /dev/null
    find {{path}} -type f -name "{{pattern}}" -exec rm {} \; 2> /dev/null
    exit 0;

_clean-all-folders path pattern:
    #!/usr/bin/env bash
    find {{path}} -type d -name "{{pattern}}" -exec basename {} \; 2> /dev/null
    find {{path}} -type d -name "{{pattern}}" -exec rm -rf {} \; 2> /dev/null
    exit 0;

_check-python-tool tool name:
    @just _check-tool "{{PYVENV}} -m {{tool}}" "{{name}}"

_check-python-bin tool name:
    @just _check-tool "{{tool}}" "{{name}}"

_check-tool tool name:
    #!/usr/bin/env bash
    success=false
    {{PYVENV_ON}} && {{tool}} --version >> /dev/null 2> /dev/null && success=true;
    {{PYVENV_ON}} && {{tool}} --help >> /dev/null 2> /dev/null && success=true;
    # NOTE: if exitcode is 251 (= help or print version), then render success.
    if [[ "$?" == "251" ]]; then success=true; fi
    # FAIL tool not installed
    if ( $success ); then
        echo -e "Tool \x1b[2;3m{{name}}\x1b[0m installed correctly.";
        exit 0;
    else
        echo -e "Tool \x1b[2;3m{{tool}}\x1b[0m did not work." >> /dev/stderr;
        echo -e "Ensure that \x1b[2;3m{{name}}\x1b[0m (-> \x1b[1mjust build\x1b[0m) installed correctly and system paths are set." >> /dev/stderr;
        exit 1;
    fi

_generate-documentation path_schema target_path name:
    @{{PYVENV_ON}} && {{GEN_MODELS_DOCUMENTATION}} generate \
        --skip-validate-spec \
        --input-spec {{path_schema}}/schema-{{name}}.yaml \
        --generator-name markdown \
        --output "{{target_path}}/{{name}}"

_build-documentation-recursively path_schema target_path:
    #!/usr/bin/env bash
    while read path; do
        if [[ "${path}" == "" ]]; then continue; fi
        path="${path##*/}";
        name="$( echo """${path}""" | sed -E """s/^schema-(.*)\.yaml$/\1/g""")";
        echo "- generate documentation for ${name}."
        just _generate-documentation "{{path_schema}}" "{{target_path}}" "${name}";
    done <<< "$( ls -f {{path_schema}}/schema-*.yaml )";
    exit 0;

_generate-models path_schema target_path name:
    @ # cf. https://github.com/koxudaxi/datamodel-code-generator?tab=readme-ov-file#all-command-options
    @{{PYVENV_ON}} && {{PYVENV}} -m {{GEN_MODELS}} \
        --input-file-type openapi \
        --output-model-type pydantic_v2.BaseModel \
        --encoding "UTF-8" \
        --disable-timestamp \
        --use-schema-description \
        --use-standard-collections \
        --use-union-operator \
        --use-default-kwarg \
        --field-constraints \
        --output-datetime-class AwareDatetime \
        --capitalise-enum-members \
        --enum-field-as-literal one \
        --set-default-enum-member \
        --use-subclass-enum \
        --allow-population-by-field-name \
        --snake-case-field \
        --strict-nullable \
        --use-double-quotes \
        --target-python-version 3.11 \
        --input {{path_schema}}/schema-{{name}}.yaml \
        --output {{target_path}}/{{name}}.py

_generate-models-recursively path_schema target_path:
    #!/usr/bin/env bash
    while read path; do
        if [[ "${path}" == "" ]]; then continue; fi
        path="${path##*/}";
        name="$( echo """${path}""" | sed -E """s/^schema-(.*)\.yaml$/\1/g""")";
        echo "- generate models for ${name}."
        just _generate-models "{{path_schema}}" "{{target_path}}" "${name}";
    done <<< "$( ls -f {{path_schema}}/schema-*.yaml )";
    exit 0;

# ----------------------------------------------------------------
# TARGETS
# ----------------------------------------------------------------

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: build
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

setup:
    @echo "TASK: SETUP"
    @mkdir -p "data"
    @mkdir -p "setup"
    @# For general setup
    @- cp -n "templates/template.env" ".env"
    @- cp -n "templates/template-config.yaml" "setup/config.yaml"

build:
    @just build-venv
    @just build-requirements
    @just check-system-requirements
    @just build-models

build-venv:
    @echo "create venv if not exists"
    @- ${PYTHON_PATH} -m venv .venv 2> /dev/null

build-requirements:
    @just build-requirements-basic
    @just build-requirements-dependencies

build-requirements-basic:
    @{{PYVENV_ON}} && {{PYVENV}} -m pip install --upgrade pip
    @{{PYVENV_ON}} && {{PYVENV}} -m pip install ruff uv

build-requirements-dependencies:
    @{{PYVENV_ON}} && {{PYVENV}} -m uv pip install \
        --exact \
        --strict \
        --compile-bytecode \
        --no-python-downloads \
        --requirements pyproject.toml
    @{{PYVENV_ON}} && {{PYVENV}} -m uv sync

build-models:
    @echo "SUBTASK: build data models from schemata."
    @rm -rf "src/models/generated" 2> /dev/null
    @mkdir -p "src/models/generated"
    @touch "src/models/generated/__init__.py"
    @just _generate-models-recursively "models" "src/models/generated"

build-docs:
    @echo "SUBTASK: build documentation for data models from schemata."
    @rm -rf "docs/models" 2> /dev/null
    @mkdir -p "docs/models"
    @- just _build-documentation-recursively "models" "docs/models"
    @- just _clean-all-files "." ".openapi-generator*"
    @- just _clean-all-folders "." ".openapi-generator*"

build-archive:
    @echo "TASK: create .zip archive of project"
    @# store current state
    @git add . && git commit --no-verify --allow-empty -m "temp"
    @# create archive
    @git archive -o dist/${PROJECT_NAME}-$(cat dist/VERSION).zip "HEAD"
    @# undo above commit
    @git reset --soft HEAD~1 && git reset .

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: execution
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

run *args:
    @echo "Not implemented!"
    @# {{PYVENV_ON}} && {{PYVENV}} -m src.main {{args}}

# runs python notebook (in browser)
notebook name="examples":
    @# create config/data folders if missing:
    @just build-misc
    @# run notebook
    @{{PYVENV_ON}} && {{PYVENV}} -m jupyter notebook notebooks/{{name}}.ipynb

# exports notebook to format: html, markdown, pdf, latex.
export name format="html" theme="light":
    @{{PYVENV_ON}} && {{PYVENV}} -m jupyter nbconvert \
        --allow-chromium-download \
        --HTMLExporter.theme={{theme}} \
        --TemplateExporter.exclude_input=false \
        --to {{format}} \
        --output-dir examples \
        notebooks/{{name}}.ipynb

serve-notebooks:
    #!/usr/bin/env bash
    if [[ "{{OS}}" == "linux" ]]; then
        ps aux | grep "uvicorn src.api:app"
    else
        netstat -ano | findstr "uvicorn src.api:app"
    fi

# --------------------------------
# TARGETS: development
# --------------------------------

# Recipe only works if local file test.py exists
dev *args:
    @just _reset-logs
    @{{PYVENV_ON}} && {{PYVENV}} test.py {{args}}

# --------------------------------
# TARGETS: terminate execution
# --------------------------------

# finds pid based on port
get-pid port="":
    #!/usr/bin/env bash
    port=$(echo "{{port}}" | grep -q . && echo "{{port}}" || echo ${HTTP_PORT})
    lsof -ti ":{{port}}" 2> /dev/null

# kills process based on process ID
kill-pid pid:
    @echo "Killing {{pid}}"
    @kill {{pid}} 2> /dev/null

kill-port port="":
    #!/usr/bin/env bash
    port=$(echo "{{port}}" | grep -q . && echo "{{port}}" || echo ${HTTP_PORT})
    PID="$( just get-pid "{{port}}" )";
    if [[ "${PID}" == "" ]]; then
        echo "No process running on PORT {{port}}";
    else
        echo "Process ${PID} running on PORT {{port}}";
        just kill-pid "${PID}";
    fi
    exit 0;

kill-notebooks port="":
    #!/usr/bin/env bash
    # NOTE: only need to do this for linux.
    port=$(echo "{{port}}" | grep -q . && echo "{{port}}" || echo ${HTTP_PORT})
    if [[ "{{OS}}" == "linux" ]]; then
        echo "Terminating all processes associated to app and port {{port}}."
        while read pid; do
            if [[ "$pid" == "" ]]; then continue; fi
            echo "- killing process $pid:"
            kill -9 ${pid};
        done <<< $( pgrep -f "uvicorn src.api:app --port {{port}}" )
    fi

# --------------------------------
# TARGETS: tests
# --------------------------------

tests:
    @just tests-unit

tests-logs log_path="logs":
    @just _reset-logs "{{log_path}}"
    @- just tests
    @just _display-logs

test-unit path *args:
    @just _reset-test-logs "unit"
    @{{PYVENV_ON}} && {{PYVENV}} -m pytest "{{path}}" {{args}}

test-unit-one path method:
    @just test-unit "{{path}}" -k "{{method}}"

tests-unit:
    @just test-unit "tests/unit" --cov-reset --cov="."

# lists markers for optional tests
test-unit-list-flags:
    @{{PYVENV_ON}} && {{PYVENV}} -m pytest --markers

test-unit-optional path flags="'(azure or remote)'":
    @just test-unit "{{path}}" -m "{{flags}}"

test-unit-one-optional path method flags="'(azure or remote)'":
    @just test-unit "{{path}}" -k "{{method}}" -m "{{flags}}"

tests-unit-optional flags="'(azure or remote)'":
    @just test-unit "tests/unit" -m "{{flags}}"

# --------------------------------
# TARGETS: qa
# NOTE: use for development only.
# --------------------------------

qa:
    @{{PYVENV_ON}} && {{PYVENV}} -m coverage report -m

coverage source_path tests_path log_path="logs":
    @just _reset-logs "{{log_path}}"
    @{{PYVENV_ON}} && {{PYVENV}} -m pytest {{tests_path}} \
        --ignore=tests/integration \
        --cov-reset \
        --cov={{source_path}} \
        --capture=tee-sys \
        2> /dev/null
    @just _display-logs

# --------------------------------
# TARGETS: prettify
# --------------------------------

lint path:
    @{{PYVENV_ON}} && {{PYVENV}} -m {{LINTING}} check \
        --respect-gitignore \
        --show-fixes \
        --no-unsafe-fixes \
        --exit-zero \
        --fix \
        "{{path}}"
    @{{PYVENV_ON}} && {{PYVENV}} -m {{LINTING}} format \
        --respect-gitignore \
        "{{path}}"

lint-dry path:
    @{{PYVENV_ON}} && {{PYVENV}} -m {{LINTING}} check \
        --respect-gitignore \
        --no-unsafe-fixes \
        --exit-zero \
        --diff \
        "{{path}}"

lint-check path:
    @{{PYVENV_ON}} && {{PYVENV}} -m {{LINTING}} check \
        --respect-gitignore \
        --no-unsafe-fixes \
        --exit-zero \
        --verbose \
        "{{path}}"

prettify:
    @just lint "src"
    @just lint "tests"

prettify-dry:
    @just lint-dry "src"
    @just lint-dry "tests"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: clean
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

clean log_path="logs":
    @- just clean-notebooks
    @just clean-venv
    @just clean-basic "{{log_path}}"

clean-basic log_path="logs":
    @echo "All system artefacts will be force removed."
    @- just _clean-all-files "." ".DS_Store" 2> /dev/null
    @echo "All test artefacts will be force removed."
    @- rm -rf ".pytest_cache" 2> /dev/null
    @- rm -f ".coverage" 2> /dev/null
    @echo "All build artefacts will be force removed."
    @- rm -rf ".venv" 2> /dev/null
    @- rm -rf "build" 2> /dev/null
    @- just _clean-all-folders "." ".idea" 2> /dev/null
    @- just _clean-all-folders "." "__pycache__" 2> /dev/null

clean-venv:
    @echo "VENV will be removed."
    @- just _delete-if-folder-exists ".venv" 2> /dev/null

clean-notebooks:
    @echo "Clean python notebooks."
    @{{PYVENV_ON}} && {{PYVENV}} -m jupyter nbconvert --clear-output --inplace **/*.ipynb
    @- {{PYVENV_ON}} && {{PYVENV}} -m jupytext --update-metadata '{"vscode":""}' **/*.ipynb 2> /dev/null
    @- {{PYVENV_ON}} && {{PYVENV}} -m jupytext --update-metadata '{"vscode":null}' **/*.ipynb 2> /dev/null

# --------------------------------
# TARGETS: logging, session
# --------------------------------

_clear-logs log_path="logs":
    @rm -rf "{{log_path}}" 2> /dev/null

_create-logs log_path="logs":
    @just _create-logs-part "debug" "{{log_path}}"
    @just _create-logs-part "out" "{{log_path}}"
    @just _create-logs-part "err" "{{log_path}}"

_create-logs-part part log_path="logs":
    @mkdir -p "{{log_path}}"
    @touch "{{log_path}}/{{part}}.log"

_reset-logs log_path="logs":
    @rm -rf "{{log_path}}" 2> /dev/null
    @just _create-logs "{{log_path}}"

_reset-test-logs kind:
    @rm -rf "tests/{{kind}}/logs" 2> /dev/null
    @just _create-logs-part "debug" "tests/{{kind}}/logs"

_display-logs:
    @echo ""
    @echo "Content of logs/debug.log:"
    @echo "----------------"
    @echo ""
    @- cat logs/debug.log
    @echo ""
    @echo "----------------"

watch-logs n="10":
    @tail -f -n {{n}} logs/out.log

watch-logs-err n="10":
    @tail -f -n {{n}} logs/err.log

watch-logs-debug n="10":
    @tail -f -n {{n}} logs/debug.log

watch-logs-all n="10":
    @just watch-logs {{n}} &
    @just watch-logs-err {{n}} &
    @just watch-logs-debug {{n}} &

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: requirements
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

check-system:
    @echo "Operating System detected:  {{os_family()}}"
    @echo "Python command used:        ${PYTHON_PATH}"
    @echo "Python command for venv:    {{PYVENV}}"
    @echo "Python path for venv:       $( {{PYVENV_ON}} && which {{PYVENV}} )"

check-system-requirements:
    @just _check-python-tool "{{GEN_MODELS}}" "datamodel-code-generator"
    @just _check-tool "{{GEN_MODELS_DOCUMENTATION}}" "openapi-code-generator"
    @just _check-python-tool "{{LINTING}}" "{{LINTING}}"
    @just _check-python-tool "jupyter" "jupyter"
    @just _check-python-tool "jupytext" "jupytext"
