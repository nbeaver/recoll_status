#! /usr/bin/env python
import unittest
import recollstatus
import os
import logging

class recollstatusTest(unittest.TestCase):
    def test_parsing(self):
        dirname = 'idxstatuses'
        for filename in os.listdir(dirname):
            filepath = os.path.join(dirname, filename)
            if os.path.isfile(filepath):
                try:
                    parsed = recollstatus.parse_idxstatus(filepath, write_tempfiles=False)
                except:
                    logging.error("recollstatus.parse_idxstatus failed on file: {}".format(filepath))
                    raise
                recollstatus.format_idxstatus(parsed)

if __name__ == '__main__':
    unittest.main()
