import os
import subprocess
import argparse

UTF8 = 'utf8'
DISK = 'F:\\'
SHARE_DIR = 'share_pdf'
SUFFIX_PDF = '.pdf'
TARGET_DIR = os.path.join(DISK, SHARE_DIR)


def gen_new_PDF(PDF):
    assert PDF.endswith(SUFFIX_PDF)
    return PDF.removesuffix(SUFFIX_PDF)


def replace_old_PDF(new_PDF, PDF):
    os.replace(new_PDF, PDF)


def update_info_utf8(PDF):
    TXT = 'doc_data.txt'
    assert os.path.exists(TXT) is False

    Info_list = [
        ('Author', 'xc'),
        ('Purpose', 'share')
    ]
    with open(TXT, 'w', encoding=UTF8) as f:
        for key, value in Info_list:
            f.write('InfoBegin\n')
            f.write('InfoKey: ' + key + '\n')
            f.write('InfoValue: ' + value + '\n')

    new_PDF = gen_new_PDF(PDF)
    subprocess.run(['pdftk', PDF, 'update_info_utf8', TXT, 'output', new_PDF]).check_returncode()
    replace_old_PDF(new_PDF, PDF)
    os.remove(TXT)


def pdftk_share(PDF, pdf_dir):
    _base = os.path.basename(PDF)

    if pdf_dir:
        assert PDF.count(pdf_dir) == 1

        lo = PDF.find(pdf_dir)
        _base = PDF[lo:]

    new_PDF = os.path.join(TARGET_DIR, _base)

    _dirname = os.path.dirname(new_PDF)
    _basename = os.path.basename(new_PDF)
    _basename = _basename.replace('-', ' ')
    new_PDF = os.path.join(_dirname, _basename)

    subprocess.run(['pdftk', PDF, 'cat', 'output', new_PDF]).check_returncode()

    update_info_utf8(new_PDF)


def get_all_files(suffix, path):
    suffix = suffix.upper()
    results = os.listdir(path)
    results = [os.path.join(path, result) for result in results]

    file_names = []
    dir_names = []
    for result in results:
        if os.path.isfile(result):
            if result.upper().endswith(suffix):
                file_names.append(result)
        elif os.path.isdir(result):
            dir_names.append(result)

    for dir_name in dir_names:
        file_names.extend(get_all_files(suffix, dir_name))

    return file_names


def get_all_dirs(path):
    dir_names = [path]

    results = os.listdir(path)
    results = [os.path.join(path, result) for result in results]
    for result in results:
        if os.path.isdir(result):
            dir_names.extend(get_all_dirs(result))

    return dir_names


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PDF file or directory')
    parser.add_argument('--pdf_file', type=str, default=None)
    parser.add_argument('--pdf_dir', type=str, default=None)
    args = parser.parse_args()

    assert os.getcwd() == 'F:\\BaiduNetdiskWorkspace'

    assert os.path.exists(TARGET_DIR) and os.path.isdir(TARGET_DIR)

    assert not (args.pdf_file and args.pdf_dir)
    assert not ((not args.pdf_file) and (not args.pdf_dir))

    if args.pdf_file:
        args.pdf_file = os.path.normpath(args.pdf_file)
    if args.pdf_dir:
        args.pdf_dir = os.path.normpath(args.pdf_dir)

    all_PDF = []
    if args.pdf_file:
        assert args.pdf_file.endswith(SUFFIX_PDF)
        assert os.path.isfile(args.pdf_file)
        all_PDF = [args.pdf_file]
    else:
        assert os.path.isdir(args.pdf_dir)
        all_PDF = get_all_files(SUFFIX_PDF, args.pdf_dir)

    assert len(all_PDF) != 0

    if args.pdf_dir:
        _pdf_dir = os.path.basename(args.pdf_dir)
        _share_dir = os.path.join(TARGET_DIR, _pdf_dir)
        assert not os.path.exists(_share_dir)

        all_dirs = get_all_dirs(args.pdf_dir)
        for _dir in all_dirs:
            _share_dir = os.path.join(TARGET_DIR, _dir)
            os.makedirs(_share_dir)

    for PDF in all_PDF:
        pdftk_share(PDF, args.pdf_dir)
