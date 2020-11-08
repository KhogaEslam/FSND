# ------------------------------------- Imports ------------------------------------------------

import traceback
import random

from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from werkzeug.exceptions import ServiceUnavailable
from models import setup_db, Question, Category

# ------------------------------------- Constants ------------------------------------------------

CATEGORIES_PER_PAGE = 10
QUESTIONS_PER_PAGE = 10

# ------------------------------------ App Init -------------------------------------------------


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, PUT, PATCH, POST, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials',
                             'true')
        return response

# -------------------------------------------------------------------------------------

    # Helpers...

    def paginate_categories(request, all_categories):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * CATEGORIES_PER_PAGE
        end = start + CATEGORIES_PER_PAGE

        categories = [category.format() for category in all_categories]
        paginated_categories = categories[start:end]

        return paginated_categories

    def paginate_questions(request, all_questions):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in all_questions]
        paginated_questions = questions[start:end]

        return paginated_questions


# -------------------------------------------------------------------------------------

    # Routes...

    @app.route('/api/categories')
    def retrieve_categories():
        """
        GET '/categories'
        - Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
        - Request Arguments: None
        - Returns: An object with categories, that each contains an object of category id and category type, total number of categories and success boolean, as the follwoing sample:
        {
            "categories": {
                {
                    "id": 1,
                    "type": "Science"
                },
                {
                    "id": 2,
                    "type": "Art"
                },
                {
                    "id": 3,
                    "type": "Geography"
                },
                {
                    "id": 4,
                    "type": "History"
                },
                {
                    "id": 5,
                    "type": "Entertainment"
                },
                {
                    "id": 6,
                    "type": "Sports"
                }
            },
            "total_categories": 6,
            "success": true
        }
        """
        try:
            all_categories = Category.query.order_by(Category.id).all()
            paginated_categories = paginate_categories(request, all_categories)

            total_categories = len(all_categories)

            res_body = {}

            res_body['categories'] = paginated_categories
            res_body['total_categories'] = total_categories
            res_body['success'] = True

            return jsonify(res_body)

        except Exception:
            abort(422)

    @app.route('/api/questions')
    def retrieve_questions():
        """
        GET '/questions'
        - Fetches a dictionary of questions in which the keys are the ids and the values is the corresponding string of the question, string of the answer,
        integer of category and integer of difficulty
        - Request Arguments: None
        - Returns: An object with questions, that each contains an object of question id, question category id, question difficulty, question answer, and question text.
        total number of questions and success boolean, as the follwoing sample:
        {
            "questions": [
                {
                    "answer": "answer1",
                    "category": 1,
                    "difficulty": 1,
                    "id": 1,
                    "question": "question1"
                },
                {
                    "answer": "answer2",
                    "category": 4,
                    "difficulty": 1,
                    "id": 2,
                    "question": "question2"
                },            {
                    "answer": "answer3",
                    "category": 3,
                    "difficulty": 5,
                    "id": 3,
                    "question": "question3"
                }
            ],
            "total_questions": 3,
            "success": true
        }
        """
        try:
            all_questions = Question.query.order_by(Question.id).all()
            paginated_questions = paginate_questions(request, all_questions)
            categories = Category.query.all()

            total_questions = len(all_questions)

            res_body = {}

            res_body['categories'] = [category.format() for category in categories]
            res_body['questions'] = paginated_questions
            res_body['total_questions'] = total_questions
            res_body['success'] = True

            return jsonify(res_body)

        except Exception:
            abort(422)

    @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        """
        DELETE '/questions/<int:question_id>'
        - Delete a question item in which the key is the id of the question to be deleted.
        - Request Arguments: int:question_id
        - Returns: The deleted question id, An object with questions, that each contains an object of question id, question category id, question difficulty, question answer, and question text.
        total number of questions and success boolean, as the follwoing sample:
        {
            "deleted": 3,
            "questions": [
                {
                    "answer": "answer1",
                    "category": 1,
                    "difficulty": 1,
                    "id": 1,
                    "question": "question1"
                },
                {
                    "answer": "answer2",
                    "category": 4,
                    "difficulty": 1,
                    "id": 2,
                    "question": "question2"
                }
            ],
            "total_questions": 2,
            "success": true
        }
        """
        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(404)

            question.delete()

            all_questions = Question.query.order_by(Question.id).all()
            paginated_questions = paginate_questions(request, all_questions)

            total_questions = len(all_questions)

            res_body = {}

            res_body['questions'] = paginated_questions
            res_body['total_questions'] = total_questions
            res_body['deleted'] = question_id
            res_body['success'] = True

            return jsonify(res_body)

        except Exception:
            abort(422)

    @app.route('/api/questions', methods=['POST'])
    def create_question():
        """
        POST '/questions'
        - Fetches a dictionary of questions in which the keys are the ids and the values is the corresponding string of the question, string of the answer, integer of category and integer of difficulty
        - Request Arguments: An object with a key, question, answer, category, difficulty, that contains a object of question: question_string key:value pairs, answer: answer_string key:value pairs, category: category_id key:value pairs, difficulty: difficulty_id key:value pairs.  
        - Returns: An object with questions, that each contains an object of question id, question category id, question difficulty, question answer, and question text.
        total number of questions and success boolean, as the follwoing sample:
        {
            "questions": [
                {
                    "answer": "answer1",
                    "category": 1,
                    "difficulty": 1,
                    "id": 1,
                    "question": "question1"
                },
                {
                    "answer": "answer2",
                    "category": 4,
                    "difficulty": 1,
                    "id": 2,
                    "question": "question2"
                },
                {
                    "answer": "answer4",
                    "category": 4,
                    "difficulty": 1,
                    "id": 4,
                    "question": "question4"
                }
            ],
            "total_questions": 3,
            "success": true
        }
        """
        data = request.get_json()
        if data:
            question = data.get('question', None)
            answer = data.get('answer', None)
            category = data.get('category', None)
            difficulty = data.get('difficulty', None)

            try:
                questions = Question(question=question, answer=answer, category=category, difficulty=difficulty)
                questions.insert()

                all_questions = Question.query.order_by(Question.id).all()
                paginated_questions = paginate_questions(request, all_questions)

                total_questions = len(all_questions)

                res_body = {}

                res_body['questions'] = paginated_questions
                res_body['total_questions'] = total_questions
                res_body['success'] = True

                return jsonify(res_body)

            except Exception:
                abort(422)

        abort(422)

    @app.route('/api/questions/search', methods=['POST'])
    def search_questions():
        """
        POST '/questions/search'
        - Fetches a dictionary of questions in which the keys are the ids and the values is the corresponding string of the question search term and listing the current category of this questions listed.
        - Request Arguments: An object with a key, question that contains a object of question: question_string key:value pairs.  
        - Returns: 
            Current category of fetched results with id and type values,
            An object with questions of that category, that each contains an object of question id, question category id, question difficulty, question answer, and question text.
            total number of questions and success boolean, as the follwoing sample:
        {
            "current_category": {
                "id": 1,
                "type": "Science"
            },
            "questions": [
                {
                    "answer": "answer2",
                    "category": 1,
                    "difficulty": 1,
                    "id": 2,
                    "question": "question2"
                },
                {
                    "answer": "answer4",
                    "category": 1,
                    "difficulty": 1,
                    "id": 4,
                    "question": "question4"
                }
            ],
            "total_questions": 2,
            "success": true
        }
        """
        total_questions = 0

        try:
            data = request.get_json()
            search_term = data.get('searchTerm', '')

            search_result = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).order_by('id').all()
            paginated_questions = paginate_questions(request, search_result)

            res_body = {}
            total_questions = len(search_result)

            for question in search_result:
                try:
                    questions_categories = Category.query.filter_by(id=question.category).order_by('id').all()
                    current_categories = paginate_categories(request, questions_categories)

                    for category in current_categories:
                        res_body['questions'] = paginated_questions
                        res_body['total_questions'] = total_questions
                        res_body['success'] = True
                        res_body['current_category'] = category

                        return jsonify(res_body)

                except Exception:
                    abort(422)

        except Exception:
            abort(422)

        res_body['questions'] = paginated_questions
        res_body['total_questions'] = total_questions
        res_body['success'] = True
        res_body['current_category'] = None

        return jsonify()

    @app.route('/api/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        """
        GET '/categories/<int:category_id>/questions'
        - Fetches a dictionary of questions based on category, only questions of that category to be shown.
        - Request Arguments: An object with a key, category that contains id of the category of the questions to liest: category_id key:value pairs.  
        - Returns: 
            Current category slected with id and type values,
            An object with questions of that category, that each contains an object of question id, question category id, question difficulty, question answer, and question text.
            total number of questions and success boolean, as the follwoing sample:
        {
            "current_category": {
                "id": 1,
                "type": "Science"
            },
            "questions": [
                {
                    "answer": "answer1",
                    "category": 1,
                    "difficulty": 1,
                    "id": 2,
                    "question": "question1"
                },
                {
                    "answer": "answer3",
                    "category": 1,
                    "difficulty": 1,
                    "id": 4,
                    "question": "question3"
                }
            ],
            "success": true,
            "total_questions": 2
        }
        """
        try:
            category = Category.query.get(category_id)

            if not category:
                abort(404)

            try:
                all_category_questions = Question.query.filter_by(category=category.id).order_by('id').all()
                paginated_category_questions = paginate_questions(request, all_category_questions)

                total_category_questions = len(all_category_questions)

                res_body = {}
                res_body['questions'] = paginated_category_questions
                res_body['total_questions'] = total_category_questions
                res_body['success'] = True
                res_body['current_category'] = category.format()

                return jsonify(res_body)

            except Exception:
                abort(422)

        except Exception:
            abort(422)

    @app.route("/api/quizzes", methods=["POST"])
    def play():
        """
        POST '/quizzes'
        - Fetches a dictionary of questions based on take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
        - Request Arguments: An object with a key, category that contains id of the category of the questions to list: category_id key:value pairs and previous question parameter that contains key of the previous_question of the questions to list: previous_question_string key:value pairs.
        - Returns: 
            Previously selected questions,
            Randomly selected question of the selected category that contains question id, question category id, question difficulty, question answer, and question text.
            a boolean if question found and success boolean, as the follwoing sample:
        {
            "previousQuestions": [1, 4],
            "question": {
                    "answer": "answer3",
                    "category": 1,
                    "difficulty": 1,
                    "id": 4,
                    "question": "question3"
            },
            "foundQuestion": true,
            "success": true
        }
        """
        try:
            req = request.get_json()
            previous_questions = req.get('previous_questions', None)
            quiz_category = req.get('quiz_category', None)

            category = Category.query.get(quiz_category.get('id', 0))

            if not category:
                category = random.choice(Category.query.all())

            try:
                all_category_questions = Question.query.filter(Question.id.notin_(previous_questions)).filter_by(category=category.id).order_by('id').all()
                paginated_category_questions = paginate_questions(request, all_category_questions)

                found_question = True
                question = None

                if len(paginated_category_questions) == 0:
                    found_question = False
                else:
                    question = random.choice(paginated_category_questions)

                return jsonify({
                    'success': True,
                    'question': question,
                    'previousQuestions': previous_questions,
                    'foundQuestion': found_question
                })

            except Exception:
                abort(422)

        except Exception:
            abort(422)


# -------------------------------------------------------------------------------------

    # Error Handlers...

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Method Not Allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Reuest"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({
            "success": False,
            "error": 503,
            "message": "Service Unavailable"
        }), 503


# -------------------------------------------------------------------------------------

    # App...

    return app