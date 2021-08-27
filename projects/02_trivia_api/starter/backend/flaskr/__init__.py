from io import open_code
import os
from flask import Flask, json, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy import func

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def paginate_questions(request,selection):
  page = request.args.get('page',1,type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  current_questions = selection[start:end]
  
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  # '''
  # @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  # '''
  CORS(app, resources={r"/*": {'origins': '*'}})
  # '''
  # @TODO: Use the after_request decorator to set Access-Control-Allow
  # '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
      return response
  # '''
  # @TODO: 
  # Create an endpoint to handle GET requests 
  # for all available categories.
  # '''
  @app.route('/categories', methods= ['GET'])
  def get_categories():
    categories = Category.query.all()
    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type
    
    return jsonify({
      'success':True,
      'categories': categories_dict,
      'total_categories':len(categories_dict)
    })



  # '''
  # @TODO: 
  # Create an endpoint to handle GET requests for questions, 
  # including pagination (every 10 questions). 
  # This endpoint should return a list of questions, 
  # number of total questions, current category, categories. 
  
  # TEST: At this point, when you start the application
  # you should see questions and categories generated,
  # ten questions per page and pagination at the bottom of the screen for three pages.
  # Clicking on the page numbers should update the questions. 
  # '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    selection=Question.query.all()
    questions=paginate_questions(request,selection)
    categories=Category.query.all()
    categories_dict = {}
    for category in categories:
      categories_dict[category.id] = category.type
    totalquestions=len(selection)
    formatted_questions=[]
    for question in questions:
      one_question = question.format()
      formatted_questions.append(one_question)


    return jsonify({
      'success':True,
      'questions':formatted_questions,
      'total_questions':totalquestions,
      'categories':categories_dict,
      'current_category': None
    })

  # '''
  # @TODO: 
  # Create an endpoint to DELETE question using a question ID. 

  # TEST: When you click the trash icon next to a question, the question will be removed.
  # This removal will persist in the database and when you refresh the page. 
  # '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      Question.query.filter_by(id=question_id).delete()
      db.session.commit()
    except:
      db.session.rollback()
    finally:
      db.session.close()
    return jsonify({
      'success':True,
      'id':question_id,
    })
  # '''
  # @TODO: 
  # Create an endpoint to POST a new question, 
  # which will require the question and answer text, 
  # category, and difficulty score.

  # TEST: When you submit a question on the "Add" tab, 
  # the form will clear and the question will appear at the end of the last page
  # of the questions list in the "List" tab.  
  # '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    data = request.get_json()
    question=data['question']
    answer=data['answer']
    category=data['category']
    difficulty=data['difficulty']
    myquestion = Question(question,answer,category,difficulty)
    myquestion.insert()
    
    return jsonify({
      'success':True,
      'id':myquestion.id
    })
    

  # '''
  # @TODO: 
  # Create a POST endpoint to get questions based on a search term. 
  # It should return any questions for whom the search term 
  # is a substring of the question. 

  # TEST: Search by any phrase. The questions list will update to include 
  # only question that include that string within their question. 
  # Try using the word "title" to start. 
  # '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    questions=Question.query.filter(func.lower(Question.question).contains(request.get_json()['searchTerm'].lower())).all()
    questions_dict={
      'totalQuestions':len(questions),
      'questions':[]
    }
    for question in questions:
      questions_data= {
        'id': question.id,
        'question':question.question,
        'answer': question.answer,
        'difficulty':question.difficulty,
        'category':question.category
      }
      questions_dict['questions'].append(questions_data)
    print(questions_dict['questions'])
    return jsonify({
      'success':True,
      'questions':questions_dict['questions'],
      'totalQuestions':questions_dict['totalQuestions'],
      'currentCategory':None
    })

  # '''
  # @TODO: 
  # Create a GET endpoint to get questions based on category. 

  # TEST: In the "List" tab / main screen, clicking on one of the 
  # categories in the left column will cause only questions of that 
  # category to be shown. 
  # '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_category_questions(category_id):
    questions=Question.query.filter_by(category=category_id).all()
    questions_dict={
      'totalQuestions':len(questions),
      'questions':[]
    }
    for question in questions:
      questions_data= {
        'id': question.id,
        'question':question.question,
        'answer': question.answer,
        'difficulty':question.difficulty,
        'category':question.category
      }
      questions_dict['questions'].append(questions_data)
    print(questions_dict['questions'])
    return jsonify({
      'success':True,
      'questions':questions_dict['questions'],
      'totalQuestions':questions_dict['totalQuestions'],
      'currentCategory':None
    })


  # '''
  # @TODO: 
  # Create a POST endpoint to get questions to play the quiz. 
  # This endpoint should take category and previous question parameters 
  # and return a random questions within the given category, 
  # if provided, and that is not one of the previous questions. 

  # TEST: In the "Play" tab, after a user selects "All" or a category,
  # one question at a time is displayed, the user is allowed to answer
  # and shown whether they were correct or not. 
  # '''
  @app.route('/quizzes', methods=['POST'])
  def play_quizzes():
    data = request.get_json()
    previous_questions = data.get("previous_questions",[])
    quiz_category = data.get("quiz_category", None)
    print(previous_questions)
    try:
      category_id = int(quiz_category["id"])
      
      if category_id == 0:
        quiz = Question.query.all()

      else:
        quiz = Question.query.filter_by(category=category_id).all()
      if not quiz:
        return abort(422)
      playing = []
      for question in quiz:
        if question.id not in previous_questions:
          playing.append(question.format())
      if len(playing) !=0:
        result = random.choice(playing)
        return jsonify({"question":result})
      else:
        return jsonify({})
    except:
      abort(422)
               

    
  # '''
  # @TODO: 
  # Create error handlers for all expected errors 
  # including 404 and 422. 
  # '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error':404,
      'message': 'resource not found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success':False,
      'error':422,
      'message': 'unprocessable'
    }),422

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error':405,
      'message':'method_not_allowed'
    }),405
  
  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      'success':False,
      'error':500,
      'message':"server_error"
    }),500
  return app

    