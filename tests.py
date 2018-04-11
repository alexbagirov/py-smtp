import unittest
from smtp import SMTP, SMTPException


class TestSMTP(unittest.TestCase):
    def setUp(self) -> None:
        self.smtp = SMTP()

    def test_exception_when_wrong_server(self):
        with self.assertRaises(SMTPException):
            self.smtp.connect('a', 555)


if __name__ == '__main__':
    unittest.main()
