# fuzz/fuzz_parseqs.py
import sys, atheris, urllib.parse

def test_one_input(data: bytes):
    # swap this later to call into your own parsing/util functions
    s = data.decode("utf-8", errors="ignore")
    try:
        urllib.parse.parse_qs(s)
    except Exception:
        # Crashes will still surface; we ignore expected parser exceptions
        pass

def main():
    atheris.Setup(sys.argv, test_one_input)
    atheris.Fuzz()

if __name__ == "__main__":
    main()
