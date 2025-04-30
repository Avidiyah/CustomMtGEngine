# === TreeValidator.py ===
# Phase 3.2 — Behavior Tree Structure & Consistency Validator

class TreeValidator:
    def __init__(self):
        self.issues = []

    def validate(self, tree, card_name="Unknown Card"):
        self.issues.clear()
        self._walk_tree(tree, path=[card_name])
        return self.issues

    def _walk_tree(self, node, path):
        if isinstance(node, list):
            for i, child in enumerate(node):
                self._walk_tree(child, path + [f"[{i}]"])
        elif isinstance(node, dict):
            if (
                "action" not in node
                and "effect_chain" not in node
                and "modal_choices" not in node
                and "trigger" not in node
            ):
                self.issues.append((path, "Missing action or control structure"))

            if node.get("action") in ["unknown_effect", "unparsed_effect"]:
                self.issues.append((path, f"Unrecognized effect: {node['action']}"))

            if "reference_tag" in node and "target_resolved" not in node:
                self.issues.append((path, f"Reference tag '{node['reference_tag']}' present but not resolved"))

            for key, value in node.items():
                self._walk_tree(value, path + [key])

    def summarize(self):
        if not self.issues:
            return "Tree passed all structure checks."
        summary = ["Tree validation issues found:"]
        for path, issue in self.issues:
            summary.append(f"{' -> '.join(path)}: {issue}")
        return "\n".join(summary)
