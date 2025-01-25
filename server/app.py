from flask import Flask, jsonify, request, session, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, User, Article

app = Flask(__name__)
app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

class ClearSession(Resource):
    def get(self):
        session.clear()
        return {}, 204

class Login(Resource):
    def post(self):
        username = request.json.get('username')
        user = User.query.filter_by(username=username).first()
        if user:
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {'error': 'Invalid username'}, 401

class Logout(Resource):
    def delete(self):
        session.clear()
        return {}, 204

class MemberOnlyIndex(Resource):
    def get(self):
        if not session.get('user_id'):
            return {'error': 'Unauthorized access'}, 401
        articles = Article.query.filter_by(is_member_only=True).all()
        return [article.to_dict() for article in articles], 200

class MemberOnlyArticle(Resource):
    def get(self, id):
        if not session.get('user_id'):
            return {'error': 'Unauthorized access'}, 401
        article = Article.query.filter_by(id=id, is_member_only=True).first()
        if article:
            return article.to_dict(), 200
        return {'error': 'Article not found or not a member-only article'}, 404

api.add_resource(ClearSession, '/clear')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(MemberOnlyIndex, '/members_only_articles')
api.add_resource(MemberOnlyArticle, '/members_only_articles/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
