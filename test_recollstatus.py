#! /usr/bin/env python
import unittest
import recollstatus
import os

class recollstatusTest(unittest.TestCase):
    def test_parsing(self):
        dirname = 'idxstatuses'
        for filename in os.listdir(dirname):
            filepath = os.path.join(dirname, filename)
            if os.path.isfile(filepath):
                parsed = recollstatus.parse_idxstatus(filepath, write_tempfiles=False)
                recollstatus.format_idxstatus(parsed)

if __name__ == '__main__':
    unittest.main()
