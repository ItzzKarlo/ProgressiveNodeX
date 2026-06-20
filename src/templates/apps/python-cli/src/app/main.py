import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="A ProgressiveNodeX generated Python CLI.")
    parser.add_argument("--name", default="PNX", help="Name to greet.")
    args = parser.parse_args()

    print(f"Hello, {args.name}!")


if __name__ == "__main__":
    main()