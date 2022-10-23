# set shell := [ "bash", "-uc" ]
_default:
    @- just --unsorted --list
menu:
    @- just --unsorted --choose
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Justfile
# NOTE: Do not change the contents of this file!
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# VARIABLES
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

OS := if os_family() == "windows" { "windows" } else { "linux" }
PYTHON := if os_family() == "windows" { "py -3" } else { "python3" }
GEN_MODELS := "datamodel-codegen"
GEN_MODELS_DOCUMENTATION := "openapi-generator"
PORT := "8000"
URL_API := "http://127.0.0.1:8000/docs"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Macros
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_create-file-if-not-exists fname:
    @touch "{{fname}}";

_create-folder-if-not-exists path:
    @if ! [ -d "{{path}}" ]; then mkdir "{{path}}"; fi

_delete-if-file-exists fname:
    @if [ -f "{{fname}}" ]; then rm "{{fname}}"; fi

_delete-if-folder-exists path:
    @if [ -d "{{path}}" ]; then rm -rf "{{path}}"; fi

_clean-all-files pattern:
    @find . -type f -name "{{pattern}}" -exec basename {} \; 2> /dev/null
    @- find . -type f -name "{{pattern}}" -exec rm {} \; 2> /dev/null

_clean-all-folders pattern:
    @find . -type d -name "{{pattern}}" -exec basename {} \; 2> /dev/null
    @- find . -type d -name "{{pattern}}" -exec rm -rf {} \; 2> /dev/null

_copy-file-if-not-exists path_from path_to:
    @- cp -n "{{path_from}}" "{{path_to}}"

_check-python-tool tool name:
    #!/usr/bin/env bash
    success=false
    {{tool}} --help >> /dev/null 2> /dev/null && success=true;
    # NOTE: if exitcode is 251 (= help or print version), then render success.
    [[ "$?" == "251" ]] && success=true;
    # FAIL tool not installed
    if ( $success ); then
        echo -e "Tool \x1b[2;3m{{tool}}\x1b[0m installed correctly.";
        exit 0;
    else
        echo -e "Tool \x1b[2;3m{{tool}}\x1b[0m did not work." >> /dev/stderr;
        echo -e "Ensure that \x1b[2;3m{{name}}\x1b[0m (-> \x1b[1mjust build\x1b[0m) installed correctly and system paths are set." >> /dev/stderr;
        exit 1;
    fi

_generate-models path name:
    @{{GEN_MODELS}} \
        --input-file-type openapi \
        --encoding "UTF-8" \
        --disable-timestamp \
        --use-schema-description \
        --allow-population-by-field-name \
        --snake-case-field \
        --strict-nullable \
        --target-python-version 3.10 \
        --input {{path}}/{{name}}-schema.yaml \
        --output {{path}}/generated/{{name}}.py

_generate-models-documentation path_schema path_docs name:
    @{{GEN_MODELS_DOCUMENTATION}} generate \
        --input-spec {{path_schema}}/{{name}}-schema.yaml \
        --generator-name markdown \
        --output "{{path_docs}}/{{name}}"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: build
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

build:
    @just build-misc
    @just build-requirements
    @just _check-system-requirements
    @just build-models
build-misc:
    @# create database if not exists:
    @just _create-folder-if-not-exists "data"
    @# copy template of configs to setup if not exists:
    @just _create-folder-if-not-exists "setup"
    @just _copy-file-if-not-exists "templates/template-config.yaml" "setup/config.yaml"
    @just _copy-file-if-not-exists "templates/.env" ".env"
build-requirements:
    @{{PYTHON}} -m pip install --disable-pip-version-check -r requirements.txt
build-models:
    @echo "Generate data models from schemata."
    @just _delete-if-folder-exists "models/generated"
    @just _create-folder-if-not-exists "models/generated"
    @- #just _generate-models "models" "config"
build-documentation:
    @echo "Generate documentations data models from schemata."
    @just _delete-if-folder-exists "docs"
    @just _create-folder-if-not-exists "docs"
    @- #just _generate-models-documentation "models" "docs" "config"
    @- just _clean-all-files .openapi-generator*
    @- just _clean-all-folders .openapi-generator*

