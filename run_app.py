import asyncio
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import sys
from streamlit.web import cli

if __name__ == "__main__":
    sys.argv = ["streamlit", "run", "app.py", "--server.port", "8502"]
    sys.exit(cli.main())
