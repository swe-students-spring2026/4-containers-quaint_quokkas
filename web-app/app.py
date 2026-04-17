"""Simple Flask app that serves the home page."""

from flask import Flask, render_template, jsonify, request
from random import choice
from db import get_latest_result

app = Flask(__name__)

VALID_MOVES = ["rock", "paper", "scissors"]


def get_winner(player, computer):
    """Return the outcome of the round."""
    if player == computer:
        return "tie"
    if (
        (player == "rock" and computer == "scissors")
        or (player == "paper" and computer == "rock")
        or (player == "scissors" and computer == "paper")
    ):
        return "player"
    return "computer"


@app.route("/")
def home():
    """Render the homepage."""
    return render_template("index.html")


@app.route("/play", methods=["POST"])
def play():
    """Play one round using the latest detected gesture."""
    latest = get_latest_result()

    if not latest:
        return render_template("result.html", error="No gesture detected yet.")

    player_move = latest["gesture"]
    computer_move = choice(["rock", "paper", "scissors"])
    winner = get_winner(player_move, computer_move)

    return render_template(
        "result.html",
        player_move=player_move,
        computer_move=computer_move,
        winner=winner,
    )


app.run(host="0.0.0.0", port=8000, debug=True)
