# === RuleModifierLexicon.py ===
# Stores known static abilities that modify core game rules rather than perform stack-based effects

STATIC_RULE_MODIFIERS = {
    "players can't cast more than one spell each turn": {
        "rule": "cast_limit_per_turn",
        "value": 1,
        "applies_to": "player"
    },
    "creatures can't attack you unless their controller pays": {
        "rule": "attack_tax",
        "cost": "{2}",
        "target": "you"
    },
    "can't attack or block unless": {
        "rule": "combat_restriction"
    },
    "must attack each combat if able": {
        "rule": "must_attack"
    }
}
CONDITIONALS = {
    "if": "conditional_start",
    "as long as": "sustained_condition",
    "unless": "negated_condition",
    "while": "state_condition"
}
