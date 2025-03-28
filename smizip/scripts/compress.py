import sys
import time
import json
import argparse

from smizip import SmiZip

def parse_args():
    parser = argparse.ArgumentParser(description="Compress or decompress a SMILES file")
    parser.add_argument("-i", "--input", help="Input file", required=True)
    parser.add_argument("-o", "--output", help="Output file (default is stdout)")
    parser.add_argument("-n", "--ngrams", help="JSON file containing ngrams", required=True)
    parser.add_argument("-d", "--decompress", action="store_true", help="Decompress (the default is compress)")
    # parser.add_argument("-j", "--ncpus", help="Number of CPUs (default is 1)")
    # parser.add_argument("--no-preserve-order", action="store_true", help="Do NOT require that line order is preserved. This may enable the conversion to run faster.")
    args = parser.parse_args()
    return args

def decompress(args, zipper):
    out = open(args.output, "w") if args.output else sys.stdout
    with open(args.input, "rb") as inp:
        for line in inp:
            smi, title = line.split(b"\t")
            title = title.decode("ascii")
            unzipped = zipper.unzip(smi)
            out.write(f"{unzipped}\t{title}")

def compress(args, zipper):
    out = open(args.output, "wb") if args.output else sys.stdout.buffer
    with open(args.input) as inp:
        for line in inp:
            broken = line.split(maxsplit=1)
            if len(broken) == 1:
                smi = broken[0]
                zipped = zipper.zip(smi.rstrip())
                out.write(zipped)
                out.write(b'\n')
            else:
                smi, title = broken
                zipped = zipper.zip(smi)
                out.write(zipped)
                out.write(b"\t")
                out.write(title.encode("ascii"))

def main():
    args = parse_args()
    with open(args.ngrams) as inp:
        ngrams = json.load(inp)['ngrams']
    for x in "\t\n":
        if x not in ngrams:
            sys.exit(f"ERROR: This script requires {repr(x)} to be included in the list of n-grams")

    zipper = SmiZip(ngrams)


    t = time.time()
    if args.decompress:
        decompress(args, zipper)
    else:
        compress(args, zipper)
    print(f"Elapsed time: {time.time() - t:.1f}s")

if __name__ == "__main__":
    main()
