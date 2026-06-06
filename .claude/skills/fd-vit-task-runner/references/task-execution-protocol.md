# FD-VIT Task Execution Protocol

## Before Coding

State or determine:

- Phase and Task card number.
- Input files and directories.
- Output files and directories.
- Docs read for this task.
- Whether the change touches data schemas, prediction schemas, metrics, experiment IDs, or report claims.
- Whether the change can contaminate train/val/test separation.
- Self-test command from the task card or nearest affected script.

If the task would change a schema, update `docs/DATA_AND_FORMAT_CONTRACT.md` and the validator in the same change.

If the task would change experiment IDs, metrics, fixed variables, split policy, or output directory policy, update `docs/EXPERIMENT_PROTOCOL.md` in the same change.

## During Coding

- Keep scripts CLI-driven with explicit input path, output path, limit, seed, and overwrite/dry-run controls when applicable.
- Use relative paths from repo root; never hardcode private absolute paths.
- Preserve per-sample JSONL outputs for inference and errors.
- Keep E00-E03 comparable: same model family, eval set, evaluation script, generation config, and seed unless documented.
- Add focused smoke tests or toy fixtures when full data/model execution is unavailable.

## Before Finishing

Run the task self-test when possible. If not possible, explain the missing dependency, data, model, or hardware.

For data/inference/evaluation tasks, verify row counts and JSON/JSONL parseability. For experiment scripts, verify output paths and metadata logging.

## Final Response

Use `references/output-template.md`. Include enough command output detail for the user to understand the result; do not paste long logs.
