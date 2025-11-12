"""Utility script for inspecting saved LangGraph checkpoints."""

import json

from workflows.Jokestruc.graph import _memory


def main() -> None:
    """Print saved checkpoint state for a hardcoded thread ID."""
    thread_id = "696bbc19-c754-47c3-bb56-7e0c3abfffc2"
    snapshots = list(_memory.list({"configurable": {"thread_id": thread_id}}))

    if not snapshots:
        print(f"No checkpoints found for thread {thread_id}.")
        print("Available threads:", list(_memory.storage.keys()))
        return

    for idx, snap in enumerate(snapshots, start=1):
        print(f"\nCheckpoint {idx} (thread {snap.config['thread_id']}):")
        print(json.dumps(snap.checkpoint.state, indent=2))


if __name__ == "__main__":
    main()
