# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application. 

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 
3. Create an endpoint to handle GET requests for all available categories. 
4. Create an endpoint to DELETE question using a question ID. 
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 
6. Create a POST endpoint to get questions based on category. 
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 
9. Create error handlers for all expected errors including 400, 404, 422 and 500. 



Endpoints
```
GET '/api/categories'
GET '/api/questions'
DELETE '/api/questions/<int:question_id>'
POST '/api/questions'
POST '/api/questions/search'
GET '/api/categories/<int:category_id>/questions'
POST '/api/quizzes'

```


```
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
```

```
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
```

```
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
```

```
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
```

```
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
```

```
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
```

```
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
```



## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```