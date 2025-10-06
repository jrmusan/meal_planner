#!/usr/bin/env python3
#!/usr/bin/env python3
"""
utility_scripts/import-ingredients.py

Reads a comma-separated list of ingredient names from a file and inserts
them into the ingredients table using the existing services.ingredient.Ingredent
class.

Usage examples:
  ./utility_scripts/import-ingredients.py ingredients.txt
  ./utility_scripts/import-ingredients.py -c "Produce" ingredients.txt
  ./utility_scripts/import-ingredients.py --dry-run ingredients.txt

The script skips blank lines, duplicate ingredient names (case-insensitive),
and names that contain profanity (uses better_profanity.profanity).
"""

from __future__ import annotations

import argparse
import re
from typing import Iterable, Set

from better_profanity import profanity

from services.ingredient import Ingredent


def normalize_name(name: str) -> str:
    """Normalize ingredient names the same way the app does before comparing.

    Removes non-alphanumeric characters (but keeps whitespace) and lowercases.
    """
    letter_cleanup = re.compile(r"[^a-zA-Z0-9\s]")
    cleaned = letter_cleanup.sub('', name).strip()
    return cleaned.lower()


def parse_input_lines(text: str) -> Iterable[str]:
    """Given raw text, yield candidate ingredient names.

    Accepts comma-separated and/or newline separated input.
    """
    # First split on newlines, then split each line on commas
    for line in text.splitlines():
        if not line:
            continue
        parts = [p.strip() for p in line.split(',') if p.strip()]
        for p in parts:
            yield p


def load_existing_names() -> Set[str]:
    """Return a set of normalized existing ingredient names from DB."""
    existing = Ingredent.list_ingredients()
    return {normalize_name(ing.name) for ing in existing}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Import comma-separated ingredients')
    parser.add_argument('file', help='Path to a file containing comma-separated ingredient names')
    parser.add_argument('-c', '--category', default='', help='Category to assign to each imported ingredient')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be imported without writing to the database')

    args = parser.parse_args(argv)

    # Read input file (stdin support removed)
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            raw = f.read()
    except Exception as e:
        print(f"ERROR: Failed to read {args.file}: {e}")
        return 2

    candidate_names = list(parse_input_lines(raw))
    if not candidate_names:
        print('No ingredient names found in input.')
        return 0

    existing = load_existing_names()

    to_add = []
    for name in candidate_names:
        normalized = normalize_name(name)
        if not normalized:
            print(f"Skipping blank/invalid name: '{name}'")
            continue
        if profanity.contains_profanity(name):
            print(f"Skipping profane ingredient: '{name}'")
            continue
        if normalized in existing or normalized in {normalize_name(n) for n in to_add}:
            print(f"Skipping duplicate: '{name}'")
            continue
        to_add.append(name)

    if not to_add:
        print('No new ingredients to add.')
        return 0

    print(f"Preparing to add {len(to_add)} ingredient(s): {', '.join(to_add)}")
    if args.dry_run:
        print('Dry run enabled - no changes will be made.')
        return 0

    # Insert into DB
    for name in to_add:
        try:
            ing = Ingredent(name.strip(), category=args.category)
            ing.insert_ingredient()
            print(f"Added: {name} (category='{args.category}')")
        except Exception as e:
            print(f"ERROR adding '{name}': {e}")

    print('Import complete.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
if __name__ == '__main__':

    raise SystemExit(main())
