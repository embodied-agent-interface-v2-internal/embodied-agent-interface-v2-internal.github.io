# Developer entry points. `make help` lists them.
#
# Two packages independently print an advisory about the contested MkDocs 2.0
# transition on every build, and they read different environment variables:
# Material uses NO_MKDOCS_2_WARNING, properdocs (pulled in transitively by
# mkdocs-gen-files) uses DISABLE_MKDOCS_2_WARNING. Both are informational and
# do not affect this site. See HANDOFF.md for the background.
export NO_MKDOCS_2_WARNING      := true
export DISABLE_MKDOCS_2_WARNING := true

# Machine-specific settings (e.g. ROBOPAINT_DEMOS=host:dir) go in Makefile.local, which is gitignored.
-include Makefile.local

PYTHON ?= python
PORT   ?=
VENV   := .venv
BIN    := $(VENV)/bin

.DEFAULT_GOAL := help
.PHONY: help venv install serve build validate strict check guard public publish-runs export-run-media \
        compress-run-media upload-run-media publish links demos edit \
        runs runs-watch sync \
        sync-behavior sync-robowits sync-robolab sync-robotwin sync-robopaint sync-humanoidbench sync-kinder sync-dextoolbench sync-mujoco-playground \
        sync-metaworldplus sync-vlabench sync-robocasa sync-robocasa365 sync-robocasa-gr1 sync-verified sync-dry clean

help: ## Show this help
	@grep -hE '^[a-z-]+:.*?## ' $(MAKEFILE_LIST) \
		| awk -F':.*?## ' '{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

venv: ## Create the virtualenv
	$(PYTHON) -m venv $(VENV)

install: venv ## Install the documentation toolchain
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

# Port is discovered rather than fixed, so a stale preview or a colleague on
# the same box does not make `make serve` fail. Override with `make serve PORT=9000`.
serve: ## Preview, READ-ONLY (use `make edit` if you want to change anything)
	@port="$(PORT)"; \
	[ -n "$$port" ] || port=$$($(BIN)/python scripts/free_port.py) || exit 1; \
	echo ""; \
	echo "  OPEN THIS  ->  http://127.0.0.1:$$port"; \
	echo "  READ-ONLY: Edit buttons will not save. Use 'make edit' to change anything."; \
	echo ""; \
	SITE_URL="http://127.0.0.1:$$port/" \
		$(BIN)/mkdocs serve --dev-addr "127.0.0.1:$$port"

build: ## Build the site into ./site (fails on broken links)
	$(BIN)/mkdocs build --clean --strict

validate: ## Check every task page against the schema and registries
	$(BIN)/python scripts/validate.py

strict: ## Validate, treating warnings (incomplete pages) as failures
	$(BIN)/python scripts/validate.py --strict

demos: ## Download the oracle demo videos for every benchmark (~1.2 GB, once)
	$(BIN)/python scripts/fetch_demos.py --benchmark behavior-1k
	$(BIN)/python scripts/fetch_demos.py --benchmark robowits
	$(BIN)/python scripts/fetch_demos.py --benchmark robolab

# Preview plus the local edit daemon, so status and labels can be changed from
# the task list instead of by hand-editing YAML. Localhost only, single user.
# Both servers run under scripts/pdeath.py, which has the kernel kill them the
# moment this shell dies — a trap cannot cover `kill -9` or a closed terminal,
# and that is how every orphan got left behind. The daemon is also started
# directly rather than inside `{ ...; } &`, because the old trap killed the
# subshell job and left the python process it had spawned running.
#
# `mkdocs serve` prints its own address, and it prints it after ours, so it reads
# like the authoritative one. It is the INTERNAL port: /api/* is not there, and a
# browser that lands on it silently gets a read-only site. Rewrite the inner
# address to the front one in everything mkdocs prints, so the only URL anyone
# can ever see is the one that works.
edit: ## Preview WITH editing — the only way to change labels or status
	@front="$(PORT)"; \
	[ -n "$$front" ] || front=$$($(BIN)/python scripts/free_port.py) || exit 1; \
	inner=$$($(BIN)/python scripts/free_port.py --start $$((front + 1))) || exit 1; \
	echo ""; \
	echo "  OPEN THIS  ->  http://127.0.0.1:$$front"; \
	echo "  Editing is ON: Edit buttons and the Label taxonomy page write to state/."; \
	echo ""; \
	$(BIN)/python scripts/pdeath.py $(BIN)/python scripts/editd.py \
		--port "$$front" --upstream "127.0.0.1:$$inner" \
		--docs-url "http://127.0.0.1:$$front" & \
	api=$$!; \
	trap 'kill $$api 2>/dev/null' EXIT INT TERM; \
	SITE_URL="http://127.0.0.1:$$front/" RB_FRONT_URL="http://127.0.0.1:$$front/" \
		$(BIN)/python scripts/pdeath.py $(BIN)/mkdocs serve --dev-addr "127.0.0.1:$$inner" 2>&1 \
		| sed -u "s|http://127\.0\.0\.1:$$inner|http://127.0.0.1:$$front|g"

