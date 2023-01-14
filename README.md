# Chornado
#### Video Demo: <URL HERE>

## Description

Chornado is a web application that allows parents to create and assign chores and rewards for completing them to their kids. Each chore is assigned a point value that the child can earn by completing them. They can use these points to purchase the rewards created by the parents.

The project is built in Python using the Flask framework. It also uses WTForms and Flask-SQLAlchemy. It is hosted on Oracle Cloud using Oracle Autonomous Transaction Database.

## Source Files
\__init__.py - App factory for app

auth.py - Registration, login, and logout routes for app

children.py - Routes for Child functions

forms.py - Form objects for app

helpers.py - Various helper functions used by app

parents.py - Routes for Parent functions

routes.py - Default routes for app

sql_models.py - Flask-SQLAlchemy ORM objects for app's database tables

## Technology Stack
Flask - I used Flask as my primary web framework as it is one I've used a couple of times before, including in Week 9 of CS50. It is easy to use, and the app is simple enough that it doesn't require performance benefits that might have been provided by other frameworks.

WTForms - WTForms provides a quick and easy way to create and implement web forms in Flask using Python

Flask-SQLAlchemy - Flask-SQLAlchemy (FSA) was one of the technology choices I struggled with the most. The current production version of FSA uses an older version of the SQLAlchemy library. Unfortunately, when I moved my database from SQLite to Oracle ATD, I encountered several issues with getting FSA to connect to the database. After several hours of struggling with it, I did further research and Oracle recently released a new DB dialect library called oracledb. This library is not supported in the production version of SQLAlchemy. During development I started using the latest beta of SQLAlchemy which included this dialect, making connecting to the Oracle database much easier.

## Hosting
The application is running on an Ubuntu (?) Linux server hosted on Oracle Cloud. Oracle Cloud provides a very generous free tier that more than covers my needs for this project, even once the project goes live. If the project actually takes off in production, I will re-evaluate the hosting solution.

The database is running on an Oracle Cloud Autonomous Transaction Database. I learned a lot more about Oracle DB during this project than I ever thought I would, but once I got past the learning curve, it is incredibly easy to use, and is fully included within the Oracle Cloud free-tier. 
