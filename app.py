# Import all packages/dependencies for this project
from flask import Flask
from flask_restful import Api, Resource, abort, reqparse, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import os

base_dir = os.path.dirname(os.path.realpath(__file__))
# Instantiate Flask
app = Flask(__name__)

"""The live link"""
# Link : https://todo1api.herokuapp.com/

# The configuration for the URI of the database, the my_api.db is the name of this project's database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'my_api.db')
# The configuration for the track modification
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# The configuration to set up a secret key to strengthen the security of your database
app.config["SECRET_KEY"] = '026b0eb800ec2934fb5cf2e7'

# Instantiate Api
api = Api(app)
# Instantiate Database
db = SQLAlchemy(app)
db.init_app(app)


# Creating thr database models
class TodoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(50), nullable=False)

    # This is a representation method for the model created
    def __repr__(self):
        return f'Title >> {self.title}'


# Regparse for posting an item into the database
todo_post_args = reqparse.RequestParser()
# this gets the value for the key 'title' from the input, the field is required. If you leave it empty, the string assigned to the help gets displayed to you
todo_post_args.add_argument('title', type=str, help='Title is required', required=True)
# this gets the value for the key 'body' from the input, the field is required. If you leave it empty, the string assigned to the help gets displayed to you
todo_post_args.add_argument('body', type=str, help='Body is required', required=True)

# Regparse for updating an item into the database
todo_put_args = reqparse.RequestParser()
todo_put_args.add_argument('title', type=str)
todo_put_args.add_argument('body', type=str)

# This is the resource field(schema) which the response will be serialized with
# this indicates that the id's field is an integer while the other two fields are string fields
resource_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'body': fields.String
}


# first class
class Todo(Resource):
    # marshal with serializes the returns in the resource_fields format
    @marshal_with(resource_fields)
    # The get function
    def get(self):
        # query the database for all the todos in the database
        todos = TodoModel.query.filter().all()
        # Check if the database is empty
        if not todos:
            # If the database is empty, abort the process with a status code 404 and the message 'No todo found'
            abort(404, message='No Todo found')
        # If the database is not empty, return the todos in the database
        return todos, 200

    @marshal_with(resource_fields)
    # Te post function
    def post(self):
        # args gets the todo information from the input
        args = todo_post_args.parse_args()
        # using the information from the input to instantiate the TodoModel
        add_todo = TodoModel(title=args['title'], body=args['body'])
        # adding the instantiation into the database
        db.session.add(add_todo)
        # committing the changes into the database
        db.session.commit()
        # when the todo has been added, return the added todo
        return add_todo, 201

    # The delete function
    def delete(self):
        # query the database for all the todos in the database
        todos = TodoModel.query.filter().all()
        # Check if the database is empty
        if not todos:
            # If the database is empty, abort the process with a status code 404 and the message 'No todo found'
            abort(404, message='No Todo found')
        # if the database is not empty, loop through the information in the database
        for todo in todos:
            # delete each information from the database
            db.session.delete(todo)
            # commit each changes after delete back to the database
            db.session.commit()
        # after a successful operation, returns this message in a json format
        return {'message': 'Todos cleared'}


# the second class for each todo using their id
class EachTodo(Resource):

    @marshal_with(resource_fields)
    # the get function with the todo id passed into it
    def get(self, todo_id):
        # query the database using the passed todo id as the id
        todo = TodoModel.query.filter_by(id=todo_id).first()
        # if todo does not exist
        if not todo:
            # abort the process with a message if the todo does not exist
            abort(404, message='Todo with such id does not exist')
        # if the todo does exist, return the todo
        return todo, 200

    @marshal_with(resource_fields)
    # the update function with the todo id passed into it
    def put(self, todo_id):
        # query the database using the passed todo id as the id
        todo = TodoModel.query.filter_by(id=todo_id).first()
        # args gets the todo for this particular id from the input
        args = todo_put_args.parse_args()
        # check if the todo does not exist
        if not todo:
            # if the todo does not exist, abort thr process with this status code and message
            abort(404, message='Todo with such id does not exist')
        # if the todo exist
        # check if the args has a key called 'title'
        if args['title']:
            # if yes, then assign the value of thr key to the title column of that particular todo, thereby replacing it
            todo.title = args['title']
        # check if the args has a key called 'body'
        if args['body']:
            # if yes, then assign the value of thr key to the body column of that particular todo, thereby replacing it
            todo.body = args['body']
        # commit the changes back to the database
        db.session.commit()
        # and return the updated todo
        return todo

    # the delete function with the todo id passed into it
    def delete(self, todo_id):
        # query the database using the passed todo id as the id
        todo = TodoModel.query.filter_by(id=todo_id).first()
        # check if the todo does not exist
        if not todo:
            # abort the process with a message and status code if the todo does not exist
            abort(404, message='Todo with such id doe not exist')
        # if the todo exist, delete it from the database
        db.session.delete(todo)
        # then commit the changes to the database
        db.session.commit()
        # after the deletion, return this message
        return {'message': 'Todo has been deleted'}


# the url to for the first class
api.add_resource(Todo, '/')
# the url for the second class
api.add_resource(EachTodo, '/<int:todo_id>')


if __name__ == "__main__":
    app.run(debug=True)
