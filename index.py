import os
import sys

# This tells Vercel how to find and run your Streamlit app
from streamlit.web.cli import main

if __name__ == "__main__":
    # We point it to your 'app.py' file
    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        "--server.port",
        "8080",
        "--server.address",
        "0.0.0.0",
    ]
    sys.exit(main())
