import os
import sys
import unittest
import warnings
from argparse import Namespace
from filecmp import cmp

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))

from simple import split_attachments


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            test_func(self, *args, **kwargs)
    return do_test


def merge_parts(parts: list):
    files = {}
    for part in parts:
        if part[0] in files:
            files[part[0]] += part[1]
        else:
            files[part[0]] = part[1]
    return files


class TestAttachmentsSplit(unittest.TestCase):
    def setUp(self):
        self.n = Namespace()
        self.n.attachments = []
        self.n.attch_parts = []

        for i in range(3):
            fname = 'big_{}'.format(i)
            with open(fname, 'wb') as f:
                f.write(os.urandom(2099152))
            self.n.attachments.append((open(fname, 'rb'), None))

        for i in range(3):
            fname = 'medium_{}'.format(i)
            with open(fname, 'wb') as f:
                f.write(os.urandom(1068576))
            self.n.attachments.append((open(fname, 'rb'), None))

        for i in range(3):
            fname = 'small_{}'.format(i)
            with open(fname, 'wb') as f:
                f.write(os.urandom(10))
            self.n.attachments.append((open(fname, 'rb'), None))

    @ignore_warnings
    def test_does_not_split_when_zero(self):
        self.n.max_file_size = 0
        self.n.attch_parts.clear()

        split_attachments(self.n, self.n.attch_parts)
        self.assertEqual(len(self.n.attch_parts), 0)
        self.assertEqual(len(self.n.attachments), 9)

    @ignore_warnings
    def test_split_big_files(self):
        self.n.max_file_size = 2097152
        self.n.attch_parts.clear()

        split_attachments(self.n, self.n.attch_parts)
        self.assertEqual(len(self.n.attch_parts), 6)
        self.assertEqual(len(self.n.attachments), 6)

        self.compare_files(['big'], merge_parts(self.n.attch_parts))

    @ignore_warnings
    def test_split_big_and_medium_files(self):
        self.n.max_file_size = 1048576
        self.n.attch_parts.clear()

        split_attachments(self.n, self.n.attch_parts)
        self.assertEqual(len(self.n.attch_parts), 15)
        self.assertEqual(len(self.n.attachments), 3)

        self.compare_files(['big', 'medium'], merge_parts(self.n.attch_parts))

    def compare_files(self, names: list, new_files: dict):
        for name in names:
            for i in range(3):
                fname = '{}_{}'.format(name, i)
                new_fname = '{}_new'.format(fname)
                with open(new_fname, 'wb') as f:
                    f.write(new_files[fname])
                self.assertTrue(cmp(fname, new_fname))
                os.remove(new_fname)

    def tearDown(self):
        for file in self.n.attachments:
            file[0].close()

        for i in range(3):
            os.remove('big_{}'.format(i))
            os.remove('medium_{}'.format(i))
            os.remove('small_{}'.format(i))
