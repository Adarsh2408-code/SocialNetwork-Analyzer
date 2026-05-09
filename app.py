"""
Social Network Analyzer - app.py
=================================
A unified command-line application that brings together all four modules:
  1. Data Cleaning       (cleandata.ipynb)
  2. Display Data        (displaydata.ipynb)
  3. People You May Know (peopleyoumayknow.ipynb)
  4. Pages You Might Like (pagesyoumightlike.ipynb)

Usage:
    python app.py
    python app.py --data data.json
    python app.py --data massive_data.json
"""

import json
import os
import argparse
from collections import defaultdict


# ──────────────────────────────────────────────
# MODULE 1 — Data Loading
# ──────────────────────────────────────────────

def load_data(filepath: str) -> dict:
    """Load and return JSON data from the given file path."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data file not found: {filepath}")
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


# ──────────────────────────────────────────────
# MODULE 2 — Data Cleaning
# ──────────────────────────────────────────────

def clean_data(data: dict) -> dict:
    """
    Clean and normalise raw social network JSON data.

    Steps performed:
      - Remove users with missing or blank names
      - Deduplicate each user's friends list
      - Remove inactive users (no friends AND no liked pages)
      - Deduplicate pages by ID (keep first occurrence)
    """
    cleaned_users = []
    for user in data.get("users", []):
        # Skip users with missing or blank names
        name = user.get("name", "").strip()
        if not name:
            continue

        # Deduplicate friends
        friends = list(dict.fromkeys(user.get("friends", [])))

        # Deduplicate liked pages
        liked_pages = list(dict.fromkeys(user.get("liked_pages", [])))

        # Skip inactive users
        if not friends and not liked_pages:
            continue

        cleaned_users.append({
            "id": user["id"],
            "name": name,
            "friends": friends,
            "liked_pages": liked_pages,
        })

    # Deduplicate pages by ID
    seen_page_ids = set()
    cleaned_pages = []
    for page in data.get("pages", []):
        if page["id"] not in seen_page_ids:
            seen_page_ids.add(page["id"])
            cleaned_pages.append(page)

    return {"users": cleaned_users, "pages": cleaned_pages}


# ──────────────────────────────────────────────
# MODULE 3 — Display Data
# ──────────────────────────────────────────────

def display_data(data: dict) -> None:
    """Pretty-print a summary of all users and pages in the dataset."""
    users = data.get("users", [])
    pages = data.get("pages", [])

    # Build a quick page-id → name lookup
    page_lookup = {p["id"]: p["name"] for p in pages}

    print(f"\n{'='*50}")
    print(f"  SOCIAL NETWORK SUMMARY")
    print(f"{'='*50}")
    print(f"  Total users : {len(users)}")
    print(f"  Total pages : {len(pages)}")
    print(f"{'='*50}\n")

    print("── USERS ──────────────────────────────────────")
    for user in users:
        friend_names = [
            next((u["name"] for u in users if u["id"] == fid), f"ID:{fid}")
            for fid in user.get("friends", [])
        ]
        liked_names = [
            page_lookup.get(pid, f"PageID:{pid}")
            for pid in user.get("liked_pages", [])
        ]
        print(f"\n  [{user['id']}] {user['name']}")
        print(f"      Friends     : {', '.join(friend_names) if friend_names else 'None'}")
        print(f"      Liked pages : {', '.join(liked_names) if liked_names else 'None'}")

    print("\n── PAGES ───────────────────────────────────────")
    for page in pages:
        print(f"  [{page['id']}] {page['name']}")
    print()


# ──────────────────────────────────────────────
# MODULE 4 — People You May Know
# ──────────────────────────────────────────────

def find_people_you_may_know(user_id: int, data: dict) -> list:
    """
    Suggest friends-of-friends for the given user_id.

    Algorithm:
      1. Find user's direct friends.
      2. For each friend, iterate their friends (friends-of-friends).
      3. Exclude the user themselves and anyone already a direct friend.
      4. Count mutual friends per candidate and rank by count (descending).

    Returns a list of (user_id, mutual_count) tuples, highest first.
    Returns [] if user_id not found.
    """
    users = data.get("users", [])
    user_map = {u["id"]: u for u in users}

    if user_id not in user_map:
        return []

    direct_friends = set(user_map[user_id].get("friends", []))
    mutual_count: dict = defaultdict(int)

    for friend_id in direct_friends:
        friend = user_map.get(friend_id)
        if not friend:
            continue
        for fof_id in friend.get("friends", []):
            if fof_id != user_id and fof_id not in direct_friends:
                mutual_count[fof_id] += 1

    suggestions = sorted(mutual_count.items(), key=lambda x: x[1], reverse=True)
    return suggestions


# ──────────────────────────────────────────────
# MODULE 5 — Pages You Might Like
# ──────────────────────────────────────────────

def find_pages_you_might_like(user_id: int, data: dict) -> list:
    """
    Recommend pages for the given user_id.

    Algorithm:
      1. Find all pages already liked by the user.
      2. For every other user V, count shared liked pages with the target user.
      3. For each page liked by V but not by the target user,
         add the shared-page count to that page's score.
      4. Return pages sorted by score (descending).

    Returns a list of (page_id, score) tuples, highest first.
    Returns [] if user_id not found.
    """
    users = data.get("users", [])
    user_map = {u["id"]: u for u in users}

    if user_id not in user_map:
        return []

    user_liked = set(user_map[user_id].get("liked_pages", []))
    page_scores: dict = defaultdict(int)

    for other in users:
        if other["id"] == user_id:
            continue
        other_liked = set(other.get("liked_pages", []))
        shared = user_liked & other_liked
        if not shared:
            continue
        for page_id in other_liked - user_liked:
            page_scores[page_id] += len(shared)

    recommendations = sorted(page_scores.items(), key=lambda x: x[1], reverse=True)
    return recommendations


# ──────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────

def resolve_user_names(suggestions: list, data: dict) -> list:
    """Replace user IDs in suggestion tuples with (name, count) tuples."""
    user_map = {u["id"]: u["name"] for u in data.get("users", [])}
    return [(user_map.get(uid, f"ID:{uid}"), count) for uid, count in suggestions]


def resolve_page_names(recommendations: list, data: dict) -> list:
    """Replace page IDs in recommendation tuples with (name, score) tuples."""
    page_map = {p["id"]: p["name"] for p in data.get("pages", [])}
    return [(page_map.get(pid, f"PageID:{pid}"), score) for pid, score in recommendations]


def pick_user(data: dict) -> int | None:
    """Interactively prompt the user to pick a user ID from the dataset."""
    users = data.get("users", [])
    if not users:
        print("  No users found in dataset.")
        return None

    print("\n  Available users:")
    for u in users:
        print(f"    [{u['id']}] {u['name']}")

    try:
        uid = int(input("\n  Enter user ID: ").strip())
        if uid not in {u["id"] for u in users}:
            print(f"  User ID {uid} not found.")
            return None
        return uid
    except ValueError:
        print("  Invalid input. Please enter a numeric ID.")
        return None


# ──────────────────────────────────────────────
# CLI MENU
# ──────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════╗
║      🌐  Social Network Analyzer     ║
╠══════════════════════════════════════╣
║  1. Display all users & pages        ║
║  2. Clean the dataset                ║
║  3. People You May Know              ║
║  4. Pages You Might Like             ║
║  5. Switch data file                 ║
║  0. Exit                             ║
╚══════════════════════════════════════╝
"""


