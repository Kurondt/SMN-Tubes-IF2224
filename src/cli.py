import argparse
from pathlib import Path

def parse_args():
    ap = argparse.ArgumentParser(description="Pascal-S Compiler \"SayMyName\" (only lexer yet)")
    ap.add_argument("source", type=Path, help=".pas source file")
    ap.add_argument("--dfa", type=Path, default=Path(__file__).parent / "rules" / "dfa.json")
    return ap.parse_args()
