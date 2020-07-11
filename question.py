from StatementGame.database import conn, c, d, get_table_id
import random


def get_category_questions():
    d.execute("SELECT * FROM statement")
    return d.fetchall()


def get_question_pair():
    q = get_category_questions()
    random.shuffle(q)
    return q[0], q[1]



def get_question(qid):
    d.execute("SELECT * FROM statement WHERE id={}".format(qid))
    return d.fetchone()


def add_question(text):
    text = text.replace('"', "'")
    c.execute("INSERT INTO statement (text) VALUES (\"{}\")".format(text))
    conn.commit()


def get_all_questions():
    d.execute("SELECT * FROM statement")
    return d.fetchall()


def edit_question(qid, text):
    text = text.replace('"', "'")

    c.execute("UPDATE statement SET text=\"{}\" WHERE id={}".format(text, qid))
    conn.commit()


def delete_question(qid):
    c.execute("DELETE FROM statement WHERE id={}".format(qid))
    conn.commit()
