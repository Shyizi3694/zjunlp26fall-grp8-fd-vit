# FD-VIT Output Template

Use this structure when finishing a coding-agent task:

```text
Implemented <short task name>.

Changed:
- <file or subsystem>: <what changed>

Validation:
- <command>: <pass/fail/not run>

Generated:
- <artifact paths, if any>

Notes:
- <risks, missing data/model/hardware, or follow-up>
```

If no validation was run, state the concrete blocker. If a command failed, include the relevant error and the next practical step.
