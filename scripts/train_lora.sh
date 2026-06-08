#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/train_lora.sh <config_path> [--dry_run] [--qlora]

Options:
  --dry_run   Validate config and print the resolved launch plan without running training.
  --qlora     Force-enable the qlora.enabled/load_in_4bit flags in the resolved config.
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

CONFIG_PATH=""
DRY_RUN=0
FORCE_QLORA=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry_run)
      DRY_RUN=1
      shift
      ;;
    --qlora)
      FORCE_QLORA=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [[ -z "${CONFIG_PATH}" ]]; then
        CONFIG_PATH="$1"
        shift
      else
        echo "ERROR: unknown extra argument: $1" >&2
        usage
        exit 1
      fi
      ;;
  esac
done

if [[ -z "${CONFIG_PATH}" ]]; then
  echo "ERROR: config path is required" >&2
  usage
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ABS_CONFIG_PATH="$(cd "${ROOT_DIR}" && python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "${CONFIG_PATH}")"

if [[ ! -f "${ABS_CONFIG_PATH}" ]]; then
  echo "ERROR: config not found: ${CONFIG_PATH}" >&2
  exit 1
fi

PARSED_JSON="$(
python3 - <<'PY' "${ROOT_DIR}" "${ABS_CONFIG_PATH}" "${FORCE_QLORA}"
import json
import os
import sys
from pathlib import Path

root = Path(sys.argv[1])
config_path = Path(sys.argv[2])
force_qlora = bool(int(sys.argv[3]))

try:
    import yaml
except Exception as exc:
    raise SystemExit(f"PyYAML import failed: {exc}")

payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
if not isinstance(payload, dict):
    raise SystemExit("config must be a mapping")

required_sections = ("model", "data", "training", "lora", "qlora", "runtime")
for section in required_sections:
    if not isinstance(payload.get(section), dict):
        raise SystemExit(f"missing or invalid section: {section}")

experiment_id = str(payload.get("experiment_id", "") or "").strip()
if not experiment_id:
    raise SystemExit("experiment_id is required")

seed = int(payload.get("seed", 42))
train_file = str(payload["data"].get("train_file", "") or "").strip()
output_dir = str(payload["training"].get("output_dir", "") or "").strip()
if not train_file:
    raise SystemExit("data.train_file is required")
if not output_dir:
    raise SystemExit("training.output_dir is required")

train_file_path = (root / train_file).resolve()
output_dir_path = (root / output_dir).resolve()
model_local_dir = str(payload["model"].get("local_dir", "") or "").strip()
model_local_path = (root / model_local_dir).resolve() if model_local_dir else None

payload["qlora"]["enabled"] = bool(payload["qlora"].get("enabled", False) or force_qlora)
payload["qlora"]["load_in_4bit"] = bool(payload["qlora"].get("load_in_4bit", False) or force_qlora)

python_executable = str(payload["runtime"].get("python_executable", "python3") or "python3").strip()
trainer_command = str(payload["runtime"].get("trainer_command", "") or "").strip()

result = {
    "root_dir": str(root),
    "config_path": str(config_path),
    "experiment_id": experiment_id,
    "seed": seed,
    "train_file": train_file,
    "train_file_exists": train_file_path.exists(),
    "train_file_abs": str(train_file_path),
    "output_dir": output_dir,
    "output_dir_abs": str(output_dir_path),
    "model_local_dir": model_local_dir,
    "model_local_exists": model_local_path.exists() if model_local_path is not None else False,
    "python_executable": python_executable,
    "trainer_command": trainer_command,
    "resolved_config_yaml": yaml.safe_dump(payload, sort_keys=False, allow_unicode=True),
    "qlora_enabled": bool(payload["qlora"]["enabled"]),
}
print(json.dumps(result, ensure_ascii=False))
PY
)"

TRAIN_FILE="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["train_file"])' "${PARSED_JSON}")"
TRAIN_FILE_EXISTS="$(python3 -c 'import json,sys; print("1" if json.loads(sys.argv[1])["train_file_exists"] else "0")' "${PARSED_JSON}")"
OUTPUT_DIR_REL="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["output_dir"])' "${PARSED_JSON}")"
OUTPUT_DIR_ABS="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["output_dir_abs"])' "${PARSED_JSON}")"
EXPERIMENT_ID="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["experiment_id"])' "${PARSED_JSON}")"
PYTHON_BIN="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["python_executable"])' "${PARSED_JSON}")"
TRAINER_COMMAND="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["trainer_command"])' "${PARSED_JSON}")"
QLORA_ENABLED="$(python3 -c 'import json,sys; print("true" if json.loads(sys.argv[1])["qlora_enabled"] else "false")' "${PARSED_JSON}")"

if [[ -z "${TRAINER_COMMAND}" && -n "${FDVIT_TRAIN_ENTRYPOINT:-}" ]]; then
  TRAINER_COMMAND="${FDVIT_TRAIN_ENTRYPOINT}"
fi

