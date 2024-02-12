# -*- encoding: utf-8 -*-
"""
CAXE
caxe.core.reporting module

"""

import json
import falcon
import requests
import blake3

from lxml import etree, html
from arelle import ModelManager, CntlrCmdLine, FileSource

from keri.core import coring
from keri.help import ogler
from keri import help

from caxe.core import attribing

logger = ogler.getLogger()

def loadEnds(app):

    reportEnd = ReportResourceEnd()
    app.add_route("/report", reportEnd)

    saidifyEnd = SaidifyResource()
    app.add_route("/report/saidify", saidifyEnd)

    return reportEnd

class ReportResourceEnd:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200


class SaidifyResource:
    """ Resource class for extract and saidify facts """

    @staticmethod
    def on_post(req, rep):
        """ Saidify facts POST endpoint

        Parameters:
            req (Request): falcon.Request HTTP request object
            rep (Response): falcon.Response HTTP response object

        """
        
        print(f"request to saidify report file and facts...")

        body = req.get_media()

        report_url = body.get("report_url")
        print(f"report file: {report_url}")
        if not report_url:
            raise falcon.HTTPBadRequest(title='Missing URL', description='The request must include an ixbrl report_url field.')

        fact_ids = body.get('fact_ids', None)
        print(f"facts to saidify: {fact_ids}")

        try:
            response = requests.get(report_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise falcon.HTTPBadRequest('File fetching failed', f'Failed to fetch report file from the provided URL: {str(e)}')

        try:
            file_content = response.content

            root = html.document_fromstring(file_content)

            links = root.xpath(".//link[@type='application/json+acdc']")
            print(f"acdc credential links: {links}")
            for link in links:
                link.getparent().remove(link)

            data = etree.tostring(root)
            xmld = etree.canonicalize(data.decode("utf-8"))

            raw = blake3.blake3(xmld.encode("utf-8")).digest()
            diger = coring.Diger(raw=raw)
            print(f"canonicalized data said: {diger.qb64}")

            a = dict(
                d='',
                rd=diger.qb64,
                dt=help.nowIso8601()
            )

            if fact_ids is not None and len(fact_ids) > 0:

                try:
                    cntlr = CntlrCmdLine.CntlrCmdLine()
                    cntlr.startLogging(logFileName='logToBuffer')
                    mmgr = ModelManager.initialize(cntlr)
                    filesource = FileSource.FileSource(report_url)
                    mmgr.load(filesource)

                    attriber = attribing.Attiber(dts=mmgr.modelXbrl)
                    attriber.createViewer()

                except Exception as e:
                    raise falcon.HTTPBadRequest('Processing Error', f'Failed to process the iXBRL file with Arelle: {str(e)}')

                values = []

                filtered_facts = [fact for fact in mmgr.modelXbrl.facts if fact.id in fact_ids]

                for fact in filtered_facts:
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

            rep.status = falcon.HTTP_200
            rep.content_type = "application/json"
            rep.data = json.dumps(a).encode("utf-8")
        
        except falcon.HTTPBadRequest:
            raise  # Re-raise Falcon's HTTPBadRequest exceptions to be handled by Falcon itself
        except Exception as e:
            raise falcon.HTTPInternalServerError('Internal Server Error', f'An unexpected error occurred while processing iXBRL file: {str(e)}')



