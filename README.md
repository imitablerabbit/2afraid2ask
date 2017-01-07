# 2afraid2ask

A anonymous site for polling questions to the internet which people are 2 afraid 2 ask in person. This project was made for the HackNotts hackathon 2016.

## Installation

Dependencies required are Flask and bcrypt (Python 3.5). They can be installed by running the following pip commands. 

```
pip install flask
pip install bcrypt
```

**Note: algoliasearch dependancy has been removed.**

Once the depedancies have been installed you can run the server using a standard python command whilst in the top level directory.

```
python main.py
```

Now navigate to the `localhost:5000` page in your web browser

## To-do

- Add something useful to the manage account page
- Dont display the manage account page if not logged in
- Change login to logout when already logged in
- Add new searching mechanism instead of algolia search
- Add ajax calls to the voting and input forms so the user doesnt have to be redirected and the browser refreshed
- Make it so that users can only vote Once
  - check log in credentials?
  - check ip?
- Can only add a new answer Once
  - log in credentials

## Changelog

- Updated UI
- Removed algolia search