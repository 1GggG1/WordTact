from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "user/novel-auditor/scripts/style_reference.py"
spec = importlib.util.spec_from_file_location("style_reference", SCRIPT)
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)


class StyleReferenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.manifest = {"schema_version": 1, "language": "zh", "text_type": "fiction",
                         "profile_id": "test-reference", "revision": 1,
                         "scope": "constructed language examples", "units": []}
        self.features = {"schema_version": 1, "measurement": dict(style.MEASUREMENT, window_chars=4),
                         "features": [{"id": "bian", "definition": "surface 便", "count_basis": "surface",
                                       "forms": [{"kind": "literal", "value": "便"}]}]}

    def unit(self, text, uid="fit1", role="fit", group="author/work", register="narration", partition=None):
        (self.root / (uid + ".txt")).write_bytes(text.encode("utf-8"))
        item = {"unit_id": uid, "path": uid + ".txt", "complete_chapter": False, "source_group": group,
                "partition_group": partition or uid, "register": register, "role": role}
        self.manifest["units"].append(item)
        return item

    def collect(self):
        return style.collect(self.root, self.manifest, self.features)

    def labels(self, evidence, applies=True):
        labels = style.annotation_template(evidence)
        labels["reviewer"] = "test reviewer v1"
        for row in labels["classifications"]:
            row.update(applies=applies, reason="reviewed in the complete synthetic context")
        return labels

    def policy(self, evidence, annotations=None):
        params = {"min_partitions": 2, "min_windows": 2, "min_feature_count": 2,
                  "min_feature_partitions": 2, "upper_quantile": 0.9, "min_extra_count": 1}
        return {"schema_version": 1, "feature_sha256": evidence["feature_sha256"], "parameters": params,
                "calibration": {"evidence_id": evidence["evidence_id"],
                                "annotations_sha256": style.fingerprint(annotations),
                                "parameter_sha256": style.fingerprint(params),
                                "unit_ids": [u["unit_id"] for u in evidence["units"] if u["role"] == "calibration"],
                                "assessment": "Synthetic algorithm fixture, not a literary threshold recommendation."}}

    def reference(self, semantic=False):
        if semantic:
            self.features["features"][0]["count_basis"] = "semantic"
        self.unit("便甲乙丙丁戊己庚", "fit1")
        self.unit("便甲乙丙丁戊己辛", "fit2")
        self.unit("甲乙便丙丁戊己壬", "cal1", "calibration")
        self.unit("甲乙便丙丁戊己癸", "cal2", "calibration")
        evidence = self.collect()
        annotations = self.labels(evidence) if semantic else None
        return style.build(self.root, evidence, annotations, self.policy(evidence, annotations))

    def target(self, text="便便便便甲乙丙丁", register="narration"):
        self.manifest["units"] = []
        self.unit(text, "target1", "target", "our/work", register)
        return self.collect()

    def test_zero_windows_and_partial_tail_are_explicit(self):
        self.unit("便甲乙丙丁戊己庚辛")
        result = self.collect()
        rows = [r for r in result["statistics"] if r["scope_kind"] == "window"]
        self.assertEqual([r["surface_count"] for r in rows], [1, 0, 0])
        self.assertEqual([r["partial"] for r in rows], [False, False, True])
        built = style.build(self.root, result)
        stats = built["groups"][0]["statistics"]
        self.assertEqual(stats["window_rates"], [2500, 0])
        self.assertEqual(stats["quantiles"]["0.5"], 1250)
        self.assertAlmostEqual(stats["per_10000"], 10000 / 9)

    def test_same_total_different_clustering(self):
        self.unit("便甲乙丙便丁戊己", "spread")
        self.unit("便便甲乙丙丁戊己", "clustered", group="other/work")
        built = style.build(self.root, self.collect())
        a, b = [g["statistics"] for g in built["groups"]]
        self.assertEqual(a["per_10000"], b["per_10000"])
        self.assertNotEqual(a["window_presence"], b["window_presence"])

    def test_overlapping_forms_cross_window_and_crlf_offsets(self):
        text = "甲\r\n\r\n乙丙方便丁戊己"
        self.features["features"][0]["forms"] = [{"kind": "literal", "value": "方便"},
                                                   {"kind": "literal", "value": "便"}]
        self.unit(text)
        result = self.collect()
        self.assertEqual(len(result["occurrences"]), 1)
        hit = result["occurrences"][0]
        self.assertEqual(text[hit["start"]:hit["end"]], "方便")
        self.assertEqual(result["units"][0]["source_sha256"], style.language.digest(text.encode()))
        rows = [r for r in result["statistics"] if r["scope_kind"] == "window"]
        self.assertEqual([r["surface_count"] for r in rows], [1, 0])
        self.assertEqual(len(result["raw_matches"][0]["matches"]), 2)

    def test_unwindowed_and_short_input_have_no_fabricated_distribution(self):
        self.features["measurement"]["window_chars"] = None
        self.unit("便。")
        built = style.build(self.root, self.collect())
        self.assertEqual(built["groups"][0]["statistics"]["window_rates"], [])
        self.assertIn("no_full_reference_windows", built["groups"][0]["advisory_limits"])

    def test_semantic_counts_exclude_other_senses_and_keep_retained_uses(self):
        self.features["features"][0]["count_basis"] = "semantic"
        self.unit("方便随便，雨停便走，他答应便开门。")
        evidence = self.collect()
        labels = self.labels(evidence)
        for row in labels["classifications"][:2]:
            row.update(applies=False, reason="词内成分")
        stats = style.build(self.root, evidence, labels)["groups"][0]["statistics"]
        self.assertEqual(stats["surface_count"], 4)
        self.assertEqual(stats["count"], 2)
        self.assertTrue(stats["complete"])

    def test_missing_semantic_labels_do_not_block_surface_feature(self):
        self.features["features"][0]["count_basis"] = "semantic"
        surface = copy.deepcopy(self.features["features"][0])
        surface.update(id="surface-bian", count_basis="surface")
        self.features["features"].append(surface)
        self.unit("便甲乙丙丁戊己庚")
        built = style.build(self.root, self.collect())
        semantic, surface = [g["statistics"] for g in built["groups"]]
        self.assertIsNone(semantic["count"])
        self.assertEqual(semantic["window_rates"], [])
        self.assertEqual(surface["count"], 1)

    def test_annotation_identity_completeness_and_boolean_validation(self):
        self.features["features"][0]["count_basis"] = "semantic"
        self.unit("便便甲乙")
        evidence = self.collect()
        for mutate in (lambda a: a.update(evidence_id="wrong"),
                       lambda a: a["classifications"].append(a["classifications"][0]),
                       lambda a: a["classifications"][0].update(id="unknown"),
                       lambda a: a["classifications"][0].update(applies=1),
                       lambda a: a["classifications"][0].update(reason="")):
            labels = self.labels(evidence)
            mutate(labels)
            with self.assertRaises(style.ValidationError):
                style.build(self.root, evidence, labels)
        labels = self.labels(evidence)
        labels["classifications"].pop()
        self.assertFalse(style.build(self.root, evidence, labels)["groups"][0]["statistics"]["complete"])

    def test_changed_source_feature_or_report_invalidates_evidence(self):
        self.unit("便甲乙丙")
        original = self.collect()
        for mutate in (lambda e: e["statistics"][0].update(surface_count=0),
                       lambda e: e["feature_spec"]["features"][0].update(definition="changed definition")):
            evidence = copy.deepcopy(original)
            mutate(evidence)
            with self.assertRaises(style.ValidationError):
                style.build(self.root, evidence)
        (self.root / "fit1.txt").write_text("便便乙丙")
        with self.assertRaisesRegex(style.ValidationError, "stale"):
            style.build(self.root, original)

    def test_feature_definitions_bind_hit_ids(self):
        self.unit("便甲乙丙")
        first = self.collect()
        self.features["features"][0]["definition"] = "different intended use"
        second = self.collect()
        self.assertNotEqual(first["occurrences"][0]["id"], second["occurrences"][0]["id"])

    def test_duplicate_copies_and_partition_leakage_rejected(self):
        self.unit("便甲乙丙")
        self.unit("便甲乙丙", "copy")
        with self.assertRaisesRegex(style.ValidationError, "duplicate source content"):
            self.collect()
        (self.root / "copy.txt").write_text("便甲乙丁")
        self.manifest["units"][1].update(partition_group="fit1", role="calibration")
        with self.assertRaisesRegex(style.ValidationError, "crosses dataset"):
            self.collect()

    def test_original_slice_verification_and_overlap(self):
        original = "甲乙丙丁便戊己庚"
        (self.root / "original.txt").write_text(original)
        sha = style.language.digest(original)
        a = self.unit(original[:5])
        a["extraction"] = {"path": "original.txt", "source_sha256": sha, "start": 0, "end": 5}
        b = self.unit(original[4:], "slice2")
        b["extraction"] = {"path": "original.txt", "source_sha256": sha, "start": 4, "end": 8}
        with self.assertRaisesRegex(style.ValidationError, "overlapping"):
            self.collect()
        self.manifest["units"].pop()
        a["extraction"]["source_sha256"] = "stale"
        with self.assertRaisesRegex(style.ValidationError, "stale extraction"):
            self.collect()

    def test_paths_and_symlinks_cannot_escape_root(self):
        item = self.unit("便甲乙丙")
        item["path"] = "../outside.txt"
        with self.assertRaises(style.ValidationError):
            self.collect()
        with tempfile.TemporaryDirectory() as other:
            outside = Path(other) / "outside.txt"
            outside.write_text("便甲乙丁")
            (self.root / "link.txt").symlink_to(outside)
            item["path"] = "link.txt"
            with self.assertRaisesRegex(style.ValidationError, "escapes"):
                self.collect()

    def test_invalid_spec_rejected(self):
        self.unit("便甲乙丙")
        for mutate in (lambda f: f["measurement"].update(normalization="NFKC"),
                       lambda f: f["measurement"].update(window_chars=True),
                       lambda f: f["features"].append(copy.deepcopy(f["features"][0])),
                       lambda f: f["features"][0].update(thresholds={"count": 2}),
                       lambda f: f["features"][0].update(forms=[{"kind": "regex", "value": "a*"}])):
            spec = copy.deepcopy(self.features)
            mutate(spec)
            with self.assertRaises(style.ValidationError):
                style.collect(self.root, self.manifest, spec)

    def test_build_only_fits_fit_units_and_records_calibration_separately(self):
        reference = self.reference()
        self.assertEqual(reference["groups"][0]["statistics"]["unit_count"], 2)
        self.assertEqual(reference["groups"][0]["statistics"]["count"], 2)
        self.assertEqual(reference["calibration_statistics"][0]["statistics"]["count"], 2)
        self.assertEqual(len(reference["calibration_results"]), 4)
        self.assertEqual(reference["state"], "calibrated")
        self.manifest["units"][0]["role"] = "holdout"
        with self.assertRaisesRegex(style.ValidationError, "holdout"):
            style.build(self.root, self.collect())

    def test_policy_parameters_and_classification_records_are_bound(self):
        self.reference()
        evidence = self.collect()
        for mutate in (lambda p: p["parameters"].update(min_extra_count=2),
                       lambda p: p["calibration"].update(unit_ids=["fit1", "fit2"]),
                       lambda p: p["calibration"].update(annotations_sha256="stale"),
                       lambda p: p["calibration"].update(assessment="")):
            policy = self.policy(evidence)
            mutate(policy)
            with self.assertRaises(style.ValidationError):
                style.build(self.root, evidence, policy=policy)

    def test_calibration_uses_the_same_support_limits_as_comparison(self):
        self.reference()
        (self.root / "cal1.txt").write_text("便便便便甲乙丙丁")
        evidence = self.collect()
        policy = self.policy(evidence)
        policy["parameters"]["min_feature_count"] = 20
        policy["calibration"]["parameter_sha256"] = style.fingerprint(policy["parameters"])
        reference = style.build(self.root, evidence, policy=policy)
        self.assertFalse(any(r["candidate"] for r in reference["calibration_results"]))
        self.assertTrue(all("insufficient_feature_count" in r["advisory_limits"] for r in reference["calibration_results"]))

    def test_calibrated_deviation_returns_advisory_positions(self):
        reference = self.reference()
        evidence = self.target()
        result = style.compare(self.root, evidence, reference)
        self.assertEqual(result["candidate_total"], 1)
        candidate = result["review_candidates"][0]
        self.assertEqual(candidate["count"], 4)
        self.assertEqual(candidate["decision"], "context_review")
        self.assertEqual(len(candidate["occurrence_ids"]), 4)
        self.assertNotIn("PASS", json.dumps(result))
        self.assertEqual(result["measurement_status"], "complete")

    def test_descriptive_profile_never_generates_automatic_candidates(self):
        self.unit("便甲乙丙")
        reference = style.build(self.root, self.collect())
        result = style.compare(self.root, self.target(), reference)
        self.assertEqual(result["candidate_total"], 0)
        self.assertIn("descriptive_profile", result["comparisons"][0]["advisory_limits"])
        self.assertTrue(result["comparisons"][0]["windows"][0]["comparable"])

    def test_zero_reference_and_lower_frequency_never_request_filler(self):
        self.unit("甲乙丙丁")
        reference = style.build(self.root, self.collect())
        result = style.compare(self.root, self.target(), reference)
        self.assertEqual(result["candidate_total"], 0)
        self.assertIn("feature_not_observed_in_reference", result["comparisons"][0]["advisory_limits"])
        self.assertNotIn("Infinity", json.dumps(result))
        self.manifest["units"] = []
        reference = self.reference()
        result = style.compare(self.root, self.target("子丑寅卯辰巳午未"), reference)
        self.assertEqual(result["candidate_total"], 0)

    def test_short_or_mismatched_register_is_explained_without_failure(self):
        reference = self.reference()
        result = style.compare(self.root, self.target("便便。"), reference)
        self.assertIn("no_full_target_windows", result["comparisons"][0]["advisory_limits"])
        self.assertEqual(result["candidate_total"], 0)
        result = style.compare(self.root, self.target(register="formal-dialogue"), reference)
        self.assertIn("register_mismatch", result["comparisons"][0]["advisory_limits"])

    def test_semantic_incomplete_target_suppresses_advisory_not_measurement(self):
        reference = self.reference(semantic=True)
        evidence = self.target()
        result = style.compare(self.root, evidence, reference)
        self.assertEqual(result["measurement_status"], "partial")
        self.assertEqual(result["candidate_total"], 0)
        result = style.compare(self.root, evidence, reference, self.labels(evidence))
        self.assertEqual(result["candidate_total"], 1)

    def test_target_identity_and_source_overlap_are_rejected(self):
        reference = self.reference()
        evidence = self.target("便甲乙丙丁戊己庚")
        with self.assertRaisesRegex(style.ValidationError, "duplicates"):
            style.compare(self.root, evidence, reference)
        self.target()
        self.manifest["units"][0].update(source_group="author/work", partition_group="fit1")
        with self.assertRaisesRegex(style.ValidationError, "shares"):
            style.compare(self.root, self.collect(), reference)

    def test_different_reference_groups_require_explicit_selection(self):
        self.unit("便甲乙丙")
        self.unit("便丁戊己", "author2", group="second/work")
        reference = style.build(self.root, self.collect())
        evidence = self.target()
        with self.assertRaisesRegex(style.ValidationError, "multiple reference"):
            style.compare(self.root, evidence, reference)
        self.assertEqual(style.compare(self.root, evidence, reference, reference_group="second/work")["reference_group"], "second/work")

    def test_changed_measurement_and_reference_artifact_are_rejected(self):
        reference = self.reference()
        self.features["measurement"]["window_chars"] = 8
        with self.assertRaisesRegex(style.ValidationError, "incompatible features"):
            style.compare(self.root, self.target(), reference)
        self.features["measurement"]["window_chars"] = 4
        reference["groups"][0]["statistics"]["count"] = 0
        with self.assertRaisesRegex(style.ValidationError, "modified style_reference"):
            style.compare(self.root, self.target(), reference)

    def test_truncation_is_explicit_and_full_comparisons_survive(self):
        reference = self.reference()
        result = style.compare(self.root, self.target("便便便便便便便便"), reference, max_results=1)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["candidate_total"], 2)
        self.assertEqual(len(result["review_candidates"]), 1)
        self.assertEqual(len(result["comparisons"][0]["windows"]), 2)

    def test_cli_pipeline_outside_cwd_and_no_overwrite(self):
        self.unit("便甲乙丙丁戊己庚")
        def write(name, value):
            path = self.root / name
            path.write_text(json.dumps(value, ensure_ascii=False))
            return path
        manifest = write("manifest.json", self.manifest)
        features = write("features.json", self.features)
        evidence = self.root / "evidence.json"
        def run(*args):
            return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], cwd=self.root,
                                  text=True, capture_output=True, check=False)
        args = ["collect", "--source-root", self.root, "--manifest", manifest, "--features", features, "--output", evidence]
        self.assertEqual(run(*args).returncode, 0)
        self.assertEqual(run(*args).returncode, 2)
        reference = self.root / "reference.json"
        result = run("build", "--source-root", self.root, "--evidence", evidence, "--output", reference)
        self.assertEqual(result.returncode, 0, result.stderr)
        target = write("target-evidence.json", self.target())
        result = run("compare", "--source-root", self.root, "--evidence", target, "--reference", reference)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["kind"], "style_comparison")

    def test_cli_annotation_template_is_bound_and_outputs_preflighted(self):
        self.features["features"][0]["count_basis"] = "semantic"
        self.unit("便甲乙丙")
        for name, value in (("manifest.json", self.manifest), ("features.json", self.features)):
            (self.root / name).write_text(json.dumps(value))
        output, template = self.root / "evidence.json", self.root / "labels.json"
        args = [sys.executable, str(SCRIPT), "collect", "--source-root", str(self.root),
                "--manifest", str(self.root / "manifest.json"), "--features", str(self.root / "features.json"),
                "--output", str(output), "--template-output", str(template)]
        template.write_text("keep existing annotations")
        result = subprocess.run(args, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(output.exists())
        template.unlink()
        result = subprocess.run(args, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        evidence, labels = json.loads(output.read_text()), json.loads(template.read_text())
        self.assertEqual(labels["evidence_id"], evidence["evidence_id"])
        self.assertIsNone(labels["classifications"][0]["applies"])


if __name__ == "__main__":
    unittest.main()
