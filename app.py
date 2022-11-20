from flask import Flask
from flask_restful import Api, Resource, abort, reqparse, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import os

base_dir = os.path.dirname(os.path.realpath(__file__))
app = Flask(__name__)


# The configuration for the URI of the database, the myblog.db is the name of this project's database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'my_api.db')
# The configuration for the track modification
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# The configuration to set up a secret key to strengthen the security of your database
app.config["SECRET_KEY"] = '026b0eb800ec2934fb5cf2e7'

api = Api(app)
db = SQLAlchemy(app)
db.init_app(app)


class TodoModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'Title >> {self.title}'


todo_post_args = reqparse.RequestParser()
todo_post_args.add_argument('title', type=str, help='Title is required', required=True)
todo_post_args.add_argument('body', type=str, help='Body is required', required=True)

todo_put_args = reqparse.RequestParser()
todo_put_args.add_argument('title', type=str)
todo_put_args.add_argument('body', type=str)

resource_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'body': fields.String
}


class Todo(Resource):
    def get(self):
        all_todo = {}
        todos = TodoModel.query.filter().all()
        if not todos:
            abort(404, message='No Todo found')
        for todo in todos:
            all_todo[todo.id] = {
                'title': todo.title,
                'body': todo.body
            }
        return all_todo, 200

    def delete(self):
        todos = TodoModel.query.filter().all()
        if not todos:
            abort(404, message='No Todo found')
        for todo in todos:
            db.session.delete(todo)
            db.session.commit()
        return {'message': 'Todos cleared'}


class EachTodo(Resource):

    @marshal_with(resource_fields)
    def get(self, todo_id):
        todo = TodoModel.query.filter_by(id=todo_id).first()
        if not todo:
            abort(404, message='Todo with such id does not exist')
        return todo, 200

    @marshal_with(resource_fields)
    def post(self, todo_id):
        todo = TodoModel.query.filter_by(id=todo_id).first()
        args = todo_post_args.parse_args()
        if todo:
            abort(409, message='Todo with that id already exist')
        add_todo = TodoModel(id=todo_id, title=args['title'], body=args['body'])
        db.session.add(add_todo)
        db.session.commit()
        return add_todo, 201

    @marshal_with(resource_fields)
    def put(self, todo_id):
        todo = TodoModel.query.filter_by(id=todo_id).first()
        args = todo_put_args.parse_args()
        if not todo:
            abort(404, message='Todo with such id does not exist')
        if args['title']:
            todo.title = args['title']
        if args['body']:
            todo.body = args['body']
        db.session.commit()
        return todo

    def delete(self, todo_id):
        todo = TodoModel.query.filter_by(id=todo_id).first()
        if not todo:
            abort(404, message='Todo with such id doe not exist')
        db.session.delete(todo)
        db.session.commit()
        return {'message': 'Todo has been deleted'}


api.add_resource(Todo, '/todos/')
api.add_resource(EachTodo, '/todos/<int:todo_id>')


if __name__ == "__main__":
    app.run(debug=True)
