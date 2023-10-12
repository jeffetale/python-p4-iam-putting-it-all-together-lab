#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')
        image_url = json.get('image_url')
        bio = json.get('bio')

        # Check if the user is valid
        if not username or not password:
            return ({'error': 'Username and password are required'}), 422

        # Check if the username already exists
        user = User.query.filter_by(username=username).first()
        if user:
            return ({'error': 'Username already exists'}), 422

        # Create a new user and save it to the database
        user = User(username=username, image_url=image_url, bio=bio)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Save the user's ID in the session object
        session['user_id'] = user.id

        # Return a JSON response with the user's details
        return user.to_dict(), 201

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                return {
                    'id': user.id,
                    'username': user.username,
                    'image_url': user.image_url,
                    'bio': user.bio
                }, 200
            else:
                session.clear()

        return {"error": "Not logged in"}, 401

class Login(Resource):
    def post(self):
        json = request.get_json()
        username = json.get('username')
        password = json.get('password')


        if not username or not password:
            return {'error': 'Username and password are required'}, 401

        user = User.query.filter_by(username=username).first()


        if user and user.check_password(password):

            session['user_id'] = user.id

            return {
                'id': user.id,
                'username': user.username,
                'image_url': user.image_url,
                'bio': user.bio
            }, 200

        return {'error': 'Invalid credentials'}, 401

class Logout(Resource):
    def delete(self):
        session.clear()

        return {}, 204

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id is None:
            return {'error': 'Unauthorized'}, 401

        recipes = Recipe.query.all()

        return {
            'recipes': [
                {
                    'title': recipe.title,
                    'instructions': recipe.instructions,
                    'minutes_to_complete': recipe.minutes_to_complete,
                    'user': {
                        'username': recipe.user.username,
                        'image_url': recipe.user.image_url,
                        'bio': recipe.user.bio
                    }
                }
                for recipe in recipes
            ]
        }, 200
    
    def post(self):
        user_id = session.get('user_id')
        if user_id is None:
            return {'error': 'Unauthorized'}, 401

        json = request.get_json()
        title = json.get('title')
        instructions = json.get('instructions')
        minutes_to_complete = json.get('minutes_to_complete')

        if not title or not instructions or not minutes_to_complete:
            return {'error': 'Title, instructions, and minutes to complete are required'}, 422

        recipe = Recipe(title=title, instructions=instructions, minutes_to_complete=minutes_to_complete, user_id=user_id)
        db.session.add(recipe)
        db.session.commit()

        return {
            'title': recipe.title,
            'instructions': recipe.instructions,
            'minutes_to_complete': recipe.minutes_to_complete,
            'user': {
                'username': recipe.user.username,
                'image_url': recipe.user.image_url,
                'bio': recipe.user.bio
            }
        }, 201

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
