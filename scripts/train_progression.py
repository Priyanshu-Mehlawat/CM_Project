"""OFFLINE ONLY: fit an interpretable progression baseline on approved feature rows.

Never run on private files from an agent. No raw dataset mappings or labels are
inferred here. Authorized researchers provide protocol-approved index-only rows.
"""

import argparse
import csv
import hashlib
import json
import math
import os
import random
import statistics
from datetime import UTC, datetime
from pathlib import Path

from ml.features.patient import BOUNDS, FEATURES
from ml.inference.bundle import Bundle, infer, transform

APPROVALS = (
    "baseline",
    "eligibility",
    "followup",
    "competing_events",
    "availability",
    "harmonization",
)


def metrics(labels, probabilities):
    n = len(labels)
    positives = sum(labels)
    negatives = n - positives
    if not positives or not negatives:
        raise ValueError("Each evaluation split must contain both outcomes")
    groups = {}
    for y, p in zip(labels, probabilities, strict=True):
        groups.setdefault(p, []).append(y)
    below = 0
    concordance = 0.0
    for p in sorted(groups):
        pos = sum(groups[p])
        neg = len(groups[p]) - pos
        concordance += pos * (below + neg / 2)
        below += neg
    tp, fp, ap = 0, 0, 0.0
    for p in sorted(groups, reverse=True):
        pos = sum(groups[p])
        tp += pos
        fp += len(groups[p]) - pos
        ap += pos / positives * tp / (tp + fp)
    return {
        "n": n,
        "events": positives,
        "prevalence": positives / n,
        "auroc": concordance / (positives * negatives),
        "average_precision": ap,
        "brier": sum((y - p) ** 2 for y, p in zip(labels, probabilities, strict=True)) / n,
    }


