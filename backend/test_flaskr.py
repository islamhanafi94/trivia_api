import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy


from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'islam:islam@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_categories(self):
        res = self.client().get('/categories')
        self.assertEqual(res.status_code, 200)

    def test_get_questions_success(self):
        page = 1
        res = self.client().get("/questions?page={page}")
        # data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    # def test_delete_question_success(self):
    #     res = self.client().delete("/questions/10")
    #     self.assertEqual(res.status_code, 200)

    def test_delete_question_failure(self):
        res = self.client().delete("/questions/566666")
        self.assertEqual(res.status_code, 404)

    def test_add_question_success(self):
        res = self.client().post("/questions", data=json.dumps({
            'question': 'q',
            'answer': 'a',
            'category': 4,
            'difficulty': 5
        }), headers={'Content-Type': 'application/json'})
        self.assertEqual(res.status_code, 201)

    def test_search_question_success(self):
        res = self.client().post("/questions/search", data=json.dumps({
            'searchTerm': 'q',
        }), headers={'Content-Type': 'application/json'})
        self.assertEqual(res.status_code, 200)

    def test_search_question_failure(self):
        res = self.client().post("/questions/search", data=json.dumps({
            'searchTerm': 'lrnflrnflnf',
        }), headers={'Content-Type': 'application/json'})
        self.assertEqual(res.status_code, 404)

    def test_get_category_questions_success(self):
        res = self.client().get("/categories/4/questions")
        self.assertEqual(res.status_code, 200)


        # Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
