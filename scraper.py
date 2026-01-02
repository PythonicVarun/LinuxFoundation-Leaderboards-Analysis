import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Optional

import requests

ranked_api_link = "https://insights.linuxfoundation.org/api/leaderboard?maxRank={0}"
paged_api_link = (
    "https://insights.linuxfoundation.org/api/leaderboard?page=0&pageSize={0}"
)
dataset_path = Path(__file__).parent / "datasets"

os.makedirs(dataset_path, exist_ok=True)


def get_total_entries():
    response = requests.get(paged_api_link.format(1))
    response.raise_for_status()
    data = response.json()
    print(f"Total entries available: {data['total']}")
    return int(data["total"])


def fetch_full_data(total_entries: Optional[int] = None):
    leaderboards = defaultdict(list)
    response = requests.get(paged_api_link.format(total_entries or get_total_entries()))
    response.raise_for_status()
    data = response.json()
    for e in data["data"]:
        leaderboards[e["leaderboardType"]].append(e)

    print(f"Found total entries: {len(data['data'])}")
    return leaderboards, "full"


def fetch_n_rank_data(n: int = 100):
    response = requests.get(ranked_api_link.format(n))
    response.raise_for_status()

    data = response.json()
    leaderboards = defaultdict(list)
    for e in data["data"]:
        leaderboards[e["leaderboardType"]].append(e)

    print(f"Found total entries: {len(data['data'])}")
    print(f"Found leaderboard types: {list(leaderboards.keys())} ({len(leaderboards)})")
    return leaderboards, f"top_{n}"


def save_leaderboards(leaderboards: defaultdict, suffix: str):
    for lb_type, entries in leaderboards.items():
        print(f"Leaderboard Type: {lb_type}, Entries: {len(entries)}")
        with open(dataset_path / f"{lb_type}_{suffix}.json", "w") as f:
            json.dump(entries, f)


if __name__ == "__main__":
    leaderboards, suffix = fetch_full_data()
    save_leaderboards(leaderboards, suffix)
