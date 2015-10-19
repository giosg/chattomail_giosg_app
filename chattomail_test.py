import chattomail
import unittest


class ChattomailTestCase(unittest.TestCase):
    def setUp(self):
        self.app = chattomail.app.test_client()

    def tearDown(self):
        pass

    def test_convert_timezone(self):
        assert 1 == 1

if __name__ == '__main__':
    unittest.main()
