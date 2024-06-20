import random
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from multiprocessing import Pool

from models import db, User, Role, FlashcardSet, Flashcard, Quiz, Grade

# SQL Setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://learningapp_user:Billy2001@localhost/learningapp_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'

# db extensions
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

# login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    roles = Role.query.all()
    flashcard_sets = FlashcardSet.query.order_by(FlashcardSet.id.desc()).all()
    return render_template('home.html', roles=roles, flashcard_sets=flashcard_sets)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('login failed try again.', 'danger')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    roles = Role.query.all()  # get roles

    if request.method == 'POST':
        # get form data
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        roleId = request.form['role']

        # hashed password
        hashed_pass = bcrypt.generate_password_hash(password).decode('utf-8')

        # creates a new user
        user = User(username=username, email=email, password=hashed_pass, role_id=roleId)
        db.session.add(user)
        db.session.commit()
        flash('your account has been created', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', roles=roles)  # pass roles


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/users')
@login_required
def list_users():
    if current_user.role.name != 'admin':
        abort(403, description="You are not an admin")
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if current_user.role.name != 'admin':
        abort(403, description="denied")

    db.session.delete(user)
    db.session.commit()
    flash('user deleted', 'success')
    return redirect(url_for('list_users'))


# list of quizzes
@app.route('/quizzes')
@login_required
def quizzes():
    quizzes = Quiz.query.filter_by(created_by=current_user.id).all()
    return render_template('quizzes.html', quizzes=quizzes)


# flashcard set
@app.route('/flashcard_set/<int:set_id>')
@login_required
def flashcard_set(set_id):
    flashcard_set = FlashcardSet.query.get_or_404(set_id)        # get flashcard set by ID
    flashcards = Flashcard.query.filter_by(set_id=set_id).all()  # get all flashcards in a set
    return render_template('flashcard_set.html', flashcard_set=flashcard_set, flashcards=flashcards)


# create a flashcard set
@app.route('/create_flashcard_set', methods=['GET', 'POST'])
@login_required
def create_flashcard_set():
    if request.method == 'POST':
        # get form data
        title = request.form['title']
        description = request.form['description']

        flashcard_set = FlashcardSet(title=title, description=description, created_by=current_user.id)

        # add and commit the new flashcard set to the database
        db.session.add(flashcard_set)
        db.session.commit()

        questions = request.form.getlist('questions[]')
        answers = request.form.getlist('answers[]')

        for question, answer in zip(questions, answers):
            flashcard = Flashcard(question=question, answer=answer, set_id=flashcard_set.id, created_by=current_user.id)
            db.session.add(flashcard)

        db.session.commit()
        flash('flashcards created successfully', 'success')
        return redirect(url_for('home'))
    return render_template('create_flashcards.html')


# delete set
@app.route('/delete_flashcard_set/<int:set_id>', methods=['POST'])
@login_required
def delete_flashcard_set(set_id):
    flashcard_set = FlashcardSet.query.get_or_404(set_id)
    user = User.query.get_or_404(current_user.id)

    # only admins can delete sets
    if user.role.name != 'admin':
        abort(403, description="you are not allowed to delete sets")

    # delete the quizzes first
    quizzes = Quiz.query.filter_by(set_id=set_id).all()
    for quiz in quizzes:
        db.session.delete(quiz)

    db.session.delete(flashcard_set)
    db.session.commit()
    flash('flashcard set deleted', 'success')
    return redirect(url_for('home'))


# create a quiz
@app.route('/create_quiz/<int:set_id>', methods=['GET', 'POST'])
@login_required
def create_quiz(set_id):
    flashcard_set = FlashcardSet.query.get_or_404(set_id)
    flashcards = Flashcard.query.filter_by(set_id=set_id).all()

    if request.method == 'POST':
        title = request.form['title']
        question_format = request.form['question_format']
        length = int(request.form['length'])

        quiz = Quiz(title=title, created_by=current_user.id, set_id=set_id,
                    question_format=question_format, length=length)

        db.session.add(quiz)
        db.session.commit()
        flash('quiz created successfully', 'success')
        return redirect(url_for('take_quiz', quiz_id=quiz.id))

    return render_template('create_quiz.html', flashcard_set=flashcard_set, flashcards=flashcards)


@app.route('/take_quiz/<int:quiz_id>')
@login_required
def take_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    flashcard_set = FlashcardSet.query.get_or_404(quiz.set_id)
    flashcards = Flashcard.query.filter_by(set_id=flashcard_set.id).all()

    # generate multiple-choice options
    for flashcard in flashcards:
        options = [flashcard.answer]
        other_flashcards = [f for f in flashcards if f.id != flashcard.id]
        options.extend([f.answer for f in other_flashcards[:3]])
        random.shuffle(options)
        flashcard.options = options

    return render_template('take_quiz.html', quiz=quiz, flashcard_set=flashcard_set, flashcards=flashcards)


# function to check quiz answers
def check_answer(args):
    correct_answer, user_answer = args
    return correct_answer.lower() == user_answer.lower()


@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    flashcards = Flashcard.query.filter_by(set_id=quiz.set_id).all()
    user_answers = request.form.to_dict(flat=False)

    # argument for parallel process
    args = [(flashcard.answer, user_answers.get(f'answers[{flashcard.id}]', [''])[0]) for flashcard in flashcards]

    # multiprocessing to check answers
    with Pool(processes=4) as pool:
        results = pool.map(check_answer, args)

    correct_answers = sum(results)
    total_questions = len(flashcards)
    totalScore = (correct_answers / total_questions) * 100  # calculate score

    # save grade
    grade = Grade(
        title=quiz.title,
        user_id=current_user.id,
        score=totalScore,
        quiz_id=quiz.id
    )
    db.session.add(grade)
    db.session.commit()

    return render_template('quiz_result.html', quiz=quiz,
                           correct_answers=correct_answers, total_questions=total_questions)


@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    user = User.query.get_or_404(current_user.id)

    # only the user who created the quiz an admin or an instructor can delete a quiz
    if quiz.created_by != current_user.id and user.role.name not in ['admin', 'instructor']:
        abort(403, description="you are not able to delete this quiz")

    db.session.delete(quiz)
    db.session.commit()
    flash('quiz deleted', 'success')
    return redirect(url_for('quizzes'))


@app.route('/gradebook', methods=['GET', 'POST'])
@login_required
def gradebook():
    grades = Grade.query.filter_by(user_id=current_user.id).all()
    return render_template('gradebook.html', grades=grades, user=current_user)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
