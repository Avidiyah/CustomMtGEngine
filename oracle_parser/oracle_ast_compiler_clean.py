# === ORACLE AST COMPILER ===
# Converts tokenized Oracle text into a structured abstract syntax tree (AST)

import re

class OracleASTCompiler:
    def __init__(self):
        pass

    def compile(self, oracle_text):
        """
        Breaks Oracle text into a nested AST structure.
        """
        segments = self._split_clauses(oracle_text)
        ast = []

        for segment in segments:
            normalized = segment.lower().strip()

            # --- Modal Choice Handling ---
            if normalized.startswith("choose one —") or normalized.startswith("choose one -"):
                options = self._parse_modal_options(normalized)
                ast.append({
                    "type": "modal",
                    "options": options
                })

            # --- Conditional Chain Handling ---
            elif "if" in normalized and "then" in normalized:
                condition_part, consequence_part = normalized.split("then", 1)
                if "otherwise" in consequence_part:
                    then_part, else_part = consequence_part.split("otherwise", 1)
                    ast.append({
                        "type": "conditional",
                        "condition": condition_part.replace("if", "").strip(),
                        "then": self.compile(then_part.strip()),
                        "else": self.compile(else_part.strip())
                    })
                else:
                    ast.append({
                        "type": "conditional",
                        "condition": condition_part.replace("if", "").strip(),
                        "then": self.compile(consequence_part.strip())
                    })

            # --- Loop / Repeat Handling ---
            elif "repeat this process" in normalized or "for each" in normalized:
                ast.append({
                    "type": "repeat",
                    "content": normalized,
                    "children": self.compile(self._clean_repeat_text(normalized))
                })

            # --- Compound Effects Split by 'and' ---
            elif " and " in normalized and not normalized.startswith("search your library"):
                parts = re.split(r' and ', normalized)
                for part in parts:
                    ast.append(self._wrap_effect(part.strip()))

            # --- Default Case ---
            else:
                ast.append(self._wrap_effect(normalized))

        return ast

    def _split_clauses(self, text):
        """
        Naively splits based on periods, semicolons, or line breaks.
        """
        text = text.replace("—", "-").replace("â€”", "-")
        return re.split(r'\. |; |\n', text)

    def _parse_modal_options(self, text):
        """
        Extract modal options (after 'choose one —') into separate AST branches.
        """
        text = text.replace("choose one -", "").replace("choose one —", "").strip()
        options = text.split(";")
        return [self._wrap_effect(opt.strip()) for opt in options if opt]

    def _wrap_effect(self, text):
        """
        Wraps a simple effect string as an AST node
        """
        return {"type": "effect", "content": text}

    def _clean_repeat_text(self, text):
        """
        Cleans up repeated effect clause for child parsing.
        """
        if "repeat this process" in text:
            return text.split("repeat this process")[0].strip()
        return text