def run_app(data_file: str) -> None:
    print(f"\n  Loading data from '{data_file}' ...")
    try:
        data = load_data(data_file)
    except FileNotFoundError as e:
        print(f"  ✗ {e}")
        return

    print(f"  ✓ Loaded {len(data.get('users', []))} users, "
          f"{len(data.get('pages', []))} pages.")

    while True:
        print(MENU)
        choice = input("  Select option: ").strip()

        if choice == "1":
            display_data(data)

        elif choice == "2":
            cleaned = clean_data(data)
            removed_users = len(data.get("users", [])) - len(cleaned["users"])
            removed_pages = len(data.get("pages", [])) - len(cleaned["pages"])
            data = cleaned
            print(f"\n  ✓ Cleaning complete.")
            print(f"    Removed users : {removed_users}")
            print(f"    Removed pages : {removed_pages}")
            print(f"    Remaining     : {len(data['users'])} users, "
                  f"{len(data['pages'])} pages")

        elif choice == "3":
            uid = pick_user(data)
            if uid is None:
                continue
            suggestions = find_people_you_may_know(uid, data)
            named = resolve_user_names(suggestions, data)
            user_name = next(u["name"] for u in data["users"] if u["id"] == uid)
            print(f"\n  👥 People {user_name} may know:")
            if named:
                for i, (name, mutual) in enumerate(named, 1):
                    print(f"    {i}. {name}  ({mutual} mutual friend{'s' if mutual != 1 else ''})")
            else:
                print("    No suggestions found.")

        elif choice == "4":
            uid = pick_user(data)
            if uid is None:
                continue
            recs = find_pages_you_might_like(uid, data)
            named = resolve_page_names(recs, data)
            user_name = next(u["name"] for u in data["users"] if u["id"] == uid)
            print(f"\n  👍 Pages {user_name} might like:")
            if named:
                for i, (name, score) in enumerate(named, 1):
                    print(f"    {i}. {name}  (score: {score})")
            else:
                print("    No recommendations found.")

        elif choice == "5":
            new_file = input("  Enter path to data file: ").strip()
            try:
                data = load_data(new_file)
                data_file = new_file
                print(f"  ✓ Switched to '{data_file}' — "
                      f"{len(data.get('users', []))} users, "
                      f"{len(data.get('pages', []))} pages.")
            except FileNotFoundError as e:
                print(f"  ✗ {e}")

        elif choice == "0":
            print("\n  Goodbye! 👋\n")
            break

        else:
            print("  Invalid option. Please choose 0–5.")


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Social Network Analyzer — interactive CLI"
    )
    parser.add_argument(
        "--data",
        default="data.json",
        help="Path to the JSON data file (default: data.json)",
    )
    args = parser.parse_args()
    run_app(args.data)


if __name__ == "__main__":
    main()
