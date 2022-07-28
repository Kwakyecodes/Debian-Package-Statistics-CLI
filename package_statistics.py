"""Helper function that can be used to execute the command line tool"""

import sys
sys.path.append("cli_tools")  # So that this file can access the exceptions module

from cli_tool import cli_func


if __name__ == "__main__":
    cli_func()