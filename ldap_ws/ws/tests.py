import ldap

from django.utils import unittest


# example test case for now.
class LDAPTestCase(unittest.TestCase):
    def setUp(self):
        self.lion = 'roar'
        self.cat = 'meow'

    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        self.assertEqual(self.lion, 'roar')
        self.assertEqual(self.cat, 'meow')