dist:
    @just build
    @just build-documentation

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: run
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# runs using commandline interface
run:
    @# create config/data folders if missing:
    @just build-misc
    @# run source code als cli
    @echo "Not implemented!"

# runs python notebook (in browser)
notebook name="main":
    @# create config/data folders if missing:
    @just build-misc
    @# run notebook
    @{{PYTHON}} -m jupyter notebook notebooks/{{name}}.ipynb

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: tests
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

tests: tests-unit tests-integration
tests-logs:
    @just _create-logs
    @- just tests
    @just _display-logs
tests-unit-logs:
    @just _create-logs
    @- just tests-unit
    @just _display-logs
tests-integration-logs:
    @just _create-logs
    @- just tests-integration
    @just _display-logs
tests-unit:
    @{{PYTHON}} -m pytest tests \
        --ignore=tests/integration \
        --cov-reset \
        --cov=. \
        2> /dev/null
tests-integration:
    @{{PYTHON}} -m pytest tests/integration 2> /dev/null

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: qa
# NOTE: use for development only.
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

qa:
    @{{PYTHON}} -m coverage report -m
coverage source_path tests_path:
    @just _create-logs
    @-just _coverage-no-logs "{{source_path}}" "{{tests_path}}"
    @just _display-logs
_coverage-no-logs source_path tests_path:
    @{{PYTHON}} -m pytest {{tests_path}} \
        --ignore=tests/integration \
        --cov-reset \
        --cov={{source_path}} \
        --capture=tee-sys \
        2> /dev/null

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: clean
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

clean:
    @just clean-basic
    @just pre-commit
pre-commit:
    @echo "Clean python notebooks."
    @{{PYTHON}} -m jupyter nbconvert --clear-output --inplace **/*.ipynb
    @- {{PYTHON}} -m jupytext --update-metadata '{"vscode":""}' **/*.ipynb 2> /dev/null
    @- {{PYTHON}} -m jupytext --update-metadata '{"vscode":null}' **/*.ipynb 2> /dev/null
clean-basic:
    @echo "All system artefacts will be force removed."
    @- just _clean-all-files ".DS_Store" 2> /dev/null
    @echo "All build artefacts will be force removed."
    @- just _clean-all-folders "__pycache__" 2> /dev/null
    @- just _delete-if-folder-exists "models/generated" 2> /dev/null
    @echo "All test artefacts will be force removed."
    @- just _clean-all-folders ".pytest_cache" 2> /dev/null
    @- just _delete-if-file-exists ".coverage" 2> /dev/null
    @- just _delete-if-folder-exists "logs" 2> /dev/null

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: logging
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_create-logs:
    @# For logging purposes (since stdout is rechanneled):
    @just _delete-if-file-exists "logs/debug.log"
    @just _create-folder-if-not-exists "logs"
    @just _create-file-if-not-exists "logs/debug.log"
_display-logs:
    @echo ""
    @echo "Content of logs/debug.log:"
    @echo "----------------"
    @echo ""
    @- cat logs/debug.log
    @echo ""
    @echo "----------------"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: processes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

api-process:
    #!/usr/bin/env bash
    if [[ "{{OS}}" == "linux" ]]; then
        ps aux | grep "uvicorn src.api:app"
    else
        netstat -ano | findstr "uvicorn src.api:app"
    fi
kill-api-process:
    #!/usr/bin/env bash
    # NOTE: only need to do this for linux.
    if [[ "{{OS}}" == "linux" ]]; then
        echo "Terminating all processes associated to app and port {{PORT}}."
        while read pid; do
            if [[ "$pid" == "" ]]; then continue; fi
            echo "- killing process $pid:"
            kill -9 ${pid};
        done <<< $( pgrep -f "uvicorn src.api:app --port {{PORT}}" )
    fi

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TARGETS: requirements
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_check-system:
    @echo "Operating System detected: {{os_family()}}."
    @echo "Python command used: {{PYTHON}}."

_check-system-requirements:
    @just _check-python-tool "{{GEN_MODELS}}" "datamodel-code-generator"
    @just _check-python-tool "{{GEN_MODELS_DOCUMENTATION}}" "openapi-code-generator"
