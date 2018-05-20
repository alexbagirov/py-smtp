## py-smtp
[![Build Status](https://travis-ci.com/alexbagirov/py-smtp.svg?token=qyY9tZLUJnscK6q7dM7T&branch=master)](https://travis-ci.com/alexbagirov/py-smtp)

#### Description
This program implements SMTP protocol using Python without any special modules.

#### Requirements
- Python3.6

#### Usage
```
usage: main.py [-h] --host HOST [-p PORT] -l LOGIN [--password PASSWORD]
               [-r RECIPIENT] [-c CC] [-b BCC] [--batch BATCH] [--batch-bcc]
               [-s SENDER] [-n NAME] [--subject SUBJECT] [-t TEXT | -f FILE]
               [-a ATTACHMENT]
               [--named-attachment NAMED_ATTACHMENT NAMED_ATTACHMENT] [-z]
               [--no-ssl] [-v] [-e ENCODING] [-m MAX_FILE_SIZE]
```
###### Example
```
python3 main.py --host smtp.gmail.com -l sender@gmail.com --password pass -s sender@gmail.com -r 
recipient@gmail.com -t Hi! -a file.txt
```

###### Author
Alexandr Bagirov
