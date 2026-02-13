import shutil
import subprocess
import sys
import textwrap
from argparse import ArgumentParser
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
ENTRYPOINT = PROJECT_ROOT / "convert.py"
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_DIR = PROJECT_ROOT
APP_NAME = "exchange-rate-bot"
OCI_BUILD_SCRIPT = PROJECT_ROOT / "build_oci_arm64.sh"
OCI_RUN_SCRIPT = PROJECT_ROOT / "run_oci_arm64.sh"
OCI_BUILD_BINARY_SCRIPT = PROJECT_ROOT / "build_oci_arm64_binary.sh"
OCI_RUN_BINARY_SCRIPT = PROJECT_ROOT / "run_oci_arm64_binary.sh"


def _run(cmd: list[str]) -> None:
    print(f"+ {' '.join(cmd)}")
    subprocess.check_call(cmd)


def _ensure_pyinstaller() -> None:
    try:
        import PyInstaller  # noqa: F401
    except Exception:
        print("PyInstaller is not installed. Installing to current environment...")
        _run([sys.executable, "-m", "pip", "install", "pyinstaller"])


def _clean() -> None:
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    spec_file = SPEC_DIR / f"{APP_NAME}.spec"
    if spec_file.exists():
        spec_file.unlink()


def _build() -> None:
    if not ENTRYPOINT.exists():
        raise FileNotFoundError(f"Entry point not found: {ENTRYPOINT}")

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--clean",
        "--name",
        APP_NAME,
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--specpath",
        str(SPEC_DIR),
        str(ENTRYPOINT),
    ]

    _run(cmd)


def _write_oci_scripts() -> None:
    build_script = textwrap.dedent(
        """\
        #!/usr/bin/env bash
        set -euo pipefail

        APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        cd "$APP_DIR"

        SUDO=""
        if command -v sudo >/dev/null 2>&1; then
          SUDO="sudo"
        fi

        if command -v apt-get >/dev/null 2>&1; then
          $SUDO apt-get update
          $SUDO apt-get install -y python3 python3-venv python3-pip
        elif command -v dnf >/dev/null 2>&1; then
          $SUDO dnf install -y python3 python3-pip python3-virtualenv || true
        elif command -v yum >/dev/null 2>&1; then
          $SUDO yum install -y python3 python3-pip python3-virtualenv || true
        else
          echo "No supported package manager found. Ensure python3 and venv are installed."
        fi

        if ! command -v python3 >/dev/null 2>&1; then
          echo "python3 not found. Install python3 and retry."
          exit 1
        fi

        python3 -m venv .venv
        source .venv/bin/activate

        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
        """
    )

    run_script = textwrap.dedent(
        """\
        #!/usr/bin/env bash
        set -euo pipefail

        APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        cd "$APP_DIR"

        if [ -f ".venv/bin/activate" ]; then
          source .venv/bin/activate
        else
          echo "Virtualenv not found. Will try system python3 instead."
          if ! command -v python3 >/dev/null 2>&1; then
            echo "python3 not found. Run ./build_oci_arm64.sh first or install python3."
            exit 1
          fi
        fi

        # Optional: provide tokens via env vars to avoid hardcoding in mytoken.py
        # export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
        # export EXCHANGE_RATE_TOKEN="your-exchange-rate-api-token"

        python3 convert.py
        """
    )

    OCI_BUILD_SCRIPT.write_text(build_script, encoding="utf-8", newline="\n")
    OCI_RUN_SCRIPT.write_text(run_script, encoding="utf-8", newline="\n")


def _write_oci_binary_scripts() -> None:
    build_script = textwrap.dedent(
        """\
        #!/usr/bin/env bash
        set -euo pipefail

        APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        cd "$APP_DIR"

        SUDO=""
        if command -v sudo >/dev/null 2>&1; then
          SUDO="sudo"
        fi

        if command -v apt-get >/dev/null 2>&1; then
          $SUDO apt-get update
          $SUDO apt-get install -y python3 python3-venv python3-pip
        elif command -v dnf >/dev/null 2>&1; then
          $SUDO dnf install -y python3 python3-pip python3-virtualenv || true
        elif command -v yum >/dev/null 2>&1; then
          $SUDO yum install -y python3 python3-pip python3-virtualenv || true
        else
          echo "No supported package manager found. Ensure python3 and venv are installed."
        fi

        if ! command -v python3 >/dev/null 2>&1; then
          echo "python3 not found. Install python3 and retry."
          exit 1
        fi

        python3 -m venv .venv
        source .venv/bin/activate

        python -m pip install --upgrade pip
        python -m pip install -r requirements.txt
        python -m pip install pyinstaller

        # Build a native aarch64 Linux binary on the instance.
        python -m PyInstaller --onefile --clean --name exchange-rate-bot convert.py
        """
    )

    run_script = textwrap.dedent(
        """\
        #!/usr/bin/env bash
        set -euo pipefail

        APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        cd "$APP_DIR"

        BIN="./dist/exchange-rate-bot"
        if [ ! -f "$BIN" ]; then
          echo "Binary not found at $BIN. Run ./build_oci_arm64_binary.sh first."
          exit 1
        fi

        # Optional: provide tokens via env vars to avoid hardcoding in mytoken.py
        # export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
        # export EXCHANGE_RATE_TOKEN="your-exchange-rate-api-token"

        "$BIN"
        """
    )

    OCI_BUILD_BINARY_SCRIPT.write_text(build_script, encoding="utf-8", newline="\n")
    OCI_RUN_BINARY_SCRIPT.write_text(run_script, encoding="utf-8", newline="\n")


def _build_pyinstaller() -> None:
    # Note: PyInstaller builds are OS-specific.
    if sys.platform.startswith("win"):
        platform_name = "Windows"
    elif sys.platform.startswith("linux"):
        platform_name = "Linux"
    elif sys.platform.startswith("darwin"):
        platform_name = "macOS"
    else:
        platform_name = sys.platform

    print(f"Building for {platform_name} using Python {sys.version.split()[0]}...")
    _ensure_pyinstaller()
    _clean()
    _build()
    print("Build complete.")
    print(f"Output: {DIST_DIR}")


def _parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Build or prepare scripts for OCI aarch64.")
    parser.add_argument(
        "--mode",
        choices=["oci", "oci-binary", "pyinstaller"],
        default="oci",
        help="Mode to run. 'oci' creates OCI scripts; 'pyinstaller' builds a one-file binary.",
    )
    return parser


def main() -> None:
    parser = _parse_args()
    args = parser.parse_args()

    if args.mode == "oci":
        _write_oci_scripts()
        print("Created OCI scripts:")
        print(f"- {OCI_BUILD_SCRIPT.name}")
        print(f"- {OCI_RUN_SCRIPT.name}")
        print("On the OCI instance, run:")
        print("  chmod +x build_oci_arm64.sh run_oci_arm64.sh")
        print("  ./build_oci_arm64.sh")
        print("  ./run_oci_arm64.sh")
        return
    if args.mode == "oci-binary":
        _write_oci_binary_scripts()
        print("Created OCI binary scripts:")
        print(f"- {OCI_BUILD_BINARY_SCRIPT.name}")
        print(f"- {OCI_RUN_BINARY_SCRIPT.name}")
        print("On the OCI instance, run:")
        print("  chmod +x build_oci_arm64_binary.sh run_oci_arm64_binary.sh")
        print("  ./build_oci_arm64_binary.sh")
        print("  ./run_oci_arm64_binary.sh")
        return

    _build_pyinstaller()


if __name__ == "__main__":
    main()
