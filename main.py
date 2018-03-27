#!/usr/bin/env python3

import argparse
import magic
import mimetypes

from polyglot_detector import PolyglotLevel, scan as polyglot_scan

MAGIC = None
""":type MAGIC: magic.Magic"""

OCTET_STREAM_MIME = 'application/octet-stream'


def magic_scan(filename):
    """Scan for a single file type with libmagic"""
    results = []
    file_mimes = MAGIC.file(filename)
    for file_mime in file_mimes.split('\012- '):
        if file_mime != OCTET_STREAM_MIME:
            extension = mimetypes.guess_extension(file_mime)
            if extension is not None:
                results.append(extension[1:])
    return results


def scan(filename, scan_with_magic=False):
    results = polyglot_scan(filename)
    if scan_with_magic:
        for ext in magic_scan(filename):
            results[ext] = results.get(ext, PolyglotLevel.VALID)
    return results


def display_results(results: [(str, {})], indent=False):
    for result in results.items():
        if indent:
            print('\t', end='')
        print('%s: %s' % (result[0], result[1]))


def create_arg_parser():
    arg_parser = argparse.ArgumentParser(prog='polyglot-detector',
                                         description='A tool to detect polyglot in common formats')
    arg_parser.add_argument('files', type=str, nargs='+', help='File to scan')
    arg_parser.add_argument('-m', '--magic', dest='magic', action='store_true', help='Scan with libmagic')
    arg_parser.add_argument('--magic-continue', dest='magic_continue', action='store_true',
                            help='Use the flag MAGIC_CONTINUE with libmagic. Implies --magic')
    arg_parser.add_argument('--magic-file', dest='magic_file', type=str,
                            help='Specify the magic file to use. Implies --magic')
    return arg_parser


def configure_libmagic(magic_continue=False, magic_file=None):
    global MAGIC
    MAGIC = magic.open(magic.MAGIC_MIME_TYPE
                       | ((magic.MAGIC_CONTINUE | magic.MAGIC_RAW) if magic_continue else magic.MAGIC_NONE))
    MAGIC.load(magic_file)


def main():
    arg_parser = create_arg_parser()
    args = arg_parser.parse_args()

    # `magic_continue` and `magic_file` implies `magic`
    args.magic = args.magic or args.magic_continue or args.magic_file

    # Configure libmagic
    if args.magic:
        configure_libmagic(magic_continue=args.magic_continue, magic_file=args.magic_file)

    if len(args.files) == 1:
        display_results(scan(args.files[0], args.magic))
    else:
        for filename in args.files:
            print('%s:' % filename)
            display_results(scan(filename, args.magic), indent=True)


if __name__ == '__main__':
    main()
