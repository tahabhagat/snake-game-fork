from dataclasses import dataclass
from flask import Flask, request, jsonify, Response, Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import datetime
from waitress import serve
from flask_cors import CORS
from functools import wraps
import json
import base64
import time

import global_variables


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = global_variables.SQLALCHEMY_DATABASE_URI
CORS(app, resources={r"/*": {"origins": global_variables.CORS_URLS}})


# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///score.db"
# CORS(app)


db = SQLAlchemy(app)
# Create Blueprint for normal APIs
normal_api_bp = Blueprint(
    "normal_api", __name__, url_prefix=global_variables.URL_PREFIX + "/api"
)

# Create Blueprint for SSE/Stream APIs
sse_api_bp = Blueprint(
    "sse_api", __name__, url_prefix=global_variables.URL_PREFIX + "/stream"
)


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
    time_taken_seconds = db.Column(db.Integer)

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
    # Print all headers
    headers = request.headers
    # for header, value in headers.items():
    #     print(f"{header}: {value}")
    if "X-Forwarded-For" in headers:
        # If behind a proxy, use the first IP in the X-Forwarded-For list
        return headers["X-Forwarded-For"].split(",")[0]
    elif "X-Real-Ip" in headers:
        return headers["X-Real-Ip"]
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

        try:
            request_body = request.get_json()
            username = request_body["username"]
            score = request_body["score"]
            time_taken_seconds = request_body["timeTakenSeconds"]
        except Exception as e:
            return jsonify({"error": "Bad Request", "message": "Field missing"}), 400

        current_time = datetime.datetime.now().timestamp()
        client_ip = get_client_ip()

        encoded_data = request.headers.get("Accept-Connection")
        if not encoded_data:
            print(
                f"Suspicious Activity: IP {client_ip} detected possible attempt to direct access the API. | "
                f"Request body: {json.dumps(request_body)} | "
                f"No 'Accept-Connection' header."
            )
            request_body["timeTakenSeconds"] = float(time_taken_seconds) + 1
            return jsonify(request_body)

        try:
            key = f"{username}~{score}~ty~{time_taken_seconds}"
            decoded_bytes = base64.b64decode(encoded_data)
            decoded_str = decoded_bytes.decode("utf-8")
            data = base64.b64decode(xor_cipher(decoded_str, key))
            json_data = json.loads(data)
        except Exception as e:
            print(
                f"Suspicious Activity: IP {client_ip} detected possible request body manipulation. | "
                f"Request body: {json.dumps(request_body)} | "
                f"Encoded data: {encoded_data}."
            )
            request_body["timeTakenSeconds"] = float(time_taken_seconds) + 1
            return jsonify(request_body)

        timestamp_from_request = int(json_data["timestamp"])
        if abs(current_time - timestamp_from_request) <= 60:
            # Valid request
            return f(*args, **kwargs)

        print(
            f"Suspicious Activity: IP {client_ip} detected a potential replay attack. | "
            f"Request body: {json.dumps(request_body)}. | "
            f"Request timestamp: {timestamp_from_request}, Current time: {current_time}. "
        )

        request_body["timeTakenSeconds"] = float(time_taken_seconds) + 1
        return jsonify(request_body)

    return decorated_function


@normal_api_bp.route("/ping")
def ping():
    return "pong"


@normal_api_bp.route("/score", methods=["POST"])
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


def get_top_scoreboard_service(page, per_page, username):
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

    return [
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


@normal_api_bp.route("/score")
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
        {
            "data": [
                get_scoreboard_pair(user=user, score=score) for user, score in result
            ]
        }
    )


@normal_api_bp.route("/personal-best")
def get_user_top_score():

    username = request.args.get("username", None)

    query = (
        db.session.query(
            User,
            Score.score.label("max_score"),
            Score.scored_at,
            Score.time_taken_seconds,
        )
        .join(Score, User.user_id == Score.user_id)
        .filter(User.username == username)  # Filter by the user's name
        .order_by(Score.score.desc(), Score.time_taken_seconds.asc())
        .limit(1)  # Limit to just the top score
    )

    result = query.all()

    if result:
        user, score, scored_at, time_taken_seconds = result[0]
    else:
        user = User(username=username)
        score = 0
        scored_at = None
        time_taken_seconds = None

    data = get_scoreboard_pair(
        user=user,
        score=Score(
            scored_at=scored_at,
            score=score,
            time_taken_seconds=time_taken_seconds,
        ),
    )
    return jsonify(
        {
            "data": data,
        }
    )


@normal_api_bp.route("/top-score")
def get_top_scoreboard():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    username = request.args.get("username", None)

    return jsonify(
        {
            "data": get_top_scoreboard_service(
                page=page, per_page=per_page, username=username
            )
        }
    )


@sse_api_bp.route("/top-score")
def stream_scores():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    username = request.args.get("username", None)

    def event_stream():
        last_data = None
        while True:
            with app.app_context():
                current_data = get_top_scoreboard_service(
                    page=page, per_page=per_page, username=username
                )
                if current_data != last_data:
                    data = {
                        "data": current_data,
                        "timestamp": str(
                            datetime.datetime.now(
                                datetime.timezone(
                                    datetime.timedelta(hours=5, minutes=30)
                                )
                            )
                        ),
                    }
                    last_data = current_data
                    yield f"data: {json.dumps(data)}\n\n"

            # Wait for either 5 seconds or a new score update
            time.sleep(global_variables.GET_SCORES_POLLING_RATE_SECONDS)

    return Response(event_stream(), mimetype="text/event-stream")


# Register the blueprints
app.register_blueprint(normal_api_bp)  # Register normal API blueprint
app.register_blueprint(sse_api_bp)  # Register SSE API blueprint

if __name__ == "__main__":
    # app.run("0.0.0.0", debug=True)
    print("BOOTING UP THE REACTORS!!!")
    host = "0.0.0.0"
    port = 8000
    print(f"STARTING WEBSERVER ON {host}:{port}")
    serve(app=app, host=host, port=port, threads=25, connection_limit=500)
