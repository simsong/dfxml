
# This software was developed in whole or in part by employees of the
# Federal Government in the course of their official duties, and with
# other Federal assistance. Pursuant to title 17 Section 105 of the
# United States Code portions of this software authored by Federal
# employees are not subject to copyright protection within the United
# States. For portions not authored by Federal employees, the Federal
# Government has been granted unlimited rights, and no claim to
# copyright is made. The Federal Government assumes no responsibility
# whatsoever for its use by other parties, and makes no guarantees,
# expressed or implied, about its quality, reliability, or any other
# characteristic.
#
# We would appreciate acknowledgement if the software is used.

from distutils.core import setup
setup(
  name='dfxml',
  version='1.0.1',
  url='https://github.com/simsong/dfxml',
#  scripts=['idifference.py','rdifference.py'],
  py_modules=['dfxml','fiwalk']
)
