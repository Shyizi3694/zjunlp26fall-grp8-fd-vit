# Invalid Optional 5k Artifacts

These files are quarantined and must not be used as report evidence or included in the official E00-E03 result summaries.

Reason:

- The optional 5k configs were named as 5k experiments but still pointed to 2k experiment ids, 2k training files, and 2k checkpoint directories.
- The optional 5k output metrics also recorded 2k experiment ids/checkpoints, so they are not reliable evidence for a 5k ablation.
- The clean mainline package uses only E00-E03 under `outputs/` and excludes this directory from `results_main.csv`, `error_comparison.csv`, case studies, and dashboard generation.

Repair date: 2026-06-16.
