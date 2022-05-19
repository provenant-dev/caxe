# -*- encoding: utf-8 -*-
"""
KERI
caxe.core.serving module

"""
import json
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
    data: bytes
    said: str
    start: datetime
    creds: list
    saids: list = None
    result: dict = None


@dataclass
class Cred:
    link: str
    client: http.Client = None
    clientDoer: http.ClientDoer = None
    said: str = ""


class VerifyEnd(doing.DoDoer):

    def __init__(self, hby, hab, kvy, rvy, tvy, vry):
        self.hby = hby
        self.hab = hab
        self.kvy = kvy
        self.tvy = tvy
        self.rvy = rvy
        self.vry = vry
        self.requests = decking.Deck()
        self.requested = decking.Deck()
        self.parsed = decking.Deck()
        self.complete = decking.Deck()
        self.failed = decking.Deck()

        self.parser = parsing.Parser(framed=True,
                                     kvy=kvy,
                                     tvy=tvy,
                                     rvy=rvy,
                                     vry=vry)

        doers = []

        super(VerifyEnd, self).__init__(doers=doers)

    def on_post(self, req, rep):
        """ Verify POST endpoint

        Parameters:
            req: falcon.Request HTTP request
            rep: falcon.Response HTTP response

       ---
        summary:  Get schema JSON of specified schema
        description:  Get schema JSON of specified schema
        tags:
           - Verify
        parameters:
          - in: path
            name: said
            schema:
              type: string
            required: true
            description: qb64 self-addressing identifier of schema to get
        responses:
           200:
              description: Schema JSON successfully returned
           404:
              description: No schema found for SAID
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

        creds = [Cred(link=link.attribute("href")) for link in links]
        rpt = Report(data=data, said=diger.qb64, start=helping.nowUTC(), creds=creds)
        self.requests.append(rpt)

        rep.status = falcon.HTTP_200
        rep.content_type = "text/html"
        rep.data = "poop"

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

                    cred.client = client
                    cred.clientDoer = clientDoer

                    client.request(
                        method="GET",
                        path=purl.path,
                        qargs=parse.parse_qs(purl.query),
                        )

                self.requested.append(report)

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
                    if cred.client is not None and cred.client.responses:
                        response = cred.client.responses.popleft()
                        self.remove([cred.clientDoer])

                        if not response["status"] == 200:
                            report.result = dict(msg=f"Invalid reponse from credential link: {cred.link}")
                            self.failed.append(report)
                            continue

                        if response["headers"]["Content-Type"] == "application/json+acdc":
                            self.parser.parse(ims=bytearray(response["body"]))
                            cred.client = None
                        else:
                            report.result = dict(msg=f"Invalid reponse from credential link: {cred.link}")
                            self.failed.append(report)
                            continue

                complete = True
                for cred in report.creds:
                    if cred.client is not None:
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
                for cred in report.creds:
                    creder = self.vry.reger.saved.get(keys=cred.said)
                    if creder is None:
                        self.parsed.append(report)
                        continue

                    attrs = creder.crd["a"]
                    if "rd" in attrs:
                        continue

                    if attrs["rd"] != report.said:
                        report.result = dict(msg=f"Report SAID in credential {attrs['rf']} does not match "
                                                 f"actual SAID {report.said} for credential {creder.said}")
                        self.failed.append(report)
                    # TODO: validate individual facts

                    results[creder.said] = attrs

                self.complete.append(report)

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

    reger = viring.Reger(name=hab.name, db=hab.db, temp=False)
    verfer = verifying.Verifier(hby=hby, reger=reger)

    cues = []
    rvy = routing.Revery(db=hby.db, cues=cues)
    kvy = eventing.Kevery(db=hby.db,
                          lax=True,
                          local=False,
                          rvy=rvy,
                          cues=cues)
    kvy.registerReplyRoutes(router=rvy.rtr)

    tvy = Tevery(reger=verfer.reger,
                 db=hby.db,
                 local=False,
                 cues=cues)

    tvy.registerReplyRoutes(router=rvy.rtr)

    app = falcon.App()
    server = http.Server(port=httpPort, app=app)
    httpServerDoer = http.ServerDoer(server=server)

    doers = []
    doers += loadEnds(app, hby, hab, kvy, tvy, rvy, verfer)
    doers.extend([httpServerDoer])

    return doers


def loadEnds(app, hby, hab, kvy, tvy, rvy, vry):
    verifyEnd = VerifyEnd(hby, hab, kvy, tvy, rvy, vry)
    app.add_route("/verify", verifyEnd)

    return [verifyEnd]
