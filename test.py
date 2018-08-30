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

    def member_checkin(self):
        tester = app.test_client(self)
        response = tester.get('/checkin/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def settings(self):
        tester = app.test_client(self)
        response = tester.get('/settings/', content_type='html/text')
        self.assertEqual(response.status_code, 200)


    def train_model(self):
        tester = app.test_client(self)
        response = tester.get('/train/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def initialize_model(self):
        tester = app.test_client(self)
        response = tester.get('/init/', content_type='html/text')
        self.assertEqual(response.status_code, 200)


    def face_recognize(self):
        tester = app.test_client(self)
        response = tester.get('/recognize/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def authenticateUser(self):
        tester = app.test_client(self)
        response = tester.get('/authenticateuser/', content_type='html/text')
        self.assertEqual(response.status_code, 200)


    def getfilldetail(self):
        tester = app.test_client(self)
        response = tester.get('/getfilldetail/', content_type='html/text')
        self.assertEqual(response.status_code, 200)


    def filldetail(self):
        tester = app.test_client(self)
        response = tester.get('/filldetail/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def saveDetail(self):
        tester = app.test_client(self)
        response = tester.get('/savedetail/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def getProgress(self):
        tester = app.test_client(self)
        response = tester.get('/getProgress/', content_type='html/text')
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()

