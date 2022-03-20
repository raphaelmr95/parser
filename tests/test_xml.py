import unittest

class TestXML(unittest.TestCase):

    def test_xml(self):
        with open('files_test/test_xml.xml', 'r') as f:
            xml = f.read()
            self.assertEqual(xml, '<xml><test>test</test></xml>')
    
    def test_xml_error(self):
        with open('files_test/test_xml_error.xml', 'r') as f:
            xml = f.read()
            self.assertNotEqual(xml, '<xml><test>test</test></xml>')

