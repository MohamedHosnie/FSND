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

    # Categories - GET
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

    # Questions - GET
    def test_get_questions(self):
        question1 = Question(question='test_question1', answer='test_answer1', category=None, difficulty=None)
        db.session.add(question1)
        db.session.commit()

        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(len(data['questions']), 1)
    
    def test_get_questions_exceed_pages(self):
        question1 = Question(question='test_question1', answer='test_answer1', category=None, difficulty=None)
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

    # Questions - POST
    def test_create_question(self):
        category1 = Category(type='test_cat_1')
        db.session.add(category1)
        db.session.commit()

        category_id = category1.id

        res = self.client().post('/questions', json={
            'question': 'test_create_question',
            'answer': 'sample_answer',
            'category': category1.id,
            'difficulty': 2
        })

        data = json.loads(res.data)
        created_question = db.session.query(Question).get(data['created'])

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(created_question)
        self.assertEqual(created_question.question, 'test_create_question')
        self.assertEqual(created_question.answer, 'sample_answer')
        self.assertEqual(created_question.category, category_id)
        self.assertEqual(created_question.difficulty, 2)

    def test_create_question_error(self):
        res = self.client().post('/questions', json={
            'question': 'test_create_question',
            'answer': 'sample_answer',
            'difficulty': 'difficulty_test_string_instead_of_int'
        })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    def test_search_questions(self):
        question1 = Question(question='test_question1', answer='test_answer1', category=None, difficulty=None)
        question2 = Question(question='test_question2', answer='test_answer2', category=None, difficulty=None)
        db.session.add(question1)
        db.session.add(question2)
        db.session.commit()

        res = self.client().post('/questions', json={
            'searchTerm': 'tion2'
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(len(data['questions']), 1)

    def test_search_questions_no_result(self):
        question1 = Question(question='test_question1', answer='test_answer1', category=None, difficulty=None)
        question2 = Question(question='test_question2', answer='test_answer2', category=None, difficulty=None)
        db.session.add(question1)
        db.session.add(question2)
        db.session.commit()

        res = self.client().post('/questions', json={
            'searchTerm': 'xx'
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    # Questions - DELETE
    def test_delete_question(self):
        question1 = Question(question='test_question1', answer='test_answer1', category=None, difficulty=None)
        db.session.add(question1)
        db.session.commit()

        res = self.client().delete('/questions/' + str(question1.id))
        data = json.loads(res.data)

        deleted_question = db.session.query(Question).get(question1.id)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question1.id)
        self.assertEqual(deleted_question, None)

    def test_delete_question_not_found(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # Catgories -> Questions - GET
    def test_get_question_by_category(self):
        category1 = Category(type='test_cat_1')
        category2 = Category(type='test_cat_2')
        db.session.add(category1)
        db.session.add(category2)
        db.session.commit()
        question1 = Question(question='test_question1', answer='test_answer1', category=category1.id, difficulty=1)
        question2 = Question(question='test_question2', answer='test_answer2', category=category2.id, difficulty=1)
        db.session.add(question1)
        db.session.add(question2)
        db.session.commit()

        res = self.client().get('/categories/' + str(category1.id) + '/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])
        self.assertEqual(data['total_questions'], 1)
        self.assertEqual(len(data['questions']), 1)

    def test_get_question_by_category_error(self):
        category1 = Category(type='test_cat_1')
        category2 = Category(type='test_cat_2')
        db.session.add(category1)
        db.session.add(category2)
        db.session.commit()
        question1 = Question(question='test_question1', answer='test_answer1', category=category2.id, difficulty=1)
        question2 = Question(question='test_question2', answer='test_answer2', category=category2.id, difficulty=1)
        db.session.add(question1)
        db.session.add(question2)
        db.session.commit()

        res = self.client().get('/categories/' + str(category1.id) + '/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # Quizzes - POST
    def test_quiz_play(self):
        category1 = Category(type='test_cat_1')
        db.session.add(category1)
        db.session.commit()
        question1 = Question(question='test_question1', answer='test_answer1', category=category1.id, difficulty=None)
        question2 = Question(question='test_question2', answer='test_answer2', category=category1.id, difficulty=None)
        question3 = Question(question='test_question3', answer='test_answer3', category=category1.id, difficulty=None)
        db.session.add(question1)
        db.session.add(question2)
        db.session.add(question3)
        db.session.commit()

        res = self.client().post('/quizzes', json={
            'previous_questions': [question1.id, question2.id],
            'quiz_category': { 'id': category1.id, 'type': category1.type }
        })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['id'], question3.id)
    
    def test_quiz_play_questions_finished(self):
        category1 = Category(type='test_cat_1')
        db.session.add(category1)
        db.session.commit()
        question1 = Question(question='test_question1', answer='test_answer1', category=category1.id, difficulty=None)
        question2 = Question(question='test_question2', answer='test_answer2', category=category1.id, difficulty=None)
        question3 = Question(question='test_question3', answer='test_answer3', category=category1.id, difficulty=None)
        db.session.add(question1)
        db.session.add(question2)
        db.session.add(question3)
        db.session.commit()

        res = self.client().post('/quizzes', json={
            'previous_questions': [question1.id, question2.id, question3.id],
            'quiz_category': { 'id': category1.id, 'type': category1.type }
        })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['question'], None)
    
    def test_quiz_play_no_data_error(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': None
        })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()