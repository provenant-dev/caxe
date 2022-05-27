# -*- encoding: utf-8 -*-
"""
KERI
caxe.core.serving module

"""
import json
import time
from dataclasses import dataclass
from datetime import datetime
from urllib import parse

import blake3
import falcon
from hio.base import doing
from hio.core import http
from hio.help import decking
from keri import help
from keri.core import coring, routing, eventing, parsing
from keri.help import helping
from keri.vdr import viring, verifying
from keri.vdr.eventing import Tevery
from lxml import html, etree

logger = help.ogler.getLogger()


@dataclass
class Report:
    uuid: str
    data: bytes = None
    said: str = None
    start: datetime = None
    creds: list = None
    saids: list = None
    result: dict = None
    clientDoer: http.ClientDoer = None


@dataclass
class Cred:
    link: str
    clientDoer: http.ClientDoer = None
    said: str = ""


class VerifyEnd(doing.DoDoer):

    def __init__(self, hby, hab, kvy, rvy, tvy, vry):
        self.ims = bytearray()
        self.hby = hby
        self.hab = hab
        self.kvy = kvy
        self.tvy = tvy
        self.rvy = rvy
        self.vry = vry
        self.pages = decking.Deck()
        self.requests = decking.Deck()
        self.requested = decking.Deck()
        self.parsed = decking.Deck()
        self.complete = decking.Deck()
        self.failed = decking.Deck()

        self.parser = parsing.Parser(ims=self.ims,
                                     framed=True,
                                     kvy=kvy,
                                     tvy=tvy,
                                     rvy=rvy,
                                     vry=vry)

        doers = [doing.doify(self.getDo), doing.doify(self.requestDo), doing.doify(self.requestedDo),
                 doing.doify(self.parsedDo), doing.doify(self.msgDo), doing.doify(self.escrowDo)]

        super(VerifyEnd, self).__init__(doers=doers)

    def on_get(self, req, rep):
        """ Verify GET endpoint

        Parameters:
            req: falcon.Request HTTP request
            rep: falcon.Response HTTP response

       ---
        summary:  Get schema JSON of specified schema
        description:  Get schema JSON of specified schema
        tags:
           - Verify
        parameters:
          - in: query
            name: url
            schema:
              type: string
            required: true
            description: ViRA ACDC Credential OOBI URL
        responses:
           200:
              description: ViRA attributes section with associated vLEI credentials
           404:
              description: No credentials found
        """
        url = req.params.get("url")
        purl = parse.urlparse(url)
        client = http.clienting.Client(hostname=purl.hostname, port=purl.port)
        clientDoer = http.clienting.ClientDoer(client=client)
        self.extend([clientDoer])

        client.request(
            method="GET",
            path=purl.path,
            qargs=parse.parse_qs(purl.query),
        )

        uuid = coring.randomNonce()
        rpt = Report(uuid=uuid, clientDoer=clientDoer)
        self.pages.append(rpt)

        rep.stream = ReportIterable(uuid=uuid, complete=self.complete, failed=self.failed)

    def on_post(self, req, rep):
        """ Verify POST endpoint

        Parameters:
            req: falcon.Request HTTP request
            rep: falcon.Response HTTP response

       ---
        summary:  Verify all ViRA credential links
        description:  Verify all ViRA credential links
        tags:
           - Verify
        responses:
           200:
              description: ViRA attributes section with associated vLEI credentials
           404:
              description: No credentials found
        """
        data = req.bounded_stream.read()
        root = html.document_fromstring(data)
        links = root.xpath(".//link[@type='application/json+acdc']")
        if len(links) == 0:
            rep.status = falcon.HTTP_400
            rep.content_type = "application/json"
            msg = dict(msg="No credential links found")
            rep.data = json.dumps(msg, indent=2)

        xmld = etree.canonicalize(data.decode("utf-8"))
        raw = blake3.blake3(xmld.encode("utf-8")).digest()
        diger = coring.Diger(raw=raw)

        creds = [Cred(link=link.attrib["href"]) for link in links]
        uuid = coring.randomNonce()
        rpt = Report(uuid=uuid, data=data, said=diger.qb64, start=helping.nowUTC(), creds=creds)
        self.requests.append(rpt)

        rep.stream = ReportIterable(uuid=uuid, complete=self.complete, failed=self.failed)

    def getDo(self, tymth=None, tock=0.0):
        """
        Returns doifiable Doist for processing requests for report verification

        This method creates HTTP requests for the credential OOBIs and sends them.

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value

        Usage:
            add result of doify on this method to doers list
        """
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        while True:
            if not self.pages:
                yield self.tock

            while self.pages:
                rpt = self.pages.popleft()
                if rpt.clientDoer.client.responses:
                    response = rpt.clientDoer.client.responses.popleft()
                    self.remove([rpt.clientDoer])
                    rpt = Report(data=b'', said="", start=helping.nowUTC(), creds=[])

                    if not response["status"] == 200:
                        rpt.result = dict(msg="Invalid reponse from page")
                        self.failed.append(rpt)
                        continue

                    data = response['body'].encode("utf-8")
                    root = html.document_fromstring(data)
                    links = root.xpath(".//link[@type='application/json+acdc']")
                    if len(links) == 0:
                        rpt.result = dict(msg="No links found on page")
                        self.failed.append(rpt)
                        continue

                    xmld = etree.canonicalize(data.decode("utf-8"))
                    raw = blake3.blake3(xmld.encode("utf-8")).digest()
                    diger = coring.Diger(raw=raw)

                    creds = [Cred(link=link.attribute("href")) for link in links]
                    rpt.data = data
                    rpt.said = diger.qb64
                    rpt.cred = creds

                    self.requests.append(rpt)
                else:
                    self.pages.append(rpt)

                yield self.tock

    def requestDo(self, tymth=None, tock=0.0):
        """
        Returns doifiable Doist for processing requests for report verification

        This method creates HTTP requests for the credential OOBIs and sends them.

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value

        Usage:
            add result of doify on this method to doers list
        """
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        while True:
            if not self.requests:
                yield self.tock

            while self.requests:
                report = self.requests.popleft()
                for cred in report.creds:
                    purl = parse.urlparse(cred.link)
                    cred.said = purl.path.lstrip('/oobi/')

                    client = http.clienting.Client(hostname=purl.hostname, port=purl.port)
                    clientDoer = http.clienting.ClientDoer(client=client)
                    self.extend([clientDoer])

                    cred.clientDoer = clientDoer
                    client.request(
                        method="GET",
                        path=purl.path,
                        qargs=parse.parse_qs(purl.query),
                        )

                self.requested.append(report)

                yield self.tock

    def requestedDo(self, tymth, tock=0.0):
        """ Process Client responses by parsing the messages and removing the client/doer

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value

        """
        self.wind(tymth)
        self.tock = tock
        yield self.tock

        while True:
            while self.requested:
                report = self.requested.popleft()
                for cred in report.creds:
                    if cred.clientDoer is not None and cred.clientDoer.client.responses:
                        response = cred.clientDoer.client.responses.popleft()
                        self.remove([cred.clientDoer])

                        if not (response["status"] == 200):
                            report.result = dict(msg=f"Invalid reponse from credential link: {cred.link}")
                            self.failed.append(report)
                            continue

                        if response["headers"]["Content-Type"] == "application/acdc+json":
                            self.ims.extend(bytearray(response["body"]))
                            cred.clientDoer = None
                        else:
                            report.result = dict(msg=f"Invalid reponse from credential link: {cred.link}")
                            self.failed.append(report)
                            continue

                complete = True
                for cred in report.creds:
                    if cred.clientDoer is not None:
                        complete = False

                if complete:
                    self.parsed.append(report)
                else:
                    self.requested.append(report)

                yield self.tock

            yield self.tock

    def parsedDo(self, tymth, tock=0.0):
        """ Process reports waiting for all pending credentials to be parsed

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value

        """
        self.wind(tymth)
        self.tock = tock
        yield self.tock

        while True:
            while self.parsed:
                report = self.parsed.popleft()
                results = dict()

                complete = True
                failed = False
                for cred in report.creds:
                    said = self.vry.reger.saved.get(keys=cred.said)
                    if said is None:
                        complete = False
                        continue

                    creder = self.vry.reger.creds.get(keys=(said.qb64,))
                    attrs = creder.crd["a"]
                    if "rd" not in attrs:
                        complete = False
                        continue

                    if attrs["rd"] != report.said:
                        report.result = dict(msg=f"Report SAID in credential {attrs['rd']} does not match "
                                                 f"actual SAID {report.said} for credential {creder.said}")
                        self.failed.append(report)
                        failed = True
                    # TODO: validate individual facts

                    results[creder.said] = attrs

                if failed:
                    continue
                elif complete:
                    report.results = results
                    self.complete.append(report)
                else:
                    self.parsed.append(report)

                yield self.tock

            yield self.tock

    def msgDo(self, tymth=None, tock=0.0):
        """
        Returns doifiable Doist compatibile generator method (doer dog) to process
            incoming message stream of .kevery

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value

        Usage:
            add result of doify on this method to doers list
        """
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        if self.parser.ims:
            logger.info("Client %s received:\n%s\n...\n", self.kvy, self.parser.ims[:1024])
        done = yield from self.parser.parsator()  # process messages continuously
        return done  # should nover get here except forced close

    def escrowDo(self, tymth=None, tock=0.0):
        """
         Returns doifiable Doist compatibile generator method (doer dog) to process
            .kevery and .tevery escrows.

        Parameters:
            tymth (function): injected function wrapper closure returned by .tymen() of
                Tymist instance. Calling tymth() returns associated Tymist .tyme.
            tock (float): injected initial tock value

        Usage:
            add result of doify on this method to doers list
        """
        self.wind(tymth)
        self.tock = tock
        _ = (yield self.tock)

        while True:
            self.kvy.processEscrows()
            self.rvy.processEscrowReply()
            self.tvy.processEscrows()
            self.vry.processEscrows()

            yield


