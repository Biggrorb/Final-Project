import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from dotenv import load_dotenv

load_dotenv()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = os.getenv('test_database_name')
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            os.getenv('test_database_user'),
            os.getenv('test_database_password'),
            os.getenv('test_database_host'), 
            self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Does this work?',
            'answer': 'I hope so!',
            'category': 1,
            'difficulty': 1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertGreater(len(data['categories']), 0)
        self.assertGreater(data['total_categories'],0)


    def test_get_questions(self):
        res = self.client().get('/questions')
        data= json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertGreater(len(data['questions']), 0)
        self.assertGreater(data['total_questions'], 0)
        self.assertGreater(len(data['categories']), 0)


    def test_delete_questions(self):
        res = self.client().delete('questions/1')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(question, None)
    

    def test_post_questions(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)


    def test_post_search_questions(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'What'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertGreater(len(data['questions']),0)

    def test_get_questions_by_category_id(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)

    
    # def test_post_quizzes(self):
    #     res = self.client().post('/quizzes',json={'previous_questions':[],'quiz_category':[]})
    #     data = json.loads(res.data)

    #     self.assertEqual(res.status_code,200)
        
        

    def test_422_unprocessable(self):
        res = self.client().post('/quizzes',json={'previous_questions':[],'quiz_catergory':[]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code,422)
        

   
    def test_500_server_error(self):
        res = self.client().post('/questions',
        content_type='application/json', data = '11111')

        data= json.loads(res.data)

        self.assertEqual(res.status_code,500)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'], 'server_error')
   

    def test_405_method_not_allowed(self):
        res= self.client().post('/categories')
        data= json.loads(res.data)

        self.assertEqual(res.status_code,405)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['message'],'method_not_allowed')


    def test_404_not_found(self):
        res = self.client().get('/categories/history')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'],'resource not found')


    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()