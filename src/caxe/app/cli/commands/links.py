# -*- encoding: utf-8 -*-
"""
keri.kli.commands module

"""
import argparse

from lxml import html

parser = argparse.ArgumentParser(description='Extract HTML link elements')
parser.set_defaults(handler=lambda args: handler(args),
                    transferable=True)
parser.add_argument('--file', '-f', help='File to load and extract', default="", required=True)


def handler(args):
    """
    Create KERI identifier prefix in specified key store with alias

    Args:
        args(Namespace): arguments object from command line
    """
    f = open(args.file, mode="r")

    data = f.read().encode("utf-8")
    root = html.document_fromstring(data)

    links = root.xpath(".//link[@rel='prefetch author']")

    for link in links:
        print(html.tostring(link))
