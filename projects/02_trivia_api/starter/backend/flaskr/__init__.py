# ------------------------------------- Imports ------------------------------------------------

import traceback

from flask import Flask, request, abort, jsonify
from flask_cors import CORS
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
        return response

# -------------------------------------------------------------------------------------

    # Helpers...

    def paginate_categories(request, all_categories):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * CATEGORIES_PER_PAGE
        end = start + CATEGORIES_PER_PAGE

        categories = [category.format() for category in all_categories]
        current_categories = categories[start:end]

        return current_categories

    def paginate_questions(request, all_questions):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in all_questions]
        current_questions = questions[start:end]

        return current_questions


# -------------------------------------------------------------------------------------

    # Routes...

    @app.route('/api/categories')
    def retrieve_categories():
        try:
            all_categories = Category.query.order_by(Category.id).all()
            current_categories = paginate_categories(request, all_categories)

            total_categories = len(all_categories)

            if total_categories == 0:
                abort(404)

            res_body = {}

            res_body['categories'] = current_categories
            res_body['total_categories'] = total_categories
            res_body['success'] = True

            return jsonify(res_body)

        except Exception:
            abort(500)

    @app.route('/api/questions')
    def retrieve_questions():
        try:
            all_questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, all_questions)
            categories = Category.query.all()

            total_questions = len(all_questions)

            # if total_questions == 0:
            #     abort(404)

            res_body = {}

            res_body['categories'] = [category.type for category in categories]
            res_body['questions'] = current_questions
            res_body['total_questions'] = total_questions
            res_body['success'] = True

            return jsonify(res_body)

        except Exception as e:
            traceback.print_exc()
            abort(500)

    @app.route('/api/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)

            if question is None:
                abort(404)

            question.delete()

            all_questions = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, all_questions)

            total_questions = len(all_questions)

            # if total_questions == 0:
            #     abort(404)

            res_body = {}

            res_body['questions'] = current_questions
            res_body['total_questions'] = total_questions
            res_body['deleted'] = question_id
            res_body['success'] = True

            return jsonify(res_body)

        except Exception:
            abort(422)

    return app