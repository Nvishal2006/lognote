import sys
import argparse
from .cli import render_trace

def main():
    parser = argparse.ArgumentParser(description="Lognote Time-Travel CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    view_parser = subparsers.add_parser("view", help="View a lognote trace file")
    view_parser.add_argument("file", help="Path to the JSON trace file")
    
    args = parser.parse_args()
    
    if args.command == "view":
        render_trace(args.file)

if __name__ == "__main__":
    main()
