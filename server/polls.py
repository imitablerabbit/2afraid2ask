"""
polls.py is the part of the server which controls the poll files.
This includes creation, deletion, editing
"""
from server import app, polls_dict, users_dict, users_lock, polls_lock
from server.users import is_logged_in, get_user_by_session, is_admin

from flask import request, render_template, redirect


def get_polls_by_user_id(user_id):
    """get_polls_by_user_id will return a list of all the polls which a single user has created"""
    users_lock.acquire()
    user = users_dict[user_id]
    users_lock.release()
    poll_ids = user["polls"]
    polls = []
    polls_lock.acquire()
    for poll_id in poll_ids:
        poll = polls_dict[poll_id]
        polls.append(poll)
    polls_lock.release()
    return polls


@app.route("/poll/new", methods=["POST", "GET"])
def poll_new():
    "poll_new will create a new poll from submitted forms or it will return a html document"
    if not is_logged_in():
        return redirect("/login")
    if request.method == "POST":
        # Create the poll via the information passed into it
        form = request.form
        question = form.get("question")
        if not question:
            return "Please enter a question"
        user = get_user_by_session()
        polls_lock.acquire()
        poll_id = len(polls_dict)
        poll = {
            "poll_id": poll_id,
            "user_id": user["user_id"],
            "question": question,
            "reports": 0,
            "answers": {}
        }
        polls_dict[poll_id] = poll
        polls_lock.release()
        polls = user["polls"]
        polls.append(poll_id)
        users_lock.acquire()
        user["polls"] = polls # might be redundant?
        users_dict[user["user_id"]] = user
        users_lock.release()
        return redirect("/poll/"+str(poll_id))
    return render_template("new_poll.html")


@app.route("/poll/delete/<int:poll_id>")
def poll_delete(poll_id):
    """poll_delete will delete the poll which the link points to only if the user is
    the owner of the link, or the user is an admin of the site"""
    if not is_logged_in():
        return redirect("/login")
    user = get_user_by_session()
    if not user:
        return redirect("/login")
    polls_lock.acquire()
    poll = polls_dict.get(poll_id)
    if not poll:
        polls_lock.release()
        return "No poll with that id"
    # check if the are an admin, or they are the owner of the poll
    if is_admin() or poll["user_id"] == user["user_id"]:
        del polls_dict[poll_id]
        polls_lock.release()
        return "Poll successfully deleted"
    polls_lock.release()
    return "Could not delete poll"


@app.route("/poll/edit/<int:poll_id>", methods=["POST", "GET"])
def poll_edit(poll_id):
    "poll_edit will edit a poll based on a submitted form"
    polls_lock.acquire()
    poll = polls_dict.get(poll_id)
    if not poll:
        return "The poll was not found"
    if request.method == "POST":
        if not is_logged_in():
            return redirect("/login")
        form = request.form
        question = form.get("question")
        if not question:
            return "The edited poll did not update the question"
        poll["question"] = question
        polls_dict[poll_id] = poll
        polls_lock.release()
        return "Successfully updated poll"
    polls_lock.release()
    return render_template("poll_edit.html", poll=poll)


@app.route("/poll/delete")
@app.route("/poll/edit")
def poll_manage():
    "poll_manage will show a list of user created polls"
    if not is_logged_in():
        return redirect("/login")
    # get the users polls
    user = get_user_by_session()
    polls = get_polls_by_user_id(user["user_id"])
    return render_template("manage_polls.html", polls=polls)


@app.route("/poll/report/<int:poll_id>")
def poll_report(poll_id):
    "poll_report reports a poll from its id"
    polls_lock.acquire()
    poll = polls_dict.get(poll_id)
    if not poll:
        polls_lock.release()
        return "Poll not found"
    reports = poll["reports"]
    reports += 1
    question = poll["question"]
    poll["reports"] = reports
    polls_dict[poll_id] = poll
    polls_lock.release()
    return "Successfully reported poll: " + question


@app.route("/poll/<int:poll_id>/answers/report/<int:answer_id>")
def poll_answer_report(poll_id, answer_id):
    "poll_answer_report will report and answer in a poll"
    polls_lock.acquire()
    poll = polls_dict.get(poll_id)
    if not poll:
        polls_lock.release()
        return "poll not found"
    answers = poll["answers"]
    answer = answers.get(str(answer_id))
    if not answer:
        polls_lock.release()
        return "answer could not be found"
    answer["reports"] += 1
    answer_answer = answer["answer"]
    polls_lock.release()
    return "Successfully reported answer: " + answer_answer


@app.route("/poll/<int:poll_id>/answers/new", methods=["POST", "GET"])
def poll_answer_new(poll_id):
    "poll_answer_new will create a new answer from a submitted form"
    if not is_logged_in():
        return redirect("/login")
    if request.method == "POST":
        form = request.form
        answer = form.get("answer")
        if not answer:
            return "Did not enter an answer value"
        polls_lock.acquire()
        poll = polls_dict.get(poll_id)
        if not poll:
            polls_lock.release()
            return "No poll with that id"
        answers = poll["answers"]
        user = get_user_by_session()
        user_id = user["user_id"]
        answer_id = len(answers)
        answer = {
            "answer_id": str(answer_id),
            "user_id": user_id,
            "answer": answer,
            "votes": 0,
            "reports": 0
        }
        answers[str(answer_id)] = answer
        # poll["answers"] = answers
        # polls_dict[poll_id] = poll
        polls_lock.release()
        answer = {
            "poll_id": str(poll_id),
            "answer_id": str(answer_id)
        }
        users_lock.acquire()
        user["answers"].append(answer)
        users_dict[user_id] = user
        users_lock.release()
        return redirect("/poll/"+str(poll_id))
    return redirect("/poll/"+str(poll_id))


@app.route("/poll/<int:poll_id>")
def poll_single(poll_id):
    "poll_single will show a template for a single poll"
    polls_lock.acquire()
    poll = polls_dict.get(poll_id)
    if not poll:
        polls_lock.release()
        return "Could not find the poll"
    polls_lock.release()
    return render_template("poll_single.html", poll=poll)


@app.route("/poll/<int:poll_id>/answers/<int:answer_id>/vote")
def poll_answer_vote(poll_id, answer_id):
    "poll_answer_vote will vote on the answer from the poll and answer id"
    polls_lock.acquire()
    poll = polls_dict.get(poll_id)
    if not poll:
        polls_lock.release()
        return "Could not find poll"
    answers = poll["answers"]
    answer = answers.get(str(answer_id))
    if not answer:
        polls_lock.release()
        return "Could not find answer"
    votes = answer["votes"]
    votes += 1
    answer["votes"] = votes
    answers[str(answer_id)] = answer
    poll["answers"] = answers
    polls_dict[poll_id] = poll
    polls_lock.release()
    return redirect("/poll/"+str(poll_id))
