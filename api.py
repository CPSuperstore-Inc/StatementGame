from flask import Blueprint, jsonify
import StatementGame.round as round_mngr

import StatementGame.game as game

app = Blueprint('api', __name__, template_folder='templates')

@app.route("/")
def index():
    return "API Not Implemented."


@app.route("/game-members/<game_id>")
def get_game_members(game_id):
    return jsonify(game.get_members(game_id))


@app.route("/get-answers/<rid>")
def get_round_answers(rid):
    return jsonify(round_mngr.get_responses(rid))


@app.route("/is-running/<gid>")
def get_game_status(gid):
    if game.is_game_running(gid):
        return "true"
    return "false"