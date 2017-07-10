[![Build Status](https://travis-ci.org/dmkitui/BucketList.svg?branch=develop)](https://travis-ci.org/dmkitui/BucketList)
[![Coverage Status](https://coveralls.io/repos/github/dmkitui/BucketList/badge.svg?branch=develop)](https://coveralls.io/github/dmkitui/BucketList?branch=develop)
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

### Definitions

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


### CODE STYLE
This project is coded with adherence to [pep8](https://www.python.org/dev/peps/pep-0008/) except 
for line length which is set at 100 characters.
    
    


## Installation

1. Make sure you have Python version 3.3 or later installed.

2. Clone the repo using the following command:

    `git clone https://github.com/dmkitui/BucketList.git`
    
3. cd into the bucketlist directory and prepare a Python 3 virtual environment with the following 
steps:

    `$ virtualenv venv`

    Activate the virtual environment

        `$ source venv/bin/activate`

4. Run the following commands to install all the modules required for this application to run:

    `$ pip install -r requirements.txt`
     
5. The following commands will create the databases

    Development database    `$ createdb bucketlist_api`
    
    Tests database    `$ createdb test_db`


6. The following commands will initialize and setup the database tables:
    
    `$ python manage.py db init`

    `$ python manage.py db migrate`

    `$ python manage.py db upgrade`

7. Setup the environment variables with the following commands:

    `$ export FLASK_APP="run.py"`
    
    `$ export APP_SETTINGS="development"`
    
    `$ export SECRET="a-long-string-of-random-characters"`
    
    `$ export DATABASE_URL="postgresql://localhost/bucketlist_api"`
    
8. To start the server, run the following command:

    `flask run`
    
    You can access the server from your web browser at:
    
    `http://127.0.0.1:5000/`
    
    Use [Postman](https://www.getpostman.com/) to test out the various endpoint functionality 
    of this application.

## Usage
### Endpoints

Endpoint | Functionality| Public Access
------------ | ------------- | -------------

POST api/v1/bucketlist/auth/register | Registers a user | TRUE

POST api/v1/bucketlist/auth/login | Logs a user in | TRUE

POST api/v1/bucketlist/ | Creates a new bucket list | FALSE

GET api/v1/bucketlist/ | Lists all created bucket lists | FALSE

GET api/v1/bucketlist/bucketlist_id | Gets a single bucket list with the id bucketlist_id | FALSE

PUT api/v1/bucketlist/bucketlist_id | Updates bucket list with the bucketlist_id | FALSE

DELETE api/v1/bucketlist/bucketlist_id | Deletes bucket list with the id bucketlist_id | FALSE

POST api/v1/bucketlist/bucketlist_id/items/ | Creates a new item in bucket list with id bucketlist_id | FALSE

PUT api/v1/bucketlist/bucketlist_id/items/item_id | Updates a bucket list item | FALSE

DELETE api/v1/bucketlists/bucketlist_id/items/item_id | Deletes an item in a bucket list | FALSE


### 1. User Registration

For a user to successfully register, a POST json with the following details is requiered:

**user_email** : User's valid email address. Invalid email addresses shall be rejected with an 
error message.
**user_password**: User's  password which must be at least 8 characters long, contain an upper case 
letter and a digit.
**confirm_password**: The user's password entered again.

Any error with the above required fields will result in an error message as shown below:

![alt text](screenshots/reg_errors_password.png "Registration success")

![alt text](screenshots/reg_errors_cofirmationpwd.png "Registration Failure")

![alt text](screenshots/reg_errors_pwd_not_match.png "Registration Failure")


On successful registration, the response will be as in the screenshot below:

![alt text](screenshots/reg_success.png "Registration success")


### 2. User Login

A registered user can login into the service at this endpoint 

`bucketlist/app/v1/bucketlists/`

Required fields are user_email and user_password

An unregistered user trying to log in will recieve the following message:

On successful login, the user will see the message below:

The **access_token** will be used in subsequent bucketlist endpoints to authenticate the user.

#### Authorization header field

This is field in the request header in the form

`Authorization : Bearer + access token`

For example:
`Authorization : Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE0OTk2NjM2MzIsImlhdCI6MTQ5OTY2MDYzMiwic3ViIjoxMX0.c9fzEpjf8y-iImPZGyxpQQwaVCha7ULf-LWxaZDH-S4`


### 3. Fetch bucketlists
`GET api/v1/bucketlist/`

After logging in, a user can use this endpoint to access all their bucketlists.

The response fields are:
 1. `owner_id`: Id of the user
 2.  `name`: Name of the bucketlist
 3. `id`: Bucketlist ID.
 4. `date_created` and `date_modified`: Date and time the bucketlist was created and modified 
 respectively.
 5. `current_page` and `total_pages`: The current page and number of total pages. 
 
#### Search

A user can perform a search on bucketlists by including the search parameter q at this endpoint.

eg: `GET api/v1/bucketlist/?q=nairobi`

The above will result in all bucketlists with __nairobi__ in their names to be returned. The 
search is case insensitive. When there is no match, the returned response shall indicate so.

#### Pagination

By default, the GET operation will return 20 items per page. The user can however specify the 
pagination by using a __limit__ parameter eg:
    `GET api/v1/bucketlist/?limit=10`
    
Will return 10 items per page, and response will include __current_page__ and __total_page__ 
dictionary.


 
### 4. POST a bucketlist
`POST api/v1/bucketlist/`

The required fields for a user to post a bucketlist are:

**name**: Bucketlist name, eg Travel the world

A successful POST will give the following message:

### 5. Fetch a particular bucketlist

`GET api/v1/bucketlist/bucketlist_id`

Used to get a bucketlist with id __bucketlist_id__

This will return a response with details of the specified bucketlist id.


### 6. Edit a particular bucketlist

`PUT api/v1/bucketlist/bucketlist_id`

Used to edit the name of  bucketlist of the given ID.
 
On successful edit, the message is as below:

### 7. Delete a particular bucketlist

`DELETE api/v1/bucketlist/bucketlist_id`

Used to delete a bucketlist with id bucketlist_id



### 8. Add items to bucketlist

`POST api/v1/bucketlist/bucketlist_id/items/`

Used to add item to bucketlist with id __bucketlist_id__

Reuired json body fields are:

1. **item_name**: The items name, eg *Visit Hawai*

If the item nameis missing, the response message will  specify the error.

The json response fields are:

1. `bucketlist_id`: The id of the bucketlist
2. `done`: Status of the list item. True if the item has been completed, otherwise false.
3. `id`: The ID of the list item.
4. `date_created` and `date_modified`: Date and time of creation, and modification.

### 9. Edit item in bucketlist

`PUT api/v1/bucketlist/bucketlist_id/items/item_id`

Used to edit an item with __item_id__ of bucketlist with id __bucketlist_id__.

The required fields can be either:

1. `item_name`: To edit the name of the item
2. `done`: __True__ or __False__ To edit status of the item.

### 10. Delete item in bucketlist

`DELETE api/v1/bucketlist/bucketlist_id/items/item_id`

Used to delete an item with __item_id__ of bucketlist with id __bucketlist_id__.


## Contributing

Fork it!
Create your feature branch: git checkout -b my-new-feature
Commit your changes: git commit -am 'Add some feature'
Push to the branch: git push origin my-new-feature
Submit a pull request

## Credits

[Roger Taracha](https://github.com/TheDancerCodes) : For the inspiration and encouragement.

[Andela Community](https://www.andela.com/) : For the opportunity to become a tech-leader.

## License

The MIT License (MIT)

Copyright (c) 2017 [dmkitui](https://github.com/dmkitui)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the "Software"), to deal in the Software without restriction, 
including without limitation the rights to use, copy, modify, merge, publish, distribute, 
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or 
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT
 NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND 
 NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
 DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
