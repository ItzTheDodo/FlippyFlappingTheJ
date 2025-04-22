from src.FFTJ import FFTJAppManager

__version__ = "DEV"

def main() -> int:
    status = FFTJAppManager(__version__).status
    return status


if __name__ == "__main__":
    _status = main()
    exit(_status)
