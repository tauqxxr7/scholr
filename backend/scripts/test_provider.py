import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents._generation import run_provider_smoke_test


async def main() -> None:
    result = await run_provider_smoke_test()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
