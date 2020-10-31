import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from werkzeug.exceptions import HTTPException

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    # CORS(app)
    cors = CORS(app)

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Origin',
                             'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')

        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def retireve_all_categories():
        categories = {cat.id: cat.type
                      for cat in Category.query.order_by(Category.id).all()}
        return jsonify({'categories': categories})

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    @app.route('/questions')
    def retireve_all_questions():
        page = request.args.get('page', 1, type=int)
        current_category = ''

        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        # note : handle if page n > all records and return empty []
        questions = [question.format()
                     for question in Question.query.order_by(Question.id).all()]

        categories = {cat.id: cat.type
                      for cat in Category.query.order_by(Category.id).all()}

        return jsonify({
            'questions': questions[start:end],
            'total_questions': len(questions),
            'categories': categories,
            'current_category': ''
        })

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)
        res = {
            'message': '',
            'status_code': 200
        }
        if not question:
            abort(404)

        try:
            question.delete()
            res['message'] = "Record with id : {question_id} is deleted !!"
            res['status_code'] = 200
        except:
            db.session.roll_back()
        finally:
            db.session.close()

        return jsonify(res)

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def insert_question():
        if not request.data:
            abort(400)
        data = dict(request.get_json())
        new_question = Question(data['question'], data['answer'],
                                data['category'], data['difficulty'])
        new_question.insert()
        return jsonify({'status_code': 201})

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    @app.route('/questions/search', methods=['POST'])
    def find_question():
        search_value = dict(request.get_json())['searchTerm']
        print(search_value)
        result = [q.format() for q in Question.query.filter(
            Question.question.ilike(f'%{search_value}%')).all()]

        return jsonify({
            'questions': result,
            'total_questions': len(result),
            'current_category': '',
        })

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:cat_id>/questions')
    def questions_by_category(cat_id):
        questions = [q.format()
                     for q in Question.query.filter_by(category=cat_id).all()]

        current_category = Category.query.get(cat_id)
        return jsonify({
            'questions': questions,
            'total_questions': len(questions),
            'current_category': current_category.type
        })

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def generate_question():
        previous_questions = dict(request.get_json())['previous_questions']
        quiz_category = dict(request.get_json())['quiz_category']

        all_questions = []
        if quiz_category['type'] == 'click' and quiz_category['id'] == 0:
            all_questions = Question.query.order_by(Question.id).all()
        else:
            all_questions = Question.query.filter_by(
                category=quiz_category['id']).order_by(Question.id).all()

        filtered_questions = [q.format()
                              for q in all_questions
                              if q.id not in previous_questions]

        next_question = False if len(
            filtered_questions) == 0 else random.choice(filtered_questions)

        return jsonify({'question': next_question})

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(HTTPException)
    def handle_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        return jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })

    return app
