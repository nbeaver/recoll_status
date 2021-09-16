#! /usr/bin/env python3
import unittest
import recollstatus
import os
import io
import logging
logger = logging.getLogger(__name__)

class recollstatusTest(unittest.TestCase):
    def test_parsing(self):
        dirname = 'idxstatuses'
        for filename in os.listdir(dirname):
            filepath = os.path.join(dirname, filename)
            with open(filepath) as fp:
                try:
                    parsed = recollstatus.parse_idxstatus(fp, write_tempfiles=False)
                except:
                    logging.error("recollstatus.parse_idxstatus failed on file: {}".format(filepath))
                    raise
                recollstatus.format_idxstatus(parsed)

if __name__ == '__main__':
    unittest.main()
