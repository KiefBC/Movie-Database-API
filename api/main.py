from flask_restful import reqparse, Resource
from flask import jsonify, make_response, Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

app = Flask(__name__)
api = Api(app)
app.config.update({
    'DEBUG': True,
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///database.db',
    'SQLALCHEMY_TRACK_MODIFICATIONS': False
})
db = SQLAlchemy(app)

movie_parser = reqparse.RequestParser()
movie_parser.add_argument('name', type=str, required=True, help='Name is required')
movie_parser.add_argument('year', type=str, required=True, help='Year is required')
movie_parser.add_argument('genre', type=str, required=True, help='Genre is required')

human_parser = reqparse.RequestParser()
human_parser.add_argument('name', type=str, required=True, help='Name is required')
human_parser.add_argument('year_born', type=str, required=True, help='Year is required')


class MovieModel(db.Model):
    """Model for the movies table"""
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    genre = db.Column(db.String(10), nullable=False)
    year = db.Column(db.String(80), nullable=False)
    humans = db.relationship('HumanInMovie', backref='movie')

    def __repr__(self):
        return f"Movie(name = {self.name}, genre = {self.genre}, year = {self.year})"

    def __str__(self):
        return f"Movie(name = {self.name}, genre = {self.genre}, year = {self.year})"


class HumanModel(db.Model):
    """The Humans in our Life"""
    __tablename__ = "humans"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    year_born = db.Column(db.Integer, nullable=False)
    movies = db.relationship('HumanInMovie', backref='human')

    def __repr__(self):
        return f"Human(name = {self.name}, year_born = {self.year_born})"

    def __str__(self):
        return f"Human(name = {self.name}, year_born = {self.year_born})"


class HumanInMovie(db.Model):
    """Humans in the Movies!"""
    __tablename__ = "humans_in_movies"

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String, nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    human_id = db.Column(db.Integer, db.ForeignKey('humans.id'), nullable=False)

    def __repr__(self):
        return f"HumanInMovie(role = {self.role}, movie_id = {self.movie_id}, human_id = {self.human_id})"

    def __str__(self):
        return f"HumanInMovie(role = {self.role}, movie_id = {self.movie_id}, human_id = {self.human_id})"


with app.app_context():
    db.drop_all()
    db.create_all()


class MoviesResource(Resource):
    def get(self):
        movies = MovieModel.query.all()
        movie_results = []
        for movie in movies:
            movie_data = {
                "id": movie.id,
                "name": movie.name,
                "genre": movie.genre,
                "year": movie.year
            }
            movie_results.append(movie_data)
        return make_response(jsonify({"movies": movie_results}), 200)

    def post(self):
        args = movie_parser.parse_args()
        movie = MovieModel(
            name=args['name'],
            year=args['year'],
            genre=args['genre']
        )
        db.session.add(movie)
        db.session.commit()
        movies_response = {"id": movie.id, "name": movie.name, "genre": movie.genre, "year": movie.year}
        return make_response(jsonify(movies_response), 200)


class HumansResource(Resource):
    def get(self):
        humans = HumanModel.query.all()
        human_results = []
        for human in humans:
            human_data = {
                "id": human.id,
                "name": human.name,
            }
            human_results.append(human_data)
        return make_response(jsonify({"humans": human_results}), 200)

    def post(self):
        args = human_parser.parse_args()
        human = HumanModel(
            name=args['name'],
            year_born=args['year_born']
        )
        db.session.add(human)
        db.session.commit()
        humans_response = {"id": human.id, "name": human.name, "year_born": human.year_born}
        return make_response(jsonify(humans_response), 200)


class MovieResource(Resource):
    def get(self, id):
        movie = MovieModel.query.filter_by(id=id).first()
        response = {"movie": {
            "id": movie.id,
            "name": movie.name,
            "genre": movie.genre,
            "year": movie.year
        }}
        return make_response(jsonify(response), 200)


class HumanResource(Resource):
    def get(self, id):
        human = HumanModel.query.filter_by(id=id).first()
        response = {"human": {
            "id": human.id,
            "name": human.name,
            "year_born": human.year_born
        }}
        return make_response(jsonify(response), 200)


api.add_resource(MoviesResource, '/movies')
api.add_resource(MovieResource, '/movies/<int:id>')
api.add_resource(HumansResource, '/humans')
api.add_resource(HumanResource, '/humans/<int:id>')

if __name__ == "__main__":
    app.run()
