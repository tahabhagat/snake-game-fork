from dataclasses import dataclass
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import datetime
from waitress import serve
from flask_cors import CORS
from functools import wraps
import json
import base64

app = Flask(
    __name__,
)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////data/score.db"
CORS(app, resources={r"/*": {"origins": "https://lockhart07.github.io"}})


# CORS(app)
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///score.db"


db = SQLAlchemy(app)


@dataclass
class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"User(user_id={self.user_id}, username='{self.username}')"

    def __str__(self):
        return f"{self.username} (ID: {self.user_id})"


class Score(db.Model):
    __tablename__ = "scores"
    score_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    score = db.Column(db.Integer, nullable=False)
    scored_at = db.Column(db.String)
    time_taken_seconds = db.Column(db.Numeric)

    def __repr__(self):
        return f"Score(score_id={self.score_id}, user_id={self.user_id}, score={self.score}, scored_at={self.scored_at}, time_taken_seconds={self.time_taken_seconds})"

    def __str__(self):
        return f"{self.score} scored by user {self.user_id} at {self.scored_at} ({self.time_taken_seconds} seconds)"


# Create the tables
with app.app_context():
    db.create_all()


def get_scoreboard_pair(user: User, score: Score):
    return {
        "username": user.username,
        "score": score.score,
        "timeTakenSeconds": score.time_taken_seconds,
        "scoredAt": score.scored_at,
    }


def get_client_ip():
    """Function to retrieve the client's IP address."""
    if "X-Forwarded-For" in request.headers:
        # If behind a proxy, use the first IP in the X-Forwarded-For list
        return request.headers["X-Forwarded-For"].split(",")[0]
    else:
        # Direct access (not behind a proxy)
        return request.remote_addr


def xor_cipher(data, key):
    result = "".join(
        chr(ord(data[i]) ^ ord(key[i % len(key)])) for i in range(len(data))
    )
    return result


def validate_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_time = datetime.datetime.now().timestamp()
        try:
            request_body = request.get_json()
            username = request_body["username"]
            score = request_body["score"]
            time_taken_seconds = request_body["timeTakenSeconds"]
        except Exception as e:
            return jsonify({"error": "Bad Request", "message": "Field missing"}), 400

        try:
            encoded_data = request.headers.get("Accept-Connection")

            key = f"{username}~{score}~ty~{time_taken_seconds}"
            decoded_bytes = base64.b64decode(encoded_data)
            decoded_str = decoded_bytes.decode("utf-8")
            data = base64.b64decode(xor_cipher(decoded_str, key))
            json_data = json.loads(data)

            timestamp_from_request = int(json_data["timestamp"])
            if abs(current_time - timestamp_from_request) <= 15:
                return f(*args, **kwargs)

            request_body["timeTakenSeconds"] = float(time_taken_seconds) + 1
        except Exception as e:
            request_body["timeTakenSeconds"] = float(time_taken_seconds) + 1

        # Get client IP address using the custom function
        client_ip = get_client_ip()

        print(
            f"Suspicious Activity: IP {client_ip} with request body: {json.dumps(data)}"
        )
        return jsonify(request_body)

    return decorated_function


@app.route("/ping")
@validate_request
def ping():
    # return render_template("hello.html", name=name)
    return "pong"


@app.route("/api/score", methods=["POST"])
@validate_request
def save_score():
    try:
        request_body = request.get_json()
        username = request_body["username"]
        score = request_body["score"]
        time_taken_seconds = request_body["timeTakenSeconds"]
    except Exception as e:
        return jsonify({"error": "Bad Request", "message": "Field missing"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        db.session.add(user)
        db.session.commit()

    score = Score(
        user_id=user.user_id,
        score=score,
        scored_at=datetime.datetime.now(datetime.UTC).isoformat(),
        time_taken_seconds=time_taken_seconds,
    )

    db.session.add(score)
    db.session.commit()

    return jsonify(request_body)


@app.route("/api/score")
def get_scoreboard():

    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    username = request.args.get("username", None)

    query = db.session.query(User, Score).join(Score, User.user_id == Score.user_id)
    if username:
        query = query.filter(User.username.like(f"%{username}%"))
    query = query.order_by(Score.score.desc(), Score.scored_at.asc()).slice(
        page - 1, per_page
    )
    result = query.all()

    return jsonify(
        [get_scoreboard_pair(user=user, score=score) for user, score in result]
    )


@app.route("/api/top-score")
def get_top_scoreboard():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    username = request.args.get("username", None)

    query = (
        db.session.query(
            User,
            func.max(Score.score).label("max_score"),
            Score.scored_at,
            Score.time_taken_seconds,
        )
        .join(Score, User.user_id == Score.user_id)
        .group_by(User.user_id)
    )

    if username:
        query = query.filter(User.username.like(f"%{username}%"))
    query = query.order_by(Score.score.desc(), Score.scored_at.asc()).slice(
        page - 1, per_page
    )

    result = query.all()

    return jsonify(
        [
            get_scoreboard_pair(
                user=user,
                score=Score(
                    scored_at=scored_at,
                    score=score,
                    time_taken_seconds=time_taken_seconds,
                ),
            )
            for user, score, scored_at, time_taken_seconds in result
        ]
    )


if __name__ == "__main__":
    # app.run("0.0.0.0", debug=True)
    print("BOOTING UP THE REACTORS!!!")
    host = "0.0.0.0"
    port = 8000
    print(f"STARTING WEBSERVER ON {host}:{port}")
    serve(app=app, host=host, port=port, threads=10)
