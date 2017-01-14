#! /usr/bin/env python
import unittest
import recollstatus
import os

class recollstatusTest(unittest.TestCase):
    def test_parse_idxstatus(self):
        dirname = 'idxstatuses'
        for filename in os.listdir(dirname):
            filepath = os.path.join(dirname, filename)
            if os.path.isfile(filepath):
                recollstatus.parse_idxstatus(filepath, write_tempfiles=False)

if __name__ == '__main__':
    unittest.main()
