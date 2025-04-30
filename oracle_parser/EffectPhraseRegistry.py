import re

# === Shared Constants ===

COLORS = ["white", "blue", "black", "red", "green"]
KEYWORD_ABILITIES = [
    "flying", "vigilance", "haste", "deathtouch", "trample",
    "first strike", "double strike", "lifelink", "hexproof",
    "indestructible", "menace", "ward", "reach", "protection"
]

# === Helper Parsing Functions ===

def parse_create_token_phrase(text):
    token = {
        "power": None,
        "toughness": None,
        "colors": [],
        "types": [],
        "abilities": [],
        "copy_of": None
    }
    pt_match = re.search(r"(\d)/(\d)", text)
    if pt_match:
        token["power"] = int(pt_match.group(1))
        token["toughness"] = int(pt_match.group(2))
    for color in COLORS:
        if color in text:
            token["colors"].append(color)
    for ability in KEYWORD_ABILITIES:
        if ability in text:
            token["abilities"].append(ability)
    if "offspring" in text:
        token["copy_of"] = "source"
        token["power"] = 1
        token["toughness"] = 1
    return {
        "action": "create_token",
        "effect_family": "token_creation",
        "token": token
    }

def parse_return_to_battlefield(text):
    return {
        "action": "return_to_battlefield",
        "timing": "beginning_of_next_end_step"
    }

def parse_power_toughness_modifier(text):
    if "+1/+1" in text:
        return {
            "type": "static_effect",
            "layer": "7c",
            "power_boost": 1,
            "toughness_boost": 1
        }
    elif "-1/-1" in text:
        return {
            "type": "static_effect",
            "layer": "7c",
            "power_boost": -1,
            "toughness_boost": -1
        }
    return None

def parse_static_combat_restriction(text):
    if "can't attack" in text:
        return {
            "type": "static_effect",
            "layer": "6",
            "restriction": "cant_attack"
        }
    if "must attack each combat if able" in text:
        return {
            "type": "static_effect",
            "layer": "6",
            "restriction": "must_attack"
        }
    return None


def parse_return_to_hand_with_reference(text):
    if "that creature" in text:
        return {"action": "return_to_hand", "reference_tag": "that_creature"}
    if "that spell" in text:
        return {"action": "return_to_hand", "reference_tag": "that_spell"}
    return {"action": "return_to_hand"}

def parse_give_haste_to_tokens(text):
    if "those tokens" in text:
        return {"action": "grant_keyword", "reference_tag": "those_tokens", "keyword": "haste"}
    return {"action": "grant_keyword", "keyword": "haste"}

def parse_keyword_ability(text):
    text = text.lower()
    if any(word in text for word in ["gains", "target", "equipped", "until end of turn"]):
        return {"action": "unknown_effect"}
    detected = []
    for part in text.split(","):
        part = part.strip()
        for keyword in KEYWORD_ABILITIES:
            if keyword in part:
                detected.append({
                    "type": "static_ability",
                    "ability": keyword
                })
    return detected if detected else {"action": "unknown_effect"}

def parse_solve_case(text):
    return {
        "action": "set_state_flag",
        "effect_family": "state_modification",
        "flag": "solved"
    }

# === STANDARD_EFFECTS Registry ===

STANDARD_EFFECTS = {
    "draw_card": {
        "phrases": ["draw a card", "draw two cards", "draw three cards"],
        "parse": lambda text: {"action": "draw_card"}
    },
    "gain_life": {
        "phrases": ["gain life", "you gain 3 life", "you gain 1 life"],
        "parse": lambda text: {"action": "gain_life"}
    },
    "lose_life": {
        "phrases": ["lose life", "you lose 2 life", "you lose 1 life"],
        "parse": lambda text: {"action": "lose_life"}
    },
    "deal_damage": {
        "phrases": ["deal damage", "deals 2 damage"],
        "parse": lambda text: {"action": "deal_damage"}
    },
    "destroy_target": {
        "phrases": ["destroy target", "destroy target tapped creature", "destroy target artifact", "destroy target planeswalker"],
        "parse": lambda text: {"action": "destroy_target"}
    },
    "exile_target": {
        "phrases": ["exile target", "exile up to one target"],
        "parse": lambda text: {"action": "exile_target"}
    },
    "tap_target": {
        "phrases": ["tap target creature", "tap target permanent"],
        "parse": lambda text: {"action": "tap_target"}
    },
    "untap_target": {
        "phrases": ["untap target creature", "untap target permanent"],
        "parse": lambda text: {"action": "untap_target"}
    },
    "return_to_hand": {
        "phrases": ["return target creature to its owner's hand", "return target permanent to its owner's hand"],
        "parse": lambda text: {"action": "return_to_hand"}
    },
    "counter_spell": {
        "phrases": ["counter target spell", "counter target activated ability", "counter target triggered ability"],
        "parse": lambda text: {"action": "counter_spell"}
    },
    "create_token": {
        "phrases": [
            "create a token", "create a 1/1 white vampire",
            "create a 1/1 white soldier creature token",
            "create a 3/3 green beast creature token",
            "create a clue token"
        ],
        "parse": parse_create_token_phrase
    },
    "offspring": {
        "phrases": ["offspring", "create an offspring token"],
        "parse": parse_create_token_phrase
    },
    "solve_case": {
        "phrases": ["solve the case", "solved"],
        "parse": parse_solve_case
    },
    "buff_all_creatures": {
        "phrases": ["creatures you control get +1/+1", "other creatures you control get +1/+1"],
        "parse": parse_power_toughness_modifier
    },
    "combat_restrictions": {
        "phrases": ["can't attack", "must attack each combat if able"],
        "parse": parse_static_combat_restriction
    },
    "grant_keyword": {
        "phrases": KEYWORD_ABILITIES,
        "parse": parse_keyword_ability
    }
}
