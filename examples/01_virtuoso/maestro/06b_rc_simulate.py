#!/usr/bin/env python3
"""Step 2: Run simulation on the RC filter Maestro setup.

Prerequisite: run 06a_rc_create.py first.
After this completes, use 06c_rc_read_results.py to read results.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from virtuoso_bridge import VirtuosoClient
from virtuoso_bridge.virtuoso.maestro import (
    open_session, close_session, run_simulation, wait_until_done,
)

LIB = "PLAYGROUND_LLM"
CELL = "TB_RC_FILTER"


def main() -> int:
    client = VirtuosoClient.from_env()
    print(f"[info] {LIB}/{CELL}")

    session = open_session(client, LIB, CELL)

    print("[sim] Running...")
    run_simulation(client, session=session)
    wait_until_done(client, timeout=600)
    print("[sim] Done")

    close_session(client, session)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
