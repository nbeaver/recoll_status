#! /usr/bin/env python3
import unittest
import recollstatus
import os
import logging
import io

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

    def test_empty(self):
        empty_fp = io.StringIO(u'')
        empty_fp.name = 'empty'
        with self.assertRaises(ValueError):
            parsed = recollstatus.parse_idxstatus(empty_fp)

if __name__ == '__main__':
    unittest.main()
