# -*- encoding: utf-8 -*-
"""
keri.kli.commands module

"""
import argparse
import io
import json

import blake3
from lxml import etree, html

from keri import help
from keri.core import coring
from arelle import ModelManager, CntlrCmdLine, FileSource

from caxe.core import attribing

parser = argparse.ArgumentParser(description='Extract attributes section')
parser.set_defaults(handler=lambda args: handler(args),
                    transferable=True)
parser.add_argument('--file', '-f', help='File to load and extract', default="", required=True)
parser.add_argument('--out', '-o', help='Putput file for extract data values', default="", required=True)


def handler(args):
    """
    Create KERI identifier prefix in specified key store with alias

    Args:
        args(Namespace): arguments object from command line
    """
    cntlr = CntlrCmdLine.CntlrCmdLine()
    cntlr.startLogging(logFileName='logToBuffer')

    f = io.open(args.file, mode="r", encoding="utf-8")
    out = io.open(args.out, mode="w", encoding="utf-8")

    data = f.read()

    root = html.document_fromstring(data.encode("utf-8"))
    links = root.xpath(".//link[@type='application/json+acdc']")

    for link in links:
        link.getparent().remove(link)

    data = etree.tostring(root)
    xmld = etree.canonicalize(data.decode("utf-8"))
    raw = blake3.blake3(xmld.encode("utf-8")).digest()
    diger = coring.Diger(raw=raw)

    a = dict(
        d='',
        rd=diger.qb64,
        dt=help.nowIso8601()
    )

    mmgr = ModelManager.initialize(cntlr)
    filesource = FileSource.FileSource(args.file)
    mmgr.load(filesource)

    attriber = attribing.Attiber(dts=mmgr.modelXbrl)
    attriber.createViewer()

    values = []
    for fact in mmgr.modelXbrl.facts:
        raw = blake3.blake3(etree.tostring(fact)).digest()
        diger = coring.Diger(raw=raw)
        fad = attriber.taxonomyData['facts'][fact.id]
        attr = dict(
            i=fact.id,
            t=fact.localName,
            d=diger.qb64,
            v=fad['v'],
        )
        attr['c'] = fad['a']['c']
        attr['e'] = fad['a']['e']
        attr['p'] = fad['a']['p']

        if 'f' in fad:
            attr['f'] = fad['f']

        values.append(attr)

    a['f'] = values
    _, a = coring.Saider.saidify(sad=a)

    json.dump(a, out, indent=2)
