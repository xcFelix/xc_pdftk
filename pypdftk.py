import os
import subprocess
import json
import argparse

SUFFIX_PDF = '.pdf'
SUFFIX_JSON = '.json'
SUFFIX_TXT = '.txt'
DOT = '.'
UTF8 = 'utf8'
PAGE = 'page'
JSON_DIR = '0 bookmarks_JSON'


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


def gen_new_PDF(PDF):
    assert PDF.endswith(SUFFIX_PDF)
    return PDF.removesuffix(SUFFIX_PDF)


def replace_old_PDF(new_PDF, PDF):
    os.replace(new_PDF, PDF)


def pdftk_cat_1_end(PDF):
    new_PDF = gen_new_PDF(PDF)
    # Let page labels comply with the page number
    subprocess.run(['pdftk', PDF, 'cat', '1-end', 'output', new_PDF]).check_returncode()
    replace_old_PDF(new_PDF, PDF)


def extract_title_list(data, level):
    # example
    example = {
        "data": [
            {
                "chapter 01": {
                    "page": 1,
                    "data": [
                        {
                            "unit 01": {
                                "page": 2
                            }
                        },
                        {
                            "unit 02": {
                                "page": 3
                            }
                        }
                    ]
                }
            },
            {
                "chapter 02": {
                    "page": 5,
                    "data": [
                        {
                            "unit 03": {
                                "page": 5
                            }
                        },
                        {
                            "unit 04": {
                                "page": 5
                            }
                        }
                    ]
                }
            }
        ]
    }
    # // example

    bookmark_list = []
    # (page, level, title)

    for d in data:
        for title in d:
            dd = d[title]
            bookmark_list.append((dd['page'], level, title))
            bookmark_list.extend(extract_title_list(dd.get('data', []), level + 1))

    return bookmark_list


def pdftk_update_info_utf8(PDF, JSON):
    with open(JSON, encoding=UTF8) as f:
        title_dict = json.load(f)

    bookmark_list = extract_title_list(title_dict.get('data', []), 1)

    TXT = 'bookmarks.txt'
    assert os.path.exists(TXT) is False
    
    with open(TXT, 'w', encoding=UTF8) as f:
        for page, level, title in bookmark_list:
            f.write('BookmarkBegin\n')
            f.write('BookmarkTitle: ' + title + '\n')
            f.write('BookmarkLevel: ' + str(level) + '\n')
            f.write('BookmarkPageNumber: ' + str(page) + '\n')

    new_PDF = gen_new_PDF(PDF)
    subprocess.run(['pdftk', PDF, 'update_info_utf8', TXT, 'output', new_PDF]).check_returncode()
    replace_old_PDF(new_PDF, PDF)
    os.remove(TXT)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PDF file or directory')
    parser.add_argument('--pdf_file', type=str, default=None)
    parser.add_argument('--pdf_dir', type=str, default=None)
    parser.add_argument('--cat', type=bool, default=False)
    parser.add_argument('--json_dir', type=str, default=JSON_DIR)
    args = parser.parse_args()

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

    all_PDF = [os.path.normpath(PDF) for PDF in all_PDF]

    all_JSON = get_all_files(SUFFIX_JSON, args.json_dir)
    all_JSON = [os.path.normpath(JSON) for JSON in all_JSON]

    basename_JSON2JSON = {
        os.path.basename(JSON): JSON for JSON in all_JSON
    }

    for PDF in all_PDF:
        if args.cat:
            pdftk_cat_1_end(PDF)

        JSON = gen_new_PDF(PDF) + SUFFIX_JSON
        basename_JSON = os.path.basename(JSON)
        if basename_JSON in basename_JSON2JSON:
            pdftk_update_info_utf8(PDF, basename_JSON2JSON[basename_JSON])
