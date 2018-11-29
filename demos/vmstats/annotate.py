#!/usr/bin/env python3
#
# annotate the EMR timeline

import datetime

now8601 = datetime.datetime.utcnow().isoformat()[0:19]

if __name__=="__main__":
    from argparse import ArgumentParser,ArgumentDefaultsHelpFormatter
    parser = ArgumentParser( formatter_class = ArgumentDefaultsHelpFormatter,
                             description="Generate stats on the current cluster" )
    parser.add_argument("--date", help="Date in ISO8601 format being annotated; default is now", default=now8601)
    parser.add_argument("message", help="Message. Put it in quotes.")

    args   = parser.parse_args()
    
