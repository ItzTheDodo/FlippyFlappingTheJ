from src.FFTJ import FFTJAppManager

__version__ = "DEV"

# "current_file": "C:\\Users\\User\\OneDrive\\Documents\\Applications\\FlippyFlappingTheJ\\assets\\example.automaton"
# "current_file": "/Users/aiden/Library/CloudStorage/OneDrive-Personal/Documents/Applications/FlippyFlappingTheJ/assets/example.automaton"


def main() -> int:
    status = FFTJAppManager(__version__).status
    return status


if __name__ == "__main__":
    _status = main()
    exit(_status)