# The agent runs (state/runs/<benchmark>.yml, data/agents/<run>.yml): what every task's trials are doing, read
# from the machines in data/runs/hosts*.local.yml (local only) into data/runs/<benchmark>/<run>.json. A running
# `make serve` / `make edit` rebuilds when the data changes. RUNS passes options, e.g. RUNS="--benchmark robolab".
RUNS ?=

runs: ## Collect every registered run once (data/runs/<benchmark>/<run>.json), log pages included
	$(BIN)/python scripts/import_runs.py $(RUNS)

runs-watch: ## Keep collecting them every 3 minutes
	$(BIN)/python scripts/import_runs.py --watch 180 $(RUNS)

links: ## Verify every internal link in site/ resolves (catches raw-HTML hrefs)
	$(BIN)/python scripts/check_links.py

check: validate guard build links ## What CI runs

guard: ## Fail if the repository tracks run media or local run data (they go to Hugging Face / stay local)
	$(BIN)/python scripts/check_no_run_media.py

# The public site (scripts/sitemode.py; its settings: data/public.yml): read-only, and only what is committed. Its
# agent runs are the published snapshot (make publish-runs), their media hosted apart (make export-run-media). This is
# what .github/workflows/deploy.yml publishes. It fails above 1 GB, GitHub Pages' limit.
PAGES_LIMIT_BYTES := 1000000000

public: ## Build the public site into ./site as deployed (read-only), check its links and its size
	RB_PUBLIC=1 $(BIN)/mkdocs build --clean --strict
	$(BIN)/python scripts/check_links.py
	@size=$$(du -sb site | cut -f1); echo "site/ is $$((size / 1048576)) MiB (GitHub Pages publishes at most 1 GB)"; \
	if [ "$$size" -gt $(PAGES_LIMIT_BYTES) ]; then echo "site/ is too big for GitHub Pages: see data/public.yml"; exit 1; fi

publish-runs: ## Snapshot the runs for the public site (data/published_runs/: filtered, secret-scanned; BENCHMARK=<id>: only its part)
	$(BIN)/python scripts/publish_runs.py $(foreach b,$(BENCHMARK),--benchmark $(b))

# OUT: where the export goes (default .cache/run-media-export/, gitignored); nothing is uploaded.
OUT ?=

export-run-media: ## Export the published runs' replays and images, with a manifest, for an outside host (OUT=dir)
	$(BIN)/python scripts/export_run_media.py $(if $(OUT),--out $(OUT),)

# The run media on Hugging Face (the public site loads them from data/public.yml's run_media_base). Each contributor
# uploads with their own `hf auth login` (a member of the organisation), and only their benchmark's folder:
#   make upload-run-media BENCHMARK=<id>        (all benchmarks when BENCHMARK is empty)
HF             ?= hf
RUN_MEDIA_REPO ?= eai-v2-internal/agent-runs
BENCHMARK      ?=

compress-run-media: ## Compress the exported run media for Hugging Face (H.264 CRF 28, PNG -> WebP): .cache/run-media-hf/
	$(BIN)/python scripts/compress_run_media.py $(foreach b,$(BENCHMARK),--benchmark $(b))

# Everything above in one unattended, gated run: import, snapshot (finished trials; scanned), media, make check +
# make public, then a commit of data/published_runs/ pushed as a fast-forward. Idempotent; logs to .cache/publish.log.
publish: ## Publish the finished runs on the public site (import, snapshot, media, gates, commit, push)
	HF=$(HF) RUN_MEDIA_REPO=$(RUN_MEDIA_REPO) $(BIN)/python scripts/publish_site.py

upload-run-media: export-run-media compress-run-media ## Export, compress and upload run media (BENCHMARK=<id>; your own hf login)
	cp data/run-media-card.md .cache/run-media-hf/README.md
	$(HF) upload-large-folder $(RUN_MEDIA_REPO) .cache/run-media-hf --repo-type dataset \
	    $(if $(BENCHMARK),--include $(foreach b,$(BENCHMARK),"$(b)/**") README.md,--include "*/**" README.md manifest.json)

# Each benchmark syncs from its own upstream. BEHAVIOR reads a public gallery;
# RoboWits and RoboLab read a source checkout (pass it in), because their tasks
# are defined in code. All three are idempotent and write only `upstream:`.
sync: sync-behavior sync-robowits sync-robolab sync-robotwin sync-robopaint sync-humanoidbench sync-kinder sync-dextoolbench sync-mujoco-playground \
      sync-metaworldplus sync-vlabench sync-robocasa sync-robocasa365 sync-robocasa-gr1 ## Re-sync every benchmark from its upstream

