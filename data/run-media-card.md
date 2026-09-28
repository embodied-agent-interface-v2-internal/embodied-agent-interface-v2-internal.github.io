---
license: other
license_name: per-benchmark
license_link: https://embodied-agent-interface-v2-internal.github.io/
pretty_name: Agent runs, replays and images
tags:
- robotics
- agents
- simulation
- video
viewer: false
---

# Agent runs: replays and images

The replay videos and images of the agent runs shown on
<https://embodied-agent-interface-v2-internal.github.io/> (the "Agent runs" section). For every trial:

- `replay.mp4`: the separate verifier's replay of the trajectory the agent handed in. It is H.264 with the index
  first, so it plays and seeks in a browser before the whole file arrives. `replay.webp` is its last frame.
- `img/`: the images the model was shown during the run.
- `snap/`: only where the agent handed in no trajectory, the newest images it saved.

The site's log pages load these files from here, and each page carries the text of its trial: the model's words, its
tool calls and their output, and the token counts.

## Layout

```
<benchmark>/<run>/<task>/<slot>/replay.mp4
                               /replay.webp
                               /img/<n>.webp | <n>.jpg
                               /snap/<n>.webp | <n>.jpg
manifest.json                  every file, its size, and the size of the original it was compressed from
```

- **benchmark**: the site's benchmark id (`behavior-1k`, `robolab`, `robowits`, `robopaint`, …).
- **run**: the agent configuration (harness + model + settings), e.g. `codex-0.157-gpt6luna-xhigh-cgpt`.
- **slot**: the mode (`unlimited`, `limited`), or `<mode>-prev` for a run that a rerun replaced.

## Adding your benchmark

Each benchmark owns its own folder. You add yours with your own account in this organisation:

1. **Register and collect your runs** in the site's repository:
   - `state/runs/<benchmark>.yml` and `data/agents/<run>.yml`;
   - `make runs`.
2. **Publish the text snapshot** with `make publish-runs`, and open a pull request with `data/published_runs/`.
3. **Upload your media:**
   - log in with `hf auth login` (your own account);
   - run `make upload-run-media BENCHMARK=<benchmark>`. It exports your benchmark's media, compresses it and uploads
     it to `<benchmark>/` here, touching no other folder.
4. **Merge.** Once the pull request is merged, the site's log pages load your media from
   `https://huggingface.co/datasets/eai-v2-internal/agent-runs/resolve/main/`.

## Licence

These files are renders from each benchmark's simulator and assets (BEHAVIOR-1K, RoboLab, RoboWits, RoboPaint, …). They
stay under the terms of the benchmark they come from and of the assets shown in them. We grant no licence beyond those
terms. Please ask before reusing them outside research.
