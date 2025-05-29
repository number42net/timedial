"""TimeDial project.

Copyright (c) Martin Miedema
Repository: https://github.com/number42net/timedial

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import gzip
import os
import shutil
import sys
from glob import glob

SIMULATOR_DIR = "/opt/simh"
SIZE_LIMIT = 20 * 1024 * 1024  # 20 MB


def prepare(simulator: str) -> None:
    """Prepares a simulator environment by copying and decompressing necessary files.

    This function copies all files from the simulator's source directory to the user's
    home directory if they are not already present. Gzipped files are automatically
    decompressed unless an uncompressed version already exists.

    Args:
        simulator (str): The name of the simulator to prepare.

    Raises:
        SystemExit: If the specified simulator directory does not exist.
    """
    source = os.path.join(SIMULATOR_DIR, simulator)
    if not os.path.isdir(source):
        print(f"Simulator {simulator} does not exist!")
        sys.exit(1)

    destination = os.path.expanduser(f"~/{simulator}")
    destination_glob = glob(destination + "/**", recursive=True)
    gzipped_rel_paths = {os.path.relpath(f, destination)[:-3] for f in destination_glob if f.lower().endswith(".gz")}

    # Copy the files from the simulator source.
    for s_path in glob(source + "/**", recursive=True):
        d_path = os.path.join(destination, os.path.relpath(s_path, source))
        if os.path.isfile(d_path):
            # If the file already exists
            continue
        if os.path.isdir(s_path):
            continue
        if os.path.relpath(s_path, source) in gzipped_rel_paths:
            # If a gzipped version of the file exists
            continue
        if s_path.lower().endswith(".gz") and os.path.isfile(d_path[:-3]):
            # If a gunzipped version of the file exists
            continue
        if s_path.lower().endswith(".gz"):
            try:
                os.makedirs(os.path.dirname(d_path), exist_ok=True)
                with gzip.open(s_path, "rb") as f_in, open(d_path[:-3], "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
                continue
            except Exception as exc:
                print(f"Warning: Failed to decompress: {s_path} - {exc}")
                continue

        try:
            os.makedirs(os.path.dirname(d_path), exist_ok=True)
            shutil.copy2(s_path, d_path)
        except Exception as exc:
            print(f"Warning: Failed to copy: {s_path} - {exc}")

    # Uncompress any remaining files in the destination
    for gz_path in glob(destination + "/**", recursive=True):
        if not os.path.isfile(gz_path):
            continue
        if not gz_path.lower().endswith(".gz"):
            continue

        print(f"Uncompressing: {gz_path}")
        try:
            with gzip.open(gz_path, "rb") as f_in, open(gz_path[:-3], "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(gz_path)
        except Exception as exc:
            print(f"Warning: Failed to decompress remaining: {gz_path} - {exc}")


def gzip_large_files(simulator: str) -> None:
    """Compresses large files in the simulator's directory using gzip.

    Files larger than a predefined size threshold are compressed unless a compressed
    version already exists. Original files are deleted after compression.

    Args:
        simulator (str): The name of the simulator to process.
    """
    destination = os.path.expanduser(f"~/{simulator}")
    for file_path in glob(destination + "/**", recursive=True):
        if not os.path.isfile(file_path):
            continue
        if file_path.lower().endswith(".gz"):
            continue
        if os.path.isfile(file_path + ".gz"):
            print(f"Warning: {file_path + '.gz'} already exists! Consider deleting or renaming it so we can safe space")
        if os.path.getsize(file_path) <= SIZE_LIMIT:
            continue

        try:
            with open(file_path, "rb") as f_in, gzip.open(file_path + ".gz", "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
            os.remove(file_path)
        except Exception as exc:
            print(f"Warning, failed to compress: {file_path} - {exc}")


def run_simulator(simulator: str) -> None:
    """Displays login instructions and starts the simulator.

    Args:
        simulator (str): The name of the simulator to run.
    """
    destination = os.path.expanduser(f"~/{simulator}")
    login_info = os.path.join(destination, "login-info.txt")
    if os.path.join(destination, "login-info.txt"):
        with open(login_info) as file:
            text = file.read()

    print()
    print(text.strip())
    input("\nPress enter to start simulator...")
    print()
    os.system(f"cd {destination}; ./start")


def main() -> None:
    """Main entry point for the simulator preparation script.

    Parses the simulator name from command-line arguments, prepares its environment,
    starts it, and compresses large files afterward.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("simulator", type=str, help="Name of the simulator")

    args = parser.parse_args()
    print("Preparing simulator...")
    prepare(args.simulator)
    run_simulator(args.simulator)
    print()
    print("Compressing disk images to save space...")
    gzip_large_files(args.simulator)


if __name__ == "__main__":
    main()
