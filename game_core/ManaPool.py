"""Mana pool utilities for players.

This module defines the :class:`ManaPool` used by ``Player`` objects to keep
track of their available mana.  The pool stores counts for each coloured mana
symbol (``W``, ``U``, ``B``, ``R``, ``G`` and ``C``) and provides helpers to
parse and spend mana costs including generic and hybrid notation such as
``{2/W}`` or ``{G/U}``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Union
import re

@dataclass
class ManaPool:
    def __init__(self):
    """Container for a player's available mana.

    Parameters
    ----------
    pool : dict[str, int], optional
        Initial mana values by colour.  Colours not supplied default to ``0``.
    """

    pool: Dict[str, int] = field(default_factory=lambda: {c: 0 for c in "WUBRGC"})

    COLORS = ("W", "U", "B", "R", "G", "C")

    # ------------------------------------------------------------------
    # Basic operations
    # ------------------------------------------------------------------
    def add(self, color: str, amount: int = 1) -> None:
        """Add mana of ``color`` to the pool.
   
        Raises
        ------
        ValueError
            If ``color`` is unknown or ``amount`` is negative.
        """
        if color not in self.COLORS:
            raise ValueError(f"Invalid mana colour: {color}")
        if amount < 0:
            raise ValueError("Cannot add a negative amount of mana")
        self.pool[color] += amount
            elif sym in cost:
    def spend(self, color: str, amount: int = 1) -> None:
        """Remove mana of ``color`` from the pool.

        Raises
        ------
        ValueError
            If ``color`` is unknown or the pool lacks enough mana.
        """
        if color not in self.COLORS:
            raise ValueError(f"Invalid mana colour: {color}")
        if amount < 0:
            raise ValueError("Cannot spend a negative amount of mana")
        if self.pool[color] < amount:
            raise ValueError(f"Not enough {color} mana to spend")
        self.pool[color] -= amount

    def available(self, color: str | None = None) -> Union[int, Dict[str, int]]:
        """Return available mana.

        Parameters
        ----------
        color : str, optional
            When provided, returns the amount of that colour.  Otherwise a copy
            of the entire pool is returned.
        """
        if color is None:
            return dict(self.pool)
        if color not in self.COLORS:
            raise ValueError(f"Invalid mana colour: {color}")
        return self.pool[color]

    def reset(self) -> None:
        """Clear all mana from the pool."""
        for c in self.COLORS:
            self.pool[c] = 0

    def total(self) -> int:
        """Return the total amount of mana in the pool."""
                return sum(self.pool.values())

    # ------------------------------------------------------------------
    # Mana cost handling
    # ------------------------------------------------------------------
    _symbol_pattern = re.compile(r"{(.*?)}")

    def parse_cost(self, mana_cost: str) -> tuple[Dict[str, int], int, List[List[Union[str, int]]]]:
        """Parse a mana cost string.

        Parameters
        ----------
        mana_cost : str
            Mana cost using braces notation, e.g. ``"{1}{G}{G/U}"``.

        Returns
        -------
        tuple
            ``(colours, generic, hybrids)`` where ``colours`` is a mapping of
            colour symbols to integer counts, ``generic`` is the amount of
            generic mana required and ``hybrids`` is a list describing each
            hybrid symbol as a list of options.  Hybrid options are either a
            colour symbol or an integer representing generic mana.
        """
        colours = {c: 0 for c in self.COLORS}
        generic = 0
        hybrids: List[List[Union[str, int]]] = []

        for sym in self._symbol_pattern.findall(mana_cost):
            if sym.isdigit():
                generic += int(sym)
            elif "/" in sym:
                parts = [p.strip() for p in sym.split("/")]
                opts: List[Union[str, int]] = []
                for p in parts:
                    if p.isdigit():
                        opts.append(int(p))
                    elif p in self.COLORS:
                        opts.append(p)
                    else:
                        raise ValueError(f"Unknown mana symbol: {sym}")
                hybrids.append(opts)
            elif sym in self.COLORS:
                colours[sym] += 1
            else:
                raise ValueError(f"Unknown mana symbol: {sym}")
        return colours, generic, hybrids

    # ------------------------------------------------------------------
    # Internal helper for paying hybrid/generic costs
    # ------------------------------------------------------------------
    def _allocate(self, available: Dict[str, int], hybrids: List[List[Union[str, int]]],
                  index: int, generic_needed: int, path: Dict[str, int]) -> Dict[str, int] | None:
        if index == len(hybrids):
            if sum(available.values()) < generic_needed:
                return None
            allocation = path.copy()
            remaining = available.copy()
            need = generic_needed
            for colour in self.COLORS:
                if need == 0:
                    break
                use = min(remaining[colour], need)
                if use:
                    allocation[colour] = allocation.get(colour, 0) + use
                    remaining[colour] -= use
                    need -= use
            return allocation if need == 0 else None

        for opt in hybrids[index]:
            if isinstance(opt, int):
                res = self._allocate(available, hybrids, index + 1, generic_needed + opt, path)
                if res:
                    return res
            else:
                if available.get(opt, 0) > 0:
                    avail_copy = available.copy()
                    avail_copy[opt] -= 1
                    new_path = path.copy()
                    new_path[opt] = new_path.get(opt, 0) + 1
                    res = self._allocate(avail_copy, hybrids, index + 1, generic_needed, new_path)
                    if res:
                        return res
        return None

    def can_pay(self, mana_cost: str) -> bool:
        """Return ``True`` if the pool can satisfy ``mana_cost``."""
        try:
            colours, generic, hybrids = self.parse_cost(mana_cost)
        except ValueError:
            return False

        available = self.pool.copy()
        for colour, amount in colours.items():
            if available[colour] < amount:
                return False
            available[colour] -= amount

        allocation = self._allocate(available, hybrids, 0, generic, {})
        return allocation is not None

    def pay(self, mana_cost: str) -> None:
        """Spend mana to satisfy ``mana_cost``.

        Raises
        ------
        ValueError
            If the pool does not contain enough mana.
        """
        colours, generic, hybrids = self.parse_cost(mana_cost)

        available = self.pool.copy()
        for colour, amount in colours.items():
            if available[colour] < amount:
                raise ValueError("Insufficient mana in pool")
            available[colour] -= amount

        allocation = self._allocate(available, hybrids, 0, generic, {})
        if allocation is None:
            raise ValueError("Insufficient mana in pool")

        # spend fixed colours
        for colour, amount in colours.items():
            self.spend(colour, amount)
        # spend hybrid/generic allocation
        for colour, amount in allocation.items():
            self.spend(colour, amount)

    # ------------------------------------------------------------------
    # Representation helpers
    # ------------------------------------------------------------------
    def __str__(self) -> str:  # pragma: no cover - simple repr
        return str(self.pool)

    __repr__ = __str__
