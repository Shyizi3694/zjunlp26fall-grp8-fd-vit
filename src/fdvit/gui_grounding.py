"""Utilities for optional GUI grounding evaluation."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from typing import Any


NUMBER_RE = re.compile(r"[-+]?(?:\d+\.\d+|\d+)")


@dataclass(frozen=True)
class ParsedPoint:
    point: list[float] | None
    mode: str
    source: str
    error: str | None = None


def bbox_center(bbox: list[float]) -> list[float]:
    return [(bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0]


def is_point_in_bbox(point: list[float] | None, bbox: list[float]) -> bool:
    if point is None:
        return False
    x, y = point
    x1, y1, x2, y2 = bbox
    return x1 <= x <= x2 and y1 <= y <= y2


def center_distance_norm(point: list[float] | None, bbox: list[float], image_size: list[int | float]) -> float | None:
    if point is None:
        return None
    center = bbox_center(bbox)
    width, height = float(image_size[0]), float(image_size[1])
    diagonal = math.hypot(width, height)
    if diagonal <= 0:
        return None
    return math.hypot(float(point[0]) - center[0], float(point[1]) - center[1]) / diagonal


def coerce_bbox(value: Any) -> list[float] | None:
    if not isinstance(value, list) or len(value) != 4:
        return None
    try:
        bbox = [float(x) for x in value]
    except (TypeError, ValueError):
        return None
    if bbox[2] < bbox[0] or bbox[3] < bbox[1]:
        return None
    return bbox


def coerce_image_size(value: Any) -> list[int] | None:
    if not isinstance(value, list) or len(value) != 2:
        return None
    try:
        width = int(value[0])
        height = int(value[1])
    except (TypeError, ValueError):
        return None
    if width <= 0 or height <= 0:
        return None
    return [width, height]


def _json_candidates(text: str) -> list[Any]:
    candidates: list[Any] = []
    stripped = text.strip()
    snippets = [stripped]
    if "```" in stripped:
        snippets.extend(part.strip() for part in stripped.split("```") if part.strip())

    for snippet in snippets:
        start = min([idx for idx in (snippet.find("{"), snippet.find("[")) if idx >= 0], default=-1)
        end = max(snippet.rfind("}"), snippet.rfind("]"))
        if start >= 0 and end > start:
            snippet = snippet[start : end + 1]
        try:
            candidates.append(json.loads(snippet))
        except Exception:
            continue
    return candidates


def _extract_point_from_json(obj: Any) -> tuple[list[float] | None, str | None]:
    if isinstance(obj, list):
        if len(obj) >= 2 and all(isinstance(item, (int, float)) for item in obj[:2]):
            return [float(obj[0]), float(obj[1])], "json_list"
        return None, None
    if not isinstance(obj, dict):
        return None, None

    for key in ("point", "prediction_point", "click_point", "coordinate", "coordinates"):
        value = obj.get(key)
        if isinstance(value, list) and len(value) >= 2:
            try:
                return [float(value[0]), float(value[1])], f"json_{key}"
            except (TypeError, ValueError):
                pass

    for key in ("bbox", "box", "bbox_2d"):
        bbox = coerce_bbox(obj.get(key))
        if bbox is not None:
            return bbox_center(bbox), f"json_{key}_center"

    if "x" in obj and "y" in obj:
        try:
            return [float(obj["x"]), float(obj["y"])], "json_xy"
        except (TypeError, ValueError):
            pass
    return None, None


def _numbers_from_text(text: str) -> list[float]:
    values = []
    for match in NUMBER_RE.finditer(text):
        try:
            values.append(float(match.group(0)))
        except ValueError:
            continue
    return values


def _convert_coordinate_mode(point: list[float], image_size: list[int], mode: str, raw_text: str) -> tuple[list[float], str]:
    width, height = float(image_size[0]), float(image_size[1])
    x, y = float(point[0]), float(point[1])
    chosen = mode
    if mode == "auto":
        lowered = raw_text.lower()
        if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
            chosen = "normalized"
        elif ("1000" in lowered or "0-1000" in lowered or "0 to 1000" in lowered) and 0.0 <= x <= 1000.0 and 0.0 <= y <= 1000.0:
            chosen = "qwen_1000"
        else:
            chosen = "pixel"

    if chosen == "normalized":
        return [x * width, y * height], chosen
    if chosen == "qwen_1000":
        return [x / 1000.0 * width, y / 1000.0 * height], chosen
    return [x, y], "pixel"


def parse_gui_point(raw_text: str | None, image_size: list[int] | None, *, coordinate_mode: str = "auto") -> ParsedPoint:
    if raw_text is None or not str(raw_text).strip():
        return ParsedPoint(point=None, mode=coordinate_mode, source="empty", error="empty prediction")
    if image_size is None:
        return ParsedPoint(point=None, mode=coordinate_mode, source="invalid_image_size", error="invalid image_size")

    text = str(raw_text)
    for obj in _json_candidates(text):
        point, source = _extract_point_from_json(obj)
        if point is not None and source is not None:
            converted, mode = _convert_coordinate_mode(point, image_size, coordinate_mode, text)
            return ParsedPoint(point=converted, mode=mode, source=source)

    numbers = _numbers_from_text(text)
    if len(numbers) >= 4 and re.search(r"bbox|box|x1|y1|x2|y2", text, flags=re.IGNORECASE):
        bbox = coerce_bbox(numbers[:4])
        if bbox is not None:
            point = bbox_center(bbox)
            converted, mode = _convert_coordinate_mode(point, image_size, coordinate_mode, text)
            return ParsedPoint(point=converted, mode=mode, source="text_bbox_center")

    if len(numbers) >= 2:
        converted, mode = _convert_coordinate_mode([numbers[0], numbers[1]], image_size, coordinate_mode, text)
        return ParsedPoint(point=converted, mode=mode, source="text_numbers")

    return ParsedPoint(point=None, mode=coordinate_mode, source="no_numbers", error="no coordinate found")


def evaluate_gui_record(record: dict[str, Any], *, coordinate_mode: str = "auto") -> dict[str, Any]:
    image_size = coerce_image_size(record.get("image_size"))
    bbox = coerce_bbox(record.get("bbox"))
    raw_prediction = record.get("prediction_raw")
    if raw_prediction is None and record.get("prediction_point") is not None:
        raw_prediction = json.dumps(record["prediction_point"])

    parsed = parse_gui_point(raw_prediction, image_size, coordinate_mode=coordinate_mode)
    if bbox is None or image_size is None:
        return {
            "prediction_point": parsed.point,
            "parse_success": parsed.point is not None,
            "point_in_bbox": False,
            "center_distance_norm": None,
            "parse_source": parsed.source,
            "parse_mode": parsed.mode,
            "eval_error": "invalid bbox or image_size",
        }

    return {
        "prediction_point": parsed.point,
        "parse_success": parsed.point is not None,
        "point_in_bbox": is_point_in_bbox(parsed.point, bbox),
        "center_distance_norm": center_distance_norm(parsed.point, bbox, image_size),
        "parse_source": parsed.source,
        "parse_mode": parsed.mode,
        "eval_error": parsed.error,
    }
