# -*- encoding: utf-8 -*-
"""
keri.kli.commands module

"""
import argparse

from keri.app import keeping, habbing, directing, configing
from keri.app.cli.common import existing, oobiing

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
parser.add_argument("--config-dir", "-c", dest="configDir", help="directory override for configuration data")
parser.add_argument('--config-file',
                    dest="configFile",
                    action='store',
                    default=None,
                    help="configuration filename override")


def launch(args, expire=0.0):
    name = args.name
    base = args.base
    bran = args.bran
    htp = args.http
    alias = args.alias
    configFile = args.configFile
    configDir = args.configDir

    ks = keeping.Keeper(name=name,
                        base=base,
                        temp=False,
                        reopen=True)

    aeid = ks.gbls.get('aeid')

    if aeid is None:
        if configFile is not None:
            cf = configing.Configer(name=configFile,
                                    base=base,
                                    headDirPath=configDir,
                                    temp=False,
                                    reopen=True,
                                    clear=False)

        hby = habbing.Habery(name=name, base=base, bran=bran, cf=cf)
    else:
        hby = existing.setupHby(name=name, base=base, bran=bran)

    hbyDoer = habbing.HaberyDoer(habery=hby)  # setup doer
    obl = oobiing.OobiLoader(hby=hby, auto=True)

    doers = [hbyDoer, obl]

    doers += serving.setup(hby, alias, htp)

    print(f"Caxe Server listening on {htp}")
    directing.runController(doers=doers, expire=expire)


def main():
    args = parser.parse_args()
    launch(args)


if __name__ == "__main__":
    main()
