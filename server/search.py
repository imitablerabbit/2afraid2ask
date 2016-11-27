from algoliasearch import algoliasearch
import json

client = algoliasearch.Client("GD0ORI3267", "0a8fc3997e8f5a1e29c760fcf10d6e67")
index = client.init_index("polls")

# create new poll, taking poll_id and question from a poll object
def create_poll(poll):
	res = index.search(int(poll["poll_id"]), {"restrictSearchableAttributes": "poll_id"})
	# check if poll already exists
	if len(res["hits"]) == 0:
		poll = {"poll_id": int(poll["poll_id"]), "question": poll["question"]}
		index.add_object(poll)


# returns matches for an entire/partial sentence
def get_question_matches(question):
	res = index.search(question, {"restrictSearchableAttributes": "question"})
	return res


# update a modified question by poll_id 
def update_question(poll_id, new_question):
	res = index.search(int(poll_id), {"restrictSearchableAttributes": "poll_id"})
	
	index.partial_update_object({"objectID": res["hits"][0]["objectID"], "poll_id": int(poll_id), "question": new_question})


# remove a poll by poll_id
def delete_poll(poll_id):
	index.delete_by_query(int(poll_id), {"restrictSearchableAttributes": "poll_id"})


''' test function calls '''
#print(get_question_matches("hands"))
#test_poll_object = json.load(open('private/polls/0.json'))
#create_poll(test_poll_object)
#update_question("1", "Do you use chips and fish to eat your hands?")
#delete_poll("0")


