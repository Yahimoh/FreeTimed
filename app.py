import os
import sqlite3
from flask import Flask, request, redirect, url_for, session, flash, render_template, g

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a9b8c7d6e5f4g3h2i1j0k9l8m7n6o5p4'
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()

if not os.path.exists(DATABASE):
    init_db()

@app.route('/')
def index():
    db = get_db()
    reviews = db.execute("""
        SELECT reviews.*, users.username 
        FROM reviews 
        LEFT JOIN users ON reviews.user_id = users.id
        ORDER BY reviews.id DESC
    """).fetchall()
    return render_template('index.html', reviews=reviews)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash("Username and password required.")
            return redirect(url_for('register'))
        db = get_db()
        try:
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, password))
            db.commit()
            flash("Registration successful. Please log in.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already taken.")
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and user['password'] == password:
            session.clear()
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Logged in successfully.")
            return redirect(url_for('index'))
        else:
            flash("Incorrect username or password.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out.")
    return redirect(url_for('index'))

@app.route('/review/add', methods=['GET', 'POST'])
def add_review():
    if 'user_id' not in session:
        flash("Please log in to add a review.")
        return redirect(url_for('login'))
    if request.method == 'POST':
        item_name = request.form['item_name']
        category = request.form['category']
        review_text = request.form['review_text']
        if not item_name or not category or not review_text:
            flash("All fields are required.")
            return redirect(url_for('add_review'))
        db = get_db()
        db.execute("INSERT INTO reviews (item_name, category, review_text, user_id) VALUES (?, ?, ?, ?)",
                   (item_name, category, review_text, session['user_id']))
        db.commit()
        flash("Review added.")
        return redirect(url_for('index'))
    return render_template('add_review.html')

@app.route('/review/edit/<int:review_id>', methods=['GET', 'POST'])
def edit_review(review_id):
    if 'user_id' not in session:
        flash("Please log in to edit your review.")
        return redirect(url_for('login'))
    db = get_db()
    review = db.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()
    if not review:
        flash("Review not found.")
        return redirect(url_for('index'))
    if review['user_id'] != session['user_id']:
        flash("You can only edit your own reviews.")
        return redirect(url_for('index'))
    if request.method == 'POST':
        item_name = request.form['item_name']
        category = request.form['category']
        review_text = request.form['review_text']
        if not item_name or not category or not review_text:
            flash("All fields are required.")
            return redirect(url_for('edit_review', review_id=review_id))
        db.execute("UPDATE reviews SET item_name = ?, category = ?, review_text = ? WHERE id = ?",
                   (item_name, category, review_text, review_id))
        db.commit()
        flash("Review updated.")
        return redirect(url_for('index'))
    return render_template('edit_review.html', review=review)

@app.route('/review/delete/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    if 'user_id' not in session:
        flash("Please log in to delete a review.")
        return redirect(url_for('login'))
    db = get_db()
    review = db.execute("SELECT * FROM reviews WHERE id = ?", (review_id,)).fetchone()
    if not review:
        flash("Review not found.")
        return redirect(url_for('index'))
    if review['user_id'] != session['user_id']:
        flash("You can only delete your own reviews.")
        return redirect(url_for('index'))
    db.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    db.commit()
    flash("Review deleted.")
    return redirect(url_for('index'))

@app.route('/profile/<int:user_id>')
def profile(user_id):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        flash("User not found.")
        return redirect(url_for('index'))
    
    reviews = db.execute("SELECT * FROM reviews WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    user_reviews_count = len(reviews)
    total_reviews = db.execute("SELECT COUNT(*) as count FROM reviews").fetchone()['count']

    reviews = db.execute("SELECT * FROM reviews WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    is_following = False
    if 'user_id' in session and session['user_id'] != user_id:
        is_following = db.execute("SELECT * FROM followers WHERE follower_id = ? AND followed_id = ?",
                                  (session['user_id'], user_id)).fetchone() is not None
    return render_template('profile.html', profile=user, reviews=reviews, is_following=is_following, user_reviews_count=user_reviews_count, total_reviews=total_reviews)

@app.route('/follow/<int:user_id>', methods=['POST'])
def follow(user_id):
    if 'user_id' not in session:
        flash("Please log in to follow users.")
        return redirect(url_for('login'))
    if session['user_id'] == user_id:
        flash("You cannot follow yourself.")
        return redirect(url_for('profile', user_id=user_id))
    db = get_db()
    if db.execute("SELECT * FROM followers WHERE follower_id = ? AND followed_id = ?",
                  (session['user_id'], user_id)).fetchone():
        flash("Already following this user.")
    else:
        db.execute("INSERT INTO followers (follower_id, followed_id) VALUES (?, ?)",
                   (session['user_id'], user_id))
        db.commit()
        flash("Now following the user.")
    return redirect(url_for('profile', user_id=user_id))

@app.route('/unfollow/<int:user_id>', methods=['POST'])
def unfollow(user_id):
    if 'user_id' not in session:
        flash("Please log in to unfollow users.")
        return redirect(url_for('login'))
    db = get_db()
    db.execute("DELETE FROM followers WHERE follower_id = ? AND followed_id = ?",
               (session['user_id'], user_id))
    db.commit()
    flash("Unfollowed the user.")
    return redirect(url_for('profile', user_id=user_id))

@app.route('/followed_reviews')
def followed_reviews():
    if 'user_id' not in session:
        flash("Please log in to view followed reviews.")
        return redirect(url_for('login'))
    db = get_db()
    reviews = db.execute("""
        SELECT reviews.*, users.username 
        FROM reviews 
        JOIN followers ON reviews.user_id = followers.followed_id 
        JOIN users ON reviews.user_id = users.id
        WHERE followers.follower_id = ?
        ORDER BY reviews.id DESC
    """, (session['user_id'],)).fetchall()
    return render_template('followed_reviews.html', reviews=reviews)

@app.route('/new_profiles')
def new_profiles():
    db = get_db()
    profiles = db.execute("SELECT * FROM users ORDER BY id DESC").fetchall()

    return render_template('new_profiles.html', profiles=profiles)

if __name__ == '__main__':
    app.run(debug=True)
