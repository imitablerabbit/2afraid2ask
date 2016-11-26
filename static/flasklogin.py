# import the Flask class from the flask module
from flask import Flask, render_template

# create the application object
app = Flask(__name__)


# use decorators to link the function to a url
@app.route('/')
def home():
    users = {'name': 'mark'}

    poll = {
	"poll_id": 1,
	"user_id": 0,
	"question": "Do you put a comma after etc.?",
	"reports": 0,
	"answers": [
		{
			"answer_id": 0,
			"answer": "yes",
			"user_id": 0,
			"votes": 7,
			"reports": 0
		},
		{
			"answer_id": 1,
			"answer": "no",
			"user_id": 1,
			"votes": 3,
			"reports": 1
		}
	]
}

    poll1 = {
        'poll_id': 11,
        'question': 'waddup?',
        'reports': 301,
        'answers': [
            {
                'answer_id': 51,
                'answer': 'the sky',
                'user_id': 791,
                'votes': 71,
                'reports': 1,
            }
        ]
    }
    polls = {0: poll ,1: poll1}

    return render_template('welcome.html',
                           user = users,
                           polls = polls
                           )


@app.route('/login')
def login():
    return render_template('login.html')  # render a template

@app.route('/user')
def user():
    return render_template('user.html')  # render a template



# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