def setup(hby, alias, httpPort):
    # make hab
    hab = hby.habByName(name=alias)
    if hab is None:
        hab = hby.makeHab(name=alias, transferable=True)

    print(f"Using hab {hab.name}:{hab.pre}")
    reger = viring.Reger(name=hab.name, db=hab.db, temp=False)
    verfer = verifying.Verifier(hby=hby, reger=reger)

    rvy = routing.Revery(db=hby.db)
    kvy = eventing.Kevery(db=hby.db,
                          lax=True,
                          local=False,
                          rvy=rvy)
    kvy.registerReplyRoutes(router=rvy.rtr)

    tvy = Tevery(reger=verfer.reger,
                 db=hby.db,
                 local=False)

    tvy.registerReplyRoutes(router=rvy.rtr)

    app = falcon.App(middleware=falcon.CORSMiddleware(
        allow_origins='*', allow_credentials='*', expose_headers=['cesr-attachment', 'cesr-date', 'content-type']))
    server = http.Server(port=httpPort, app=app)
    httpServerDoer = http.ServerDoer(server=server)

    doers = []
    doers += loadEnds(app=app, hby=hby, hab=hab, kvy=kvy, tvy=tvy, rvy=rvy, vry=verfer)
    doers.extend([httpServerDoer])

    return doers


