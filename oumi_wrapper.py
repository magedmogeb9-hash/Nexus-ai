# Oumi integration wrapper (optional)
import os

def is_available():
    try:
        import oumi
        return True
    except ImportError:
        return False

def run_training(config):
    if not is_available():
        raise RuntimeError("Oumi is not installed")
    # Add Oumi training logic here
    pass
