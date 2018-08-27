from app import app
import unittest


class FlaskTestCase(unittest.TestCase):

    def test_index(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def memeber_register(self):
        tester = app.test_client(self)
        response = tester.get('/dash/', content_type='html/text')
        self.assertEqual(response.status_code, 200)



if __name__ == '__main__':
    unittest.main()