sync-behavior: ## Re-sync BEHAVIOR-1K task pages from the official gallery
	$(BIN)/python scripts/import_behavior_tasks.py

# SRC defaults to a sibling checkout; override with `make sync-robowits SRC=~/src/RoboWits`.
ROBOWITS_SRC ?= ../RoboWits
ROBOLAB_SRC  ?= ../RoboLab

sync-robowits: ## Re-sync RoboWits from a source checkout (ROBOWITS_SRC=...)
	$(BIN)/python scripts/import_robowits_tasks.py $(if $(wildcard $(ROBOWITS_SRC)),--source $(ROBOWITS_SRC),)

sync-robolab: ## Re-sync RoboLab from a source checkout (ROBOLAB_SRC=...)
	$(BIN)/python scripts/import_robolab_tasks.py $(if $(wildcard $(ROBOLAB_SRC)),--source $(ROBOLAB_SRC),)

# RoboTwin 2.0 is read from the submodule our image pins (a robot_coding_bench checkout has it), its
# documentation site, and our own render of the suite (scene stills + expert clips), if present.
ROBOTWIN_SRC   ?= ../robot_coding_bench/third_party/RoboTwin
ROBOTWIN_MEDIA ?= ../robotwin2_tasks
ROBOTWIN_SWEEP ?= ../robot_coding_bench/exps/robotwin_expert_sweep_2026-09-21.json

sync-robotwin: ## Re-sync RoboTwin 2.0 from the pinned checkout + docs site (ROBOTWIN_SRC=..., ROBOTWIN_MEDIA=...)
	$(BIN)/python scripts/import_robotwin_tasks.py $(if $(wildcard $(ROBOTWIN_SRC)),--source $(ROBOTWIN_SRC) --fetch-docs,) \
	    $(if $(wildcard $(ROBOTWIN_MEDIA)),--media $(ROBOTWIN_MEDIA),) $(if $(wildcard $(ROBOTWIN_SWEEP)),--sweep $(ROBOTWIN_SWEEP),)

# DexToolBench and MuJoCo Playground run in our MuJoCo port (robot_coding_bench tasks/dextoolbench_*, mujoco_playground_*).
# DTB_SRC: a SimToolReal checkout, or the image's asset dir (images/mujoco/rcb_mj/simtoolreal after prepare_assets.sh);
# PLAYGROUND_SRC: a mujoco_playground checkout @ 4057c14. MJ_ORACLE_JOBS: the oracle's Harbor job, whose replays are the demos.
# Without the sources, both re-render from their caches.
DTB_SRC        ?= ../robot_coding_bench/images/mujoco/rcb_mj/simtoolreal
PLAYGROUND_SRC ?= ../mujoco_playground
MJ_HARNESS     ?= ../robot_coding_bench
MJ_ORACLE_JOBS ?= ../robot_coding_bench/exps/jobs/mj-oracle-all

sync-dextoolbench: ## Re-sync DexToolBench from SimToolReal's trajectories + our oracle replays (DTB_SRC=..., MJ_ORACLE_JOBS=...)
	$(BIN)/python scripts/import_dextoolbench_tasks.py $(if $(wildcard $(DTB_SRC)),--source $(DTB_SRC),) \
	    $(if $(wildcard $(MJ_HARNESS)),--harness $(MJ_HARNESS),) $(if $(wildcard $(MJ_ORACLE_JOBS)),--oracle-jobs $(MJ_ORACLE_JOBS),)

sync-mujoco-playground: ## Re-sync MuJoCo Playground's manipulation envs (PLAYGROUND_SRC=..., MJ_ORACLE_JOBS=...)
	$(BIN)/python scripts/import_mujoco_playground_tasks.py $(if $(wildcard $(PLAYGROUND_SRC)),--source $(PLAYGROUND_SRC),) \
	    $(if $(wildcard $(MJ_HARNESS)),--harness $(MJ_HARNESS),) $(if $(wildcard $(MJ_ORACLE_JOBS)),--oracle-jobs $(MJ_ORACLE_JOBS),)

# RoboPaint is ours, defined in robot_coding_bench (tasks/robopaint-<family>-<target>-i00): read from a commit of the
# clone with `git archive` (fetch it first: git -C ../robot_coding_bench fetch origin dev/qineng), never a checkout.
# ROBOPAINT_DEMOS: the oracle's validation jobs whose replays are the demos (host:dir, read only; the last one wins).
# Empty by default (no demos fetched); set it per machine in Makefile.local, which is gitignored.
ROBOPAINT_SRC    ?= ../robot_coding_bench
ROBOPAINT_COMMIT ?= origin/dev/qineng
ROBOPAINT_DEMOS  ?=

