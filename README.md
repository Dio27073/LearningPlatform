# Learning Platform

## Problem we aimed to solve:
With quizlet now being a paid service we decided to create a similiar app to allow students to study for upcoming exams for free. This application aims to enhance the study experience by allowing users to create flashcard sets, generate quizzes from these flashcards, and track their progress through a gradebook. 

## User Interface Instructions
### Home Page
- Displays a list of recently created flashcard sets. Clicking on a set title navigates to the details page
- Create Flashcards button redirects to the page where users can create a new flashcard set
- Admins have access to view users by clicking on the Manage Users button on the top right.

### Flashcard Set Management
- Create flashcards page: Allows users to create a new flashcard set by providing a title, description, and adding flashcards with terms and definitions.
- Flashcard Set Details Page: Displays all flashcards within the set and allows you to create a quiz, view quizzes, or delete the set (admin only).

### Quiz Management
- Create Quiz Page: Allows users to create a quiz based on a flashcard set by specifying the title, and length of the quiz.
- Quiz Result Page: Displays the user's score and provides options to go back to quizzes, home, or the gradebook.
  
### Gradebook
- Gradebook Page: Displays all quizzes taken by the user along with their scores.
  
## Libraries Used
- Flask
- Flask-Migrate
- Flask-Bcrypt
- Flask-Login
- Flask-SQLAlchemy
- Multiprocessing
- MySQL Connector

## Other Resources
- Bootstrap: For styling the web pages.
- JavaScript: Used for dynamically adding flashcards.

## Separation of Work

**Claudio Olmeda Florio**:
  - Backend development
  - Database management
  - Role-based access control implementation
  - Parallel processing for quiz answer checking

**Derek Toledo**:
  - Assisted with database management
  - Implemented gradebook
  - Completed the one page on how we would deploy this app.

**Ricardo Ledezma**:
  - Designed and implemented user registration and login features

