from unittest import TestCase
import Controller


class Test(TestCase):
    def test_main(self):
        self.assertRaises(Exception, Controller.main())
