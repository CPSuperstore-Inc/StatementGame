import StatementGame.question as question
import StatementGame.response as response
import StatementGame.round as round_mngr
import StatementGame.utils as utils
from flask import Flask, render_template, request, session, redirect, flash

import StatementGame.game as game
import StatementGame.player as player
from StatementGame.api import app as api
from StatementGame.filters import app as filters
from StatementGame.security import SECRET_KEY

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(filters)


@app.context_processor
def inject_dict_for_all_templates():
    return {
        "development": True
    }


@app.route("/")
def index():
    default_name = ""
    if "name" in request.args:
        default_name = request.args["name"]
    return render_template("index.twig", default_name=default_name)


@app.route("/newGame", methods=["POST"])
def new_game():
    code = game.new_game()
    session["id"] = player.join_game(request.form["name"], code)
    return redirect("/lobby")


@app.route("/joinGame", methods=["POST"])
def join_game():
    code = request.form["code"]
    g = game.get_game(request.form["code"].lower().replace(" ", ""))
    if g is None:
        flash("Game Code: {} Does Not Exist!".format(code))
        return redirect("/")

    session["id"] = player.join_game(request.form["name"], g["id"])
    return redirect("/lobby")


@app.route("/lobby")
def lobby():
    return render_template("lobby.twig", game=player.get_game_info(session["id"]))


@app.route("/gameEnded/<gid>")
def game_ended(gid):
    flash("The game has ended! Have a nice day :)")
    return redirect("/gameSummary/{}".format(gid))


@app.route("/round/<rid>", methods=["GET", "POST"])
def round_play(rid):
    if request.method == "GET":
        g = player.get_game_info(session["id"])
        try:
            game.remove_code(g["id"])
        except TypeError:
            flash("The game has ended! Have a nice day :)")
            return redirect("/gameSummary/{}".format(player.get_player_info(session["id"])["game"]))

        player.select_alien(g["id"])
        round_data = round_mngr.get_round(rid, g["id"])
        alien = player.is_alien(session["id"])

        if alien:
            q = question.get_question(round_data["falseStatement"])
        else:
            q = question.get_question(round_data["regularStatement"])

        return render_template("prompt.twig", round=round_data, alien=alien, question=q, rid=rid, game_id=g["id"])

    if request.method == "POST":
        g = player.get_game_info(session["id"])

        r = request.form["response"]

        if not utils.is_answer_legal(r):
            flash("The answer you have entered is an illegal answer. Please try again.")
            return redirect("/round/{}".format(rid))

        try:
            response.set_response(
                round_mngr.get_round(rid, g["id"])["id"], session["id"], r
            )
            return redirect("/response/{}".format(rid))
        except TypeError:
            flash("The game has ended! Have a nice day :)")
            return redirect("/gameSummary/{}".format(player.get_player_info(session["id"])["game"]))


@app.route("/response/<rid>")
def responses(rid):
    g = player.get_game_info(session["id"])
    try:
        player.select_alien(g["id"])
    except TypeError:
        flash("The game has ended! Have a nice day :)")
        return redirect("/gameSummary/{}".format(player.get_player_info(session["id"])["game"]))
    round_data = round_mngr.get_round(rid, g["id"])
    alien = player.is_alien(session["id"])
    q = question.get_question(round_data["regularStatement"])
    players = game.get_members(g["id"])

    return render_template("responses.twig", round=round_data, alien=alien, question=q, rid=rid, player_count=len(players))


@app.route("/endGame/<gid>")
def end_game(gid):
    game.delete_game(gid)
    return redirect("/gameSummary/{}".format(gid))


@app.route("/gameSummary/<gid>")
def game_summary(gid):
    old_name = player.get_player_info(session["id"])["name"]
    del session["id"]
    return render_template("gameSummary.twig", data=game.get_summary_data(gid), old_name=old_name)


@app.route("/addQuestion", methods=["POST"])
def add_question():
    question.add_question(request.form["question"])

    flash("Added question to question bank. Thank you for your response!")
    return redirect("/questionManager")



@app.route('/questionManager')
def question_management():
    return render_template("questionManager.twig", questions=question.get_all_questions())


@app.route("/editQuestion/<qid>", methods=["POST"])
def edit_question(qid):
    question.edit_question(qid, request.form["question"])
    flash("Successfully Updated Question")
    return redirect("/questionManager")


@app.route("/deleteQuestion/<qid>")
def delete_question(qid):
    question.delete_question(qid)
    flash("Successfully Deleted Question")
    return redirect("/questionManager")

