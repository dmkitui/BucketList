[![Build Status](https://travis-ci.org/dmkitui/BucketList.svg?branch=develop)](https://travis-ci.org/dmkitui/BucketList)
[![Coverage Status](https://coveralls.io/repos/github/dmkitui/BucketList/badge.svg?branch=ft-develop)](https://coveralls.io/github/dmkitui/BucketList?branch=ft-tests-147095419)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/c444bb9b216c4c27b31602882cc93d98/badge.svg)](https://www.quantifiedcode.com/app/project/c444bb9b216c4c27b31602882cc93d98)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/2d56324e6b624ab6a30da81c23cb7851)](https://www.codacy.com/app/dmkitui/BucketList?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dmkitui/BucketList&amp;utm_campaign=Badge_Grade)

## BUCKET LIST API APPLICATION

According to Merriam-Webster Dictionary, a Bucket List is a list of things that one has not done 
before but wants to do before dying. This project aims at implementing an API for an online Bucket 
list service using the Flask framework.

Users will be able to register, and use the service to create their bucketlists, with bucketlist 
items that they will be able to edit, and update as necessary.

It utilizes create, Read, Update update and Delete (CRUD) operations to create, read, update, 
and delete bucketlist and bucketlist items on the server using the REST framework and JSON.

###Definitions

**Bucketlist**- A broad wishlist of things one desires to accomplish, experience or engage in 
before they die. This may include:
 
 * Travel the world.
 * Live a healthy lifestyle.
 * Give back to society.
 * Learn programming
 * ETC.
 
**Bucketlist Items**- These are the specific activities/steps taken towards actualizing the 
specific bucketlist as defined above. Examples of bucketlist for _Travel the World_ might include:
* Visit the Maldives
* Live in Jamaica for a year
* Swim with the dolphines in Wasini.


**API**- (Application Program Interface) provides a blueprint for how software 
programs interacts with each other.

**JSON**-(Javascript Object Notation) is a light-weight format that facilitates interchange of 
data between different systems or, case in point, software. It is intended to be universal and 
thus allows consumption of data by any program regardless of the programming language it is 
written in. Sample JSON data is represented as a key:value dictionary as below

```json
{
"user_email": "dan@gmail.com",
"user_password": "Qwerty1234"
}
```

**REST**-(REpresentational State Transfer) is way of building API's. The five main principles the
 implementation of REST are:

* Everything is a resource.
* Every resource has a unique identifier.
* Use simple and uniform interfaces.
* Communication is done by representation.
* Aim to be Stateless.
    
    


## Installation

1. Clone the repo using the following command:

    `git clone https://github.com/dmkitui/BucketList.git`
    
2. cd into the bucketlist directory and prepare a Python 3 virtual environment with the following 
steps:

    `$ virtualenv venv`

    Activate the virtual environment

        `$ source venv/bin/activate`

3. Run the following commands to install all the modules required for this application to run:

    `$ pip install -r requirements.txt`
     
4. The following commands will create the databases

    Development database    `$ createdb bucketlist_api`
    
    Tests database    `$ createdb test_db`


5. The following commands will initialize and setup the database tables:
    
    `$ python manage.py db init`

    `$ python manage.py db migrate`

    `$ python manage.py db upgrade`

6. Setup the environment variables with the following commands:

    `$ export FLASK_APP="run.py"`
    
    `$ export APP_SETTINGS="development"`
    
    `$ export SECRET="a-long-string-of-random-characters"`
    
    `$ export DATABASE_URL="postgresql://localhost/bucketlist_api"`
    
7. To start the server, run the following command:

    `flask run`
    
    You can access the server from your web browser at:
    
    `http://127.0.0.1:5000/`
    
    Use [Postman](https://www.getpostman.com/) to test out the various endpoint functionalities 
    of this application.
    
    

## Usage
### Endpoints

TODO: Write usage instructions

## Screenshots

TODO: Include screenshots of the application.

## Contributing

Fork it!
Create your feature branch: git checkout -b my-new-feature
Commit your changes: git commit -am 'Add some feature'
Push to the branch: git push origin my-new-feature
Submit a pull request :D

## History

TODO: Write history

## Credits

TODO: Write credits

## License

TODO: Write license
