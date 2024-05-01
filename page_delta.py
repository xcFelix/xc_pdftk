import os
import argparse


PAGE = 'page'
SUFFIX_BAK = '.bak'


def process(line, delta):
    cnt = line.count(PAGE)
    if cnt == 0:
        return line

    assert cnt == 1

    ix = line.index(PAGE)
    ix += 4
    length = len(line)

    lo = hi = -1
    while ix < length:
        if line[ix].isnumeric():
            if lo == -1:
                lo = ix
        else:
            if lo != -1:
                hi = ix
                break
        ix += 1

    if hi == -1:
        hi = length

    assert lo != -1 and hi != -1

    s_old = line[lo:hi]
    s_new = str(int(s_old) + delta)

    assert line.count(s_old) == 1

    return line.replace(s_old, s_new)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Add an increment of <delta> to the page number.')
    parser.add_argument('--json_file', type=str, default=None)
    parser.add_argument('--delta', type=int, default=None)
    args = parser.parse_args()

    assert args.json_file and args.delta

    results = []
    with open(args.json_file, encoding='utf-8') as f:
        for line in f:
            results.append(process(line, args.delta))

    tmp_json_file = args.json_file + SUFFIX_BAK
    with open(tmp_json_file, encoding='utf-8', mode='w') as f:
        f.writelines(results)

    os.replace(tmp_json_file, args.json_file)