sync-robopaint: ## Re-sync RoboPaint from a robot_coding_bench commit (ROBOPAINT_COMMIT=..., ROBOPAINT_DEMOS="host:dir ...")
	$(BIN)/python scripts/import_robopaint_tasks.py --source $(ROBOPAINT_SRC) --commit $(ROBOPAINT_COMMIT) \
	    $(foreach d,$(ROBOPAINT_DEMOS),--demos $(d))

# HumanoidBench: our selection of it is defined in robot_coding_bench (scripts/humanoidbench/subset.toml, facts.json,
# tasks/humanoidbench-<category>-<task>-i00): read from a commit of the clone with `git archive`, never a checkout.
# HUMANOIDBENCH_SCENES: the t = 0 room-camera stills (gen_tasks.py measure-limited --images DIR), if present.
HUMANOIDBENCH_SRC    ?= ../robot_coding_bench
HUMANOIDBENCH_COMMIT ?= origin/dev/pingyue
HUMANOIDBENCH_SCENES ?= ../robot_coding_bench/jobs/results/humanoidbench/assets/cameras

sync-humanoidbench: ## Re-sync HumanoidBench from a robot_coding_bench commit (HUMANOIDBENCH_COMMIT=..., HUMANOIDBENCH_SCENES=...)
	$(BIN)/python scripts/import_humanoidbench_tasks.py --source $(HUMANOIDBENCH_SRC) --commit $(HUMANOIDBENCH_COMMIT) \
	    $(if $(wildcard $(HUMANOIDBENCH_SCENES)),--scenes $(HUMANOIDBENCH_SCENES),)

# KinDER: our selection of it is defined in robot_coding_bench (scripts/kinder/subset.toml, facts.json,
# tasks/kinder-<family>-i00): read from a commit of the clone with `git archive`, never a checkout.
# KINDER_SCENES: the t = 0 room-camera stills (the results site's assets/cameras/<family>/room_camera.png), if present.
KINDER_SRC    ?= ../robot_coding_bench
KINDER_COMMIT ?= origin/dev/pingyue
KINDER_SCENES ?= ../robot_coding_bench/jobs/results/kinder/assets/cameras

sync-kinder: ## Re-sync KinDER from a robot_coding_bench commit (KINDER_COMMIT=..., KINDER_SCENES=...)
	$(BIN)/python scripts/import_kinder_tasks.py --source $(KINDER_SRC) --commit $(KINDER_COMMIT) \
	    $(if $(wildcard $(KINDER_SCENES)),--scenes $(KINDER_SCENES),)

# MetaWorld+, VLABench, RoboCasa, RoboCasa365 and RoboCasa-GR1 are defined in robot_coding_bench (tasks/<prefix>-<task>-i00-
# privileged / -standard, written by scripts/<benchmark>/generate.py): read from a commit of the clone with `git archive`,
# never a checkout (scripts/rcb_selection.py). RCB_ORACLE_JOBS: dirs of the oracle's Harbor trials whose verifier replays
# are the demos (read only; searched recursively). Empty by default; set it per machine in Makefile.local.
RCB_SRC         ?= ../robot_coding_bench
RCB_COMMIT      ?= origin/main
RCB_ORACLE_JOBS ?=
RCB_SYNC         = --source $(RCB_SRC) --commit $(RCB_COMMIT) $(foreach d,$(RCB_ORACLE_JOBS),--demos $(d))

sync-metaworldplus: ## Re-sync MetaWorld+ from a robot_coding_bench commit (RCB_COMMIT=..., RCB_ORACLE_JOBS="dir ...")
	$(BIN)/python scripts/import_metaworldplus_tasks.py $(RCB_SYNC)

sync-vlabench: ## Re-sync VLABench (our selection) from a robot_coding_bench commit
	$(BIN)/python scripts/import_vlabench_tasks.py $(RCB_SYNC)

sync-robocasa: ## Re-sync RoboCasa (our selection) from a robot_coding_bench commit
	$(BIN)/python scripts/import_robocasa_tasks.py $(RCB_SYNC)

sync-robocasa365: ## Re-sync RoboCasa365 (our selection) from a robot_coding_bench commit
	$(BIN)/python scripts/import_robocasa365_tasks.py $(RCB_SYNC)

sync-robocasa-gr1: ## Re-sync RoboCasa-GR1 from a robot_coding_bench commit
	$(BIN)/python scripts/import_robocasa_gr1_tasks.py $(RCB_SYNC)

# The BDDL goals and dataset statistics come from the licensed BEHAVIOR download,
# so the extract step runs inside the simulator image; see the script's docstring.
sync-verified: ## Rewrite the `verified:` blocks from the cached extract
	$(BIN)/python scripts/import_behavior_verified.py

sync-dry: ## Preview an upstream re-sync without writing anything
	$(BIN)/python scripts/import_behavior_tasks.py --dry-run

clean: ## Remove build output
	rm -rf site
