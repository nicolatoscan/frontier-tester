import argparse
import pathlib

def get_args():
    parser = argparse.ArgumentParser(
        prog='ftest',
    )
    parser.add_argument(
        '--processors', '-p',
        type=int,
        required=False,
        default=4
    )
    parser.add_argument(
        '--out',
        type=pathlib.Path,
        required=False,
        default='./results'
    )

    args, _ = parser.parse_known_args()
    return args