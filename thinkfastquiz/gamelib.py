import sqlalchemy
from sqlalchemy.sql import text

"""
When the game reaches the last question it cycles back to the first question and starts a new round.
The index of the current question is called step.
The current position in the game is represented by a single number:

    position = round * len(questions) + step

To deduce the round and the step from a position:

    round = position // len(questions)
    step = position % len(questions)
"""

QUESTIONS = [
    ("How many different colours do passports come in?", "4"),
    ("Which capital city has three consecutive dotted letters in its English spelling?", "beijing"),
    ("The Answer to the Ultimate Question of Life, The Universe, and Everything", "42"),
    ("How many balls are there in the 8-ball pool game?", "16"),
]


engine = sqlalchemy.create_engine("sqlite:///thinkfastquiz.db")


def qna_at(position):
    step = position % len(QUESTIONS)
    return QUESTIONS[step]


def current_position():
    with engine.begin() as conn:
        return conn.execute(text("select position from game")).scalar()


# (potentially distributed) check-and-set operation.
# Works with SQLite and PostgreSQL. Maybe not with MySQL.
def claim_answer(pos):
    """
    Advance the game to the next question.
    If successful (the user is the first one) returns the new position.
    Otherwise returns None
    """
    new_pos = pos + 1
    with engine.begin() as conn:
        n = conn.execute(text("update game set position = :new_pos where position = :pos"), {
            'new_pos': new_pos,
            'pos': pos
        }).rowcount
        return new_pos if n == 1 else None


def init_db():
    with engine.begin() as conn:
        conn.execute(text("create table game (position integer)"))
        conn.execute(text("insert into game(position) values(0)"))
