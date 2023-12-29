from flask import render_template, redirect, flash, url_for, request, send_from_directory, jsonify
from models import User, Comment, Blog
from forms import AddBlogForm, RegisterForm, LoginForm, CommentForm, SearchForm
from ext import app, db
from flask_login import current_user, login_required, LoginManager, logout_user, login_user
from wtforms.validators import ValidationError
from forms import UniqueEmail, UniqueUsername
from os import path


@app.route("/")
def home():
    blogs = Blog.query.all()
    search_form = SearchForm()
    return render_template("index.html", blogs=blogs, search_form=search_form)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/blogs")
def blog_list():
    blogs = Blog.query.all()
    return render_template("blogs.html", blogs=blogs)

def get_search_results(query):
    return [{'id': 1, 'name': 'Blog 1'}, {'id': 2, 'name': 'Blog 2'}]

@app.route("/search_results", methods=['GET'])
def search_results():
    query = request.args.get('query', '')
    blogs = Blog.query.filter(Blog.name.ilike(f"%{query}%")).all()
    return render_template("search_results.html", query=query, blogs=blogs)


@app.context_processor
def inject_search_form():
    search_form = SearchForm()
    return dict(search_form=search_form)

@app.route('/validate_registration', methods=['POST'])
def validate_registration():
    csrf_token = request.form.get('csrf_token')
    email = request.form.get('email')
    username = request.form.get('username')

    if email_already_exists(email) or username_already_exists(username):
        return jsonify({"success": False, "message": "Email or username already taken."})
    else:
        return jsonify({"success": True, "message": "Validation successful."})

def email_already_exists(email):
    return User.query.filter_by(email=email).first() is not None

def username_already_exists(username):
    return User.query.filter_by(username=username).first() is not None


@app.route("/AI_Blog", methods=['GET', 'POST'])
def ai_blog():
    form = CommentForm()

    if request.method == 'POST' and form.validate_on_submit():
        comment = Comment(content=form.comment.data, author=current_user)

        db.session.add(comment)
        db.session.commit()

        flash('Comment posted successfully!', 'success')

    return render_template("AI_Blog.html", form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Login successful', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('home'))

        flash('Login unsuccessful. Check your email and password.', 'danger')

    return render_template("loginpage.html", form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password = form.password.data

        try:
            UniqueEmail()(form, form.email)
            UniqueUsername()(form, form.username)
        except ValidationError as e:
            flash(str(e), 'danger')
            return render_template('register.html', form=form)

        user = User(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/add_blog", methods=['GET', 'POST'])
@login_required
def add_blog():
    if current_user.username != "JustifyX":
        flash('Permission Denied: Only JustifyX can add blogs.', 'error')
        return redirect("/")

    form = AddBlogForm()

    if form.validate_on_submit():
        new_blog = Blog(
            name=form.name.data,
            post_date=form.post_date.data,
            img=form.image.data.filename,
            description=form.description.data,
            content=form.content.data
        )
        db.session.add(new_blog)
        db.session.commit()

        file_directory = path.join(app.root_path, "static", form.image.data.filename)
        form.image.data.save(file_directory)

        flash('Blog added successfully!', 'success')
        return redirect("/blogs")

    return render_template("add_blog.html", form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)


@app.route("/blog/<int:blog_id>", methods=['GET', 'POST'])
def blog_detail(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    form = CommentForm()

    if request.method == 'POST' and form.validate_on_submit():
        comment = Comment(content=form.comment.data, user=current_user, blog=blog)
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted successfully!', 'success')

    return render_template("blog_detail.html", blog=blog, form=form)


@app.route("/add_comment/<int:blog_id>", methods=['POST'])
@login_required
def add_comment(blog_id):
    form = CommentForm()

    if form.validate_on_submit():
        comment = Comment(content=form.comment.data, user=current_user, blog_id=blog_id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
    else:
        flash('Failed to add comment. Please check your input.', 'danger')

    return redirect(url_for('blog_detail', blog_id=blog_id))


if __name__ == '__main__':
    app.run(debug=True)
