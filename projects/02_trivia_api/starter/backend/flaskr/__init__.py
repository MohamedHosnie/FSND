import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func, and_, or_
from flask_cors import CORS
import random

from models import setup_db, Question, Category, db

# Pagination
QUESTIONS_PER_PAGE = 10
def paginate_questions(request, questions):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  formatted_questions = [question.format() for question in questions]
  current_questions = formatted_questions[start:end]
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  # CORS settings
  CORS(app)
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  # Categories - GET
  @app.route('/categories')
  def get_categories():
    categories = db.session.query(Category).order_by(Category.id).all()
    formatted_categories = { category.id: category.type for category in categories }

    if len(categories) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'categories': formatted_categories
    })

  # Questions - GET
  @app.route('/questions')
  def get_questions():
    questions = db.session.query(Question).order_by(Question.id).all()
    current_questions = paginate_questions(request, questions)
    if len(current_questions) == 0:
      abort(404)

    categories = db.session.query(Category).order_by(Category.id).all()
    formatted_categories = { category.id: category.type for category in categories }

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'categories': formatted_categories
    })

  # Questions - POST
  @app.route('/questions', methods=['POST'])
  def post_questions():
    data = request.get_json()

    question = data.get('question', None)
    answer = data.get('answer', None)
    category = data.get('category', None)
    difficulty = data.get('difficulty', None)
    search = data.get('searchTerm', None)

    try:
      if search is not None:
        questions = db.session.query(Question).filter(Question.question.ilike('%{}%'.format(search))).order_by(Question.id).all()
        current_questions = paginate_questions(request, questions)

        if len(current_questions) == 0:
          abort(404)

        return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(questions)
        })

      else:
        new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
        new_question.insert()
        return jsonify({
          'success': True,
          'created': new_question.id
        })

    except:
      abort(422)

  # Questions - DELETE
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = db.session.query(Question).get(question_id)
    if question is None:
      abort(404)

    try:
      question.delete()
      return jsonify({
        'success': True,
        'deleted': question_id
      })
    
    except:
      abort(422)

  # Catgories -> Questions - GET
  @app.route('/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    questions = db.session.query(Question).filter(Question.category == category_id).order_by(Question.id).all()
    current_questions = paginate_questions(request, questions)

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(questions),
      'current_category': category_id
    })

  # Quizzes - POST
  @app.route('/quizzes', methods=['POST'])
  def quiz_play():
    data = request.get_json()
    previous_questions = data.get('previous_questions', None)
    quiz_category = data.get('quiz_category', None)

    try:
      questions = db.session.query(Question).filter(and_(or_(Question.category == quiz_category['id'], int(quiz_category['id']) == 0), ~Question.id.in_(previous_questions))).all()

      if len(questions) == 0:
        random_question = None
      else:
        random_question = random.choice(questions).format()

      return jsonify({
        'success': True,
        'question': random_question
      })
      
    except:
      abort(422)

  # Error handling
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'bad request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'not found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'unprocessable'
    }), 422
  
  return app

    