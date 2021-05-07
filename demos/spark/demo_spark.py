#!/usr/bin/env python3
#
# Shows how DFXML works with Spark.
# This program runs Spark if it is not already running


import sys
import os

sys.path.append("../python")
from dfxml_writer import DFXMLWriter

def spark_demo():
    """A small Spark program. Must be run under Spark"""
    from pyspark import SparkConf
    from pyspark import SparkContext
    import operator

    conf = SparkConf()
    sc   = SparkContext(conf=conf)
    m    = 1000000
    result = sc.parallelize(range(0, m+1)).reduce(operator.add)
    print(f"The sum of the numbers 0 to {m} is {result}")
    assert result == 500000500000
    
def run_spark():
    # If we are running under Spark, just call check_spark.
    # Otherwise, run recursively under spark-submit
    import os
    if "SPARK_ENV_LOADED" in os.environ:
        return                  # yea! Spark is running

    # 
    # Re-run this script under Spark, and then exit.
    # 
    import subprocess
    r = subprocess.run(['spark-submit',__file__] + sys.argv[1:])
    assert r.returncode==0
    exit(0)


if __name__=="__main__":
    import argparse
    import time
    parser = argparse.ArgumentParser()
    args   = parser.parse_args()
    
    run_spark()

    dfxml  = DFXMLWriter(filename=f'demo_spark_{int(time.time())}.dfxml',prettyprint=True)
    spark_demo()
    # DFXML file gets written automatically when program exits.
    exit(0)

