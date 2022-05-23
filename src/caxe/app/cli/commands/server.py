# -*- encoding: utf-8 -*-
"""
keri.kli.commands module

"""
import argparse

from keri.app import keeping, habbing, directing
from keri.app.cli.common import existing

from caxe.core import serving

parser = argparse.ArgumentParser(description='Launch CaXe micro-service')
parser.set_defaults(handler=lambda args: launch(args),
                    transferable=True)
parser.add_argument('-p', '--http',
                    action='store',
                    default=8723,
                    help="Port on which to serve vLEI schema SADs.  Defaults to 7723")
parser.add_argument('-n', '--name',
                    action='store',
                    default="witness",
                    help="Name of controller. Default is witness.")
parser.add_argument('--base', '-b', help='additional optional prefix to file location of KERI keystore',
                    required=False, default="")
parser.add_argument('--alias', '-a', help='human readable alias for the new identifier prefix', required=True)
parser.add_argument('--passcode', help='22 character encryption passcode for keystore (is not saved)',
                    dest="bran", default=None)  # passcode => bran


def launch(args, expire=0.0):
    name = args.name
    base = args.base
    bran = args.bran
    htp = args.http
    alias = args.alias

    ks = keeping.Keeper(name=name,
                        base=base,
                        temp=False,
                        reopen=True)

    aeid = ks.gbls.get('aeid')

    if aeid is None:
        hby = habbing.Habery(name=name, base=base, bran=bran)
    else:
        hby = existing.setupHby(name=name, base=base, bran=bran)

    hbyDoer = habbing.HaberyDoer(habery=hby)  # setup doer
    doers = [hbyDoer]

    serving.setup(hby, alias, htp)

    directing.runController(doers=doers, expire=expire)


def main():
    args = parser.parse_args()
    launch(args)


if __name__ == "__main__":
    main()
