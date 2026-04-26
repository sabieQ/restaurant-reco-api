import sys


def main() -> int:
    major, minor = sys.version_info.major, sys.version_info.minor
    if (major, minor) != (3, 11):
        print(f"FAIL: Python 3.11 required, found {major}.{minor}")
        return 1
    print(f"OK: Python {major}.{minor} runtime pin satisfied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
