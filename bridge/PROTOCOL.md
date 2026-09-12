# XH Global Control process bridge protocol 1.1

`wrapper.py` is owned by `xh-tuvan`. It accepts one Global Control
`TaskEnvelope` JSON document on stdin and emits one `PluginResult` JSON document
on stdout. Diagnostics go to stderr. Protocol 1.0 contexts remain valid for
ordinary execute calls.

Global supplies `--context <path>` with a task-scoped protocol document. The
context binds task, attempt, generation, worker, channel, permission and budget,
and provides a one-shot `channel_bridge` command. The wrapper calls that
command exactly once with a generic `ChannelRequest` JSON document.

Global owns channel selection, worker selection, permissions, budget, retry,
process cancellation, artifact verification and operational persistence. The
plugin owns domain state and its handoff artifacts. No credential, provider
selection or domain knowledge is stored in the wrapper transport.

`task_type: "generic"` is accepted as the default transport-level task type.
The concrete xh-tuvan capability remains in `execution.master_capability` and
the domain objective remains in `user_request`; unsupported task types are
still rejected.

Healthcheck:

```powershell
python bridge/wrapper.py --healthcheck
```

Expected stdout:

```json
{"protocol_version": "1.1", "healthy": true}
```

## Safe pause

Global creates `pause.request.json` beside the context. It contains the bound
`task_id` and normally `action: "pause"`. The channel bridge must reach a safe
plugin-owned boundary and return a real handoff artifact URI. The wrapper
validates the URI form `xh-tuvan://handoff/<task_id>/<name>.json`, verifies that
the artifact is under the task's `30_Working/.xh/handoffs/` directory, and
checks the artifact's protocol and task identity.

On success the wrapper emits only:

```json
{"protocol_version":"1.1","task_id":"T-...","handoff_uri":"xh-tuvan://handoff/T-.../name.json"}
```

It never emits handoff content or creates a URI for a missing/invalid artifact.
If the channel does not return a valid handoff, pause fails and must not be
treated as successful. The process exits cleanly after a successful response.

## Resume

Global supplies `resume_handoff_uri` in the task-scoped context. The wrapper
accepts only a plugin-owned URI with matching task identity, validates its
artifact, and passes the opaque URI to the channel bridge. It does not replay
chat history or choose provider, worker, budget, permission, retry, or
generation. After the channel returns, the handoff is atomically marked
consumed; replaying the same URI is rejected.
