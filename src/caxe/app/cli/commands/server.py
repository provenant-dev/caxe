# -*- encoding: utf-8 -*-
"""
keri.kli.commands module

"""
import argparse
import os

from keri.app import keeping, habbing, directing, configing, oobiing
from keri.app.cli.common import existing

from caxe.core import serving

parser = argparse.ArgumentParser(description='Launch CaXe micro-service')
parser.set_defaults(handler=lambda args: launch(args),
                    transferable=True)
parser.add_argument('--host', 
                    type=str, 
                    default=os.environ.get('CAXE_HOST', '0.0.0.0'),
                    help='Host address to bind (default: 0.0.0.0)')
parser.add_argument('-p', '--port',
                    action='store',
                    default=int(os.environ.get('CAXE_PORT', 8723)),
                    type=int,
                    help="Port on which caxe service will run.  Defaults to 8723")
parser.add_argument('-n', '--name',
                    action='store',
                    default="caxe",
                    help="Name of controller. Default is caxe.")
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
    htp = args.port
    host = args.host
    alias = args.alias
    configFile = args.configFile
    configDir = args.configDir

    ks = keeping.Keeper(name=name,
                        base=base,
                        temp=False,
                        reopen=True)

    aeid = ks.gbls.get('aeid')

    if aeid is None:

        cf = None
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
    obl = oobiing.Oobiery(hby=hby)
    
    doers = [hbyDoer, *obl.doers]

    doers += serving.setup(hby, alias, htp, host)

    print(f"Caxe Server listening on {htp}")
    directing.runController(doers=doers, expire=0.0)


def main():
    args = parser.parse_args()
    launch(args)


if __name__ == "__main__":
    main()
