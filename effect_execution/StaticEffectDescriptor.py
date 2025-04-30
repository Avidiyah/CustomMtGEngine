# === StaticEffectDescriptor.py ===
# Describes parsed static effects for Magic: The Gathering Engine

class StaticEffectDescriptor:
    def __init__(self, target_class, granted_abilities=None, power_boost=0, toughness_boost=0,
                 restrictions=None, rules_overwrites=None, keywords_removed=None,
                 layer=None, duration="permanent", source=None, timestamp=None,
                 dependency_targets=None):
        self.target_class = target_class  # e.g., "creatures you control"
        self.granted_abilities = granted_abilities if granted_abilities else []
        self.power_boost = power_boost
        self.toughness_boost = toughness_boost
        self.restrictions = restrictions if restrictions else []
        self.rules_overwrites = rules_overwrites if rules_overwrites else []
        self.keywords_removed = keywords_removed if keywords_removed else []
        self.layer = layer  # MTG Layer: 6 (abilities), 7a/b/c (P/T), 9 (rules overwrites), etc.
        self.duration = duration  # Typically "permanent", or "until end of turn"
        self.source = source  # Source card or ability object
        self.timestamp = timestamp  # Creation time
        self.dependency_targets = dependency_targets or []

    def apply(self, game_state):
        """Apply this static effect to the appropriate permanents on the battlefield."""
        for permanent in game_state.battlefield:
            if self.matches_target(permanent):
                self.apply_to_permanent(permanent)

    def matches_target(self, permanent):
        """Simple targeting logic placeholder. Expand this for proper targeting classes later."""
        if self.target_class == "permanent":
            return True
        if self.target_class == "creature" and "Creature" in permanent.types:
            return True
        if self.target_class == "creatures you control" and "Creature" in permanent.types and permanent.controller == self.source.controller:
            return True
        # Expand this logic for more fine-grained targeting later
        return False

    def apply_to_permanent(self, permanent):
        """Apply abilities, boosts, restrictions, overwrites to a permanent."""
        # Layer 6 — Ability adding
        for ability in self.granted_abilities:
            if ability not in permanent.abilities:
                permanent.abilities.append(ability)

        # Layer 7c — Power/Toughness modifications
        if hasattr(permanent, 'power') and hasattr(permanent, 'toughness'):
            permanent.power += self.power_boost
            permanent.toughness += self.toughness_boost

        # Layer 9 — Rules overwrites and restrictions
        if "can't gain life" in self.rules_overwrites:
            permanent.life_gain_prevention = True  # Placeholder attribute
        if "must attack" in self.restrictions:
            permanent.must_attack = True  # Placeholder attribute

    def __repr__(self):
        return (f"<StaticEffectDescriptor target={self.target_class} abilities={self.granted_abilities} "
                f"PT=({self.power_boost}/{self.toughness_boost}) restrictions={self.restrictions} "
                f"overwrites={self.rules_overwrites} layer={self.layer} duration={self.duration}>")
