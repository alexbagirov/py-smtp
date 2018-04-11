## py-smtp
[![Build Status](https://travis-ci.com/alexbagirov/py-smtp.svg?token=qyY9tZLUJnscK6q7dM7T&branch=master)](https://travis-ci.com/alexbagirov/py-smtp)

#### Description
This program implements SMTP protocol using Python without any special modules.

#### Requirements
- Python3.6

#### Usage
```
python3 main.py [-h] host port login password sender recipient text
```
###### Example
```
python3 main.py smtp.gmail.com 587 sender@gmail.com 123456 sender@gmail.com recipient@gmail.com Hi!
```

###### Author
Alexandr Bagirov
