import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category, db


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'Round#06', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # empty database
        db.session.query(Category).delete()
        db.session.query(Question).delete()
        db.session.commit()

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        db.session.query(Category).delete()
        db.session.query(Question).delete()
        db.session.commit()
        pass

    """
    # Done
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        category1 = Category(type='test_cat_1')
        category2 = Category(type='test_cat_2')
        db.session.add(category1)
        db.session.add(category2)
        db.session.commit()

        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 2)

    def test_get_categories_not_found(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_questions(self):
        category1 = Category(type='test_cat_1')
        question1 = Question(question='test_question1', answer='test_answer1', category=category1.id, difficulty=1)
        db.session.add(category1)
        db.session.add(question1)
        db.session.commit()

        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(len(data['questions']), 1)
    
    def test_get_questions_exceed_pages(self):
        category1 = Category(type='test_cat_1')
        question1 = Question(question='test_question1', answer='test_answer1', category=category1.id, difficulty=1)
        db.session.add(category1)
        db.session.add(question1)
        db.session.commit()

        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_get_questions_no_questions(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    def test_delete_question(self):
        category1 = Category(type='test_cat_1')
        question1 = Question(question='test_question1', answer='test_answer1', category=category1.id, difficulty=1)
        db.session.add(category1)
        db.session.add(question1)
        db.session.commit()

        question_id = question1.id

        res = self.client().delete('/questions/' + str(question_id))
        data = json.loads(res.data)

        deleted_question = db.session.query(Question).get(question_id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)
        self.assertEqual(deleted_question, None)

    def test_delete_question_not_found(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()