def fit(rows, protocol, data_version, seed=31):
    if not rows:
        raise ValueError("No approved feature rows")
    required = {"patient_group", "outcome", "index_stage", "features_available_by_index", *FEATURES}
    if set(rows[0]) != required:
        raise ValueError("Feature table columns mismatch")
    groups = sorted({r["patient_group"] for r in rows})
    if "" in groups or len(groups) < 30:
        raise ValueError("At least 30 patient groups required for an engineering run")
    random.Random(seed).shuffle(groups)
    mapping = {
        g: (
            "train"
            if i < int(0.6 * len(groups))
            else "validation"
            if i < int(0.8 * len(groups))
            else "test"
        )
        for i, g in enumerate(groups)
    }
    partitions = {name: [] for name in ("train", "validation", "test")}
    for r in rows:
        if r["index_stage"] != "1" or r["features_available_by_index"] != "true":
            raise ValueError("Rows must have approved Stage 1 index and available features")
        if r["outcome"] not in ("0", "1"):
            raise ValueError("Unknown outcomes must be handled and reported before fitting")
        values = {k: float(r[k]) if r[k] != "" else None for k in FEATURES}
        for k, v in values.items():
            if v is not None and (not math.isfinite(v) or not BOUNDS[k][0] <= v <= BOUNDS[k][1]):
                raise ValueError("Feature range violation")
        for k in FEATURES[:5]:
            if values[k] is None:
                raise ValueError("Core kidney features cannot be missing")
        if sum(v is None for v in values.values()) > 4:
            raise ValueError("Training row exceeds the inference missing-input limit")
        if (
            abs(values["creatinine_ratio"] - values["creatinine"] / values["reference_creatinine"])
            > 1e-6
        ):
            raise ValueError("Derived creatinine ratio mismatch")
        if (
            abs(values["creatinine_delta"] - values["creatinine"] + values["reference_creatinine"])
            > 1e-6
        ):
            raise ValueError("Derived creatinine delta mismatch")
        partitions[mapping[r["patient_group"]]].append((values, int(r["outcome"])))
    for split in partitions.values():
        if len(split) < 10 or {y for _, y in split} != {0, 1}:
            raise ValueError(
                "Each grouped split requires >=10 rows and both outcomes; inspect feasibility"
            )
    training = partitions["train"]
    medians, means, scales = [], [], []
    for name in FEATURES:
        present = [v[name] for v, _ in training if v[name] is not None]
        if not present:
            raise ValueError("Feature wholly missing in training")
        median = statistics.median(present)
        filled = [v[name] if v[name] is not None else median for v, _ in training]
        medians.append(median)
        means.append(statistics.mean(filled))
        scales.append(statistics.pstdev(filled) or 1.0)
    bundle = Bundle(
        model_version="lr-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ"),
        protocol_version=protocol,
        data_version=data_version,
        trained_at=datetime.now(UTC).isoformat(),
        training_source="authorized_research",
        features=list(FEATURES),
        medians=medians,
        means=means,
        scales=scales,
        coefficients=[0.0] * (len(FEATURES) * 2),
        intercept=0.0,
        metrics={},
    )
    matrix = [(transform(bundle, v), y) for v, y in training]
    # Convex L2-regularized logistic regression; no evaluation data enters fitting.
    rate = 1 / (1 + max(sum(t * t for t in x) for x, _ in matrix) / 4)
    for iteration in range(20000):
        gradients = [0.0] * len(bundle.coefficients)
        bias = 0.0
        for x, y in matrix:
            z = bundle.intercept + sum(a * b for a, b in zip(x, bundle.coefficients, strict=True))
            residual = 1 / (1 + math.exp(-max(-700, min(700, z)))) - y
            bias += residual / len(matrix)
            for j, value in enumerate(x):
                gradients[j] += residual * value / len(matrix)
        gradients = [g + 0.01 * w for g, w in zip(gradients, bundle.coefficients, strict=True)]
        if max(abs(bias), *(abs(g) for g in gradients)) < 1e-5:
            break
        bundle.intercept -= rate * bias
        bundle.coefficients = [
            w - rate * g for w, g in zip(bundle.coefficients, gradients, strict=True)
        ]
    else:
        raise ValueError("Optimizer did not converge; do not deploy this run")
    for name, split in partitions.items():
        bundle.metrics[name] = metrics(
            [y for _, y in split], [infer(bundle, v)[0] for v, _ in split]
        )
    bundle.training_config = {
        "seed": seed,
        "train_fraction": 0.6,
        "validation_fraction": 0.2,
        "l2": 0.01,
        "gradient_tolerance": 1e-5,
        "iterations": iteration + 1,
        "software_version": "0.3.0",
    }
    for split_name in partitions:
        members = sorted(g for g in groups if mapping[g] == split_name)
        bundle.training_config[split_name + "_group_hash"] = hashlib.sha256(
            json.dumps(members).encode()
        ).hexdigest()
    return bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--approved-protocol", type=Path, required=True)
    parser.add_argument("--data-version", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.output.resolve().is_relative_to(root):
        parser.error("Write bundles outside the source checkout and agent environment")
    try:
        protocol = json.loads(args.approved_protocol.read_text())
        if not all(protocol.get(k) is True for k in APPROVALS) or not protocol.get("reviewer"):
            raise ValueError("Protocol approvals required")
        with args.features.open(newline="") as stream:
            bundle = fit(list(csv.DictReader(stream)), protocol["version"], args.data_version)
        raw = bundle.model_dump_json(indent=2).encode()
        # Exclusive creation protects existing runs; private filesystem permissions.
        fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
        print("Training complete. Bundle SHA256:", hashlib.sha256(raw).hexdigest())
        print(
            "Keep bundle/metrics private pending disclosure review. No clinical validation implied."
        )
    except (OSError, ValueError, KeyError, TypeError):
        parser.exit(
            1,
            "Training failed: check approved protocol, feature schema, grouped split feasibility, "
            "optimizer convergence and output location locally. Patient details withheld.\n",
        )


if __name__ == "__main__":
    main()