if [[ "${TRAIN_FILE_EXISTS}" != "1" && "${DRY_RUN}" != "1" ]]; then
  echo "ERROR: train file not found: ${TRAIN_FILE}" >&2
  exit 1
fi

mkdir -p "${OUTPUT_DIR_ABS}"

python3 - <<'PY' "${PARSED_JSON}" "${OUTPUT_DIR_ABS}" "${ROOT_DIR}" "${CONFIG_PATH}" "${DRY_RUN}" "${FORCE_QLORA}"
import importlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

payload = json.loads(sys.argv[1])
output_dir = Path(sys.argv[2])
root_dir = Path(sys.argv[3])
config_path = sys.argv[4]
dry_run = bool(int(sys.argv[5]))
force_qlora = bool(int(sys.argv[6]))

output_dir.mkdir(parents=True, exist_ok=True)
(output_dir / "train_config.yaml").write_text(payload["resolved_config_yaml"], encoding="utf-8")

command_line = f"bash scripts/train_lora.sh {config_path}"
if dry_run:
    command_line += " --dry_run"
if force_qlora:
    command_line += " --qlora"
(output_dir / "command.txt").write_text(command_line + "\n", encoding="utf-8")

def module_version(name: str) -> str | None:
    try:
        module = importlib.import_module(name)
    except Exception:
        return None
    return getattr(module, "__version__", None)

env_payload = {
    "python": sys.version,
    "platform": platform.platform(),
    "cwd": os.getcwd(),
    "experiment_id": payload["experiment_id"],
    "config_path": config_path,
    "train_file": payload["train_file"],
    "output_dir": payload["output_dir"],
    "model_local_dir": payload["model_local_dir"],
    "trainer_command": payload["trainer_command"],
    "qlora_enabled": payload["qlora_enabled"],
    "versions": {
        "torch": module_version("torch"),
        "transformers": module_version("transformers"),
        "peft": module_version("peft"),
        "trl": module_version("trl"),
        "bitsandbytes": module_version("bitsandbytes"),
        "yaml": module_version("yaml"),
    },
}
try:
    import torch

    env_payload["cuda"] = {
        "available": bool(torch.cuda.is_available()),
        "device_count": int(torch.cuda.device_count()) if torch.cuda.is_available() else 0,
        "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }
except Exception as exc:
    env_payload["cuda"] = {"available": None, "error": str(exc)}

(output_dir / "environment.txt").write_text(json.dumps(env_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY

echo "Resolved LoRA training plan"
echo "  experiment_id: ${EXPERIMENT_ID}"
echo "  config: ${CONFIG_PATH}"
echo "  train_file: ${TRAIN_FILE}"
echo "  output_dir: ${OUTPUT_DIR_REL}"
echo "  qlora_enabled: ${QLORA_ENABLED}"
if [[ "${TRAIN_FILE_EXISTS}" != "1" ]]; then
  echo "  train_file_exists: false"
else
  echo "  train_file_exists: true"
fi
if [[ -n "${TRAINER_COMMAND}" ]]; then
  echo "  trainer_command: ${TRAINER_COMMAND}"
else
  echo "  trainer_command: <not configured>"
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  echo
  echo "Dry run only. Metadata written to ${OUTPUT_DIR_REL}:"
  echo "  train_config.yaml"
  echo "  command.txt"
  echo "  environment.txt"
  if [[ -n "${TRAINER_COMMAND}" ]]; then
    echo
    echo "Would execute:"
    echo "  ${TRAINER_COMMAND} --config ${OUTPUT_DIR_REL}/train_config.yaml"
  else
    echo
    echo "No trainer command configured yet."
    echo "Set runtime.trainer_command in the YAML or export FDVIT_TRAIN_ENTRYPOINT before real training."
  fi
  exit 0
fi

if [[ -z "${TRAINER_COMMAND}" ]]; then
  echo "ERROR: training launcher is scaffolded, but no concrete trainer_command is configured." >&2
  echo "A resolved train_config.yaml has been written to ${OUTPUT_DIR_REL}." >&2
  echo "Configure runtime.trainer_command in the YAML, then rerun this script." >&2
  exit 1
fi

TRAIN_LOG="${OUTPUT_DIR_ABS}/train.log"
echo "Launching trainer..."
echo "  ${TRAINER_COMMAND} --config ${OUTPUT_DIR_REL}/train_config.yaml"

set +e
(
  cd "${ROOT_DIR}"
  eval "${TRAINER_COMMAND} --config \"${OUTPUT_DIR_REL}/train_config.yaml\""
) 2>&1 | tee "${TRAIN_LOG}"
EXIT_CODE=${PIPESTATUS[0]}
set -e

if [[ ${EXIT_CODE} -ne 0 ]]; then
  echo "ERROR: training failed with exit code ${EXIT_CODE}. See ${OUTPUT_DIR_REL}/train.log" >&2
  exit ${EXIT_CODE}
fi

echo "Training completed successfully. Logs saved to ${OUTPUT_DIR_REL}/train.log"