def loadEnds(app, hby, hab, kvy, tvy, rvy, vry):
    verifyEnd = VerifyEnd(hby=hby, hab=hab, kvy=kvy, tvy=tvy, rvy=rvy, vry=vry)
    app.add_route("/verify", verifyEnd)

    return [verifyEnd]


class ReportIterable:

    TimeoutReport = 10

    def __init__(self, uuid, complete, failed):
        self.uuid = uuid
        self.complete = complete
        self.failed = failed
        self.done = False

    def __iter__(self):
        self.start = self.end = time.perf_counter()
        return self

    def __next__(self):

        if self.done:
            raise StopIteration

        if self.end - self.start < self.TimeoutReport:
            if self.start == self.end:
                self.end = time.perf_counter()
                return b''

            if self.complete:
                rpt = self.complete.popleft()
                if rpt.uuid == self.uuid:
                    data = json.dumps(rpt.result)
                    self.done = True
                    return f"HTTP/1.1 200 OK\nContent-Length: {len(data)}\nContent-Type: application/json\n" \
                           f"{data}\n\n".encode("utf-8")
                else:
                    self.complete.append(rpt)
                    return b''

            if self.failed:
                rpt = self.failed.popleft()
                if rpt.uuid == self.uuid:
                    data = json.dumps(rpt.result)
                    self.done = True
                    return f"HTTP/1.1 500 FAILED\nContent-Length: {len(data)}\nContent-Type: application/json\
                    n{data}\n\n".encode("utf-8")

            self.end = time.perf_counter()
            return b''

        raise StopIteration
