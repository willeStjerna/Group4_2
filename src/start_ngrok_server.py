"""
Ngrok Server Module

This module manages the setup and execution of an ngrok tunnel
for exposing the local Flask server to the internet. It handles
configuration loading, tunnel establishment, and process cleanup.

Functions:
    start_ngrok_server: Initializes and manages ngrok tunnel and Flask server

Configuration:
    Requires a config.json file in the project root with:
    - ngrok_hostname: Static domain
    - port: Port number for the server
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import platform
import textwrap
import subprocess
from pyngrok import ngrok
from src.server import app  # Import the Flask "app" from server.py


def start_ngrok_server():
    """
    Start a ngrok tunnel and Flask server based on configuration settings.

    This function sets up a ngrok tunnel and starts a Flask application server. It retrieves hostname and port
    from a JSON file located in the parent directory. The function
    ensures proper cleanup of the ngrok process after termination.

    The configuration file must be named 'config.json' and should reside in the
    parent directory of the current file following this format:

        {
            "ngrok_hostname": "feasible-robin-vaguely.ngrok-free.app",
            "port": 8004
        }

        Alternativly one can set the hostname to "random" to have ngrok choose one for you.

        {
            "ngrok_hostname": "random",
            "port": 8004
        }

    Returns:
        none

    """

    # Compute path to config.json in the parent directory
    config_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "config.json")
    )

    config_text_example = textwrap.dedent("""\
        Create a file called config.json in the root of the project (not inside src/) that includes:
            - ngrok_hostname (either a static domain or just the word "random" if you want ngrok to choose one for you)
            - port
                
        Example 1: static domain
        {
            "ngrok_hostname": "feasible-robin-vaguely.ngrok-free.app",
            "port": 8004
        }
        
        Example 2: Let ngrok create a random domain for you:
        {
            "ngrok_hostname": "random",
            "port": 8004
        }
        """)

    # Attempt to parse the config file
    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

        hostname = config.get("ngrok_hostname")
        port = config.get("port")

        # Check it's correct
        if not hostname or not port:
            print("ERROR: The config.json file is missing 'ngrok_hostname' or 'port'.\n" + config_text_example)
            sys.exit(1)
    except:
        print("ERROR: config.json is missing or invalid.\n" + config_text_example)
        sys.exit(1)

    tunnel = None
    try:
        # Start ngrok
        if hostname == "random":
            tunnel = ngrok.connect(addr=port)
        else:
            tunnel = ngrok.connect(addr=port, hostname=hostname)
        print(f"ngrok tunnel established at: {tunnel.public_url}")

        # Start flask server
        app.run(port=port, use_reloader=False)

    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    finally:
        if tunnel is not None:
            # Make sure ngrok dies, but if its dead just suppress the error
            ngrok.kill()
            os_name = platform.system()
            try:
                if os_name == "Windows":
                    subprocess.run(
                        ["taskkill", "/F", "/IM", "ngrok.exe"],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                elif os_name in ["Linux", "Darwin"]:
                    subprocess.run(
                        ["pkill", "-f", "ngrok"],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
            except subprocess.CalledProcessError:
                pass


if __name__ == '__main__':
    start_ngrok_server()