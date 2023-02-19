# Chornado
### https://chornado.com
#### Video Demo: https://youtu.be/Eo80DMoXrf4

## Description

Chornado is a web application that allows parents to create and assign chores and rewards for completing them to their kids. Each chore is assigned a point value that the child can earn by completing them. They can use these points to purchase the rewards created by the parents.

The project is built in Python using the Flask framework. It also uses WTForms and Flask-SQLAlchemy. The app and database are hosted on fly.io.

Logo courtesy of DC Motion Design

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

Flask-SQLAlchemy - Flask-SQLAlchemy (FSA) is a modified version of SQLAlchemy that integrates more completely with Flask. SQLAlchemy allows you to work with database tables as Python Objects, rather than writing direct SQL queries in your code. I found this to be a much easier and more fun way to work with the database. Although, at times it did present its own challenges, I believe it was the correct choice, and I will likely use it in any Flask projects I work with in the future.

Bootstrap - I am using Bootstrap 5 for my front-end framework. It provides a (fairly) easy to use toolset to quickly provide high-quality, professional looking design.

## Hosting
The app and database are both hosted on fly.io. Fly offers an adequate free tier, and appears to be a very suitable replacement for Heroku.
