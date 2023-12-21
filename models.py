from ext import db, app, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))


    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'), nullable=False)
    blog = db.relationship('Blog', backref=db.backref('comments', lazy=True))



class Blog(db.Model):
    __tablename__ = "blog"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    post_date = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    img = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Blog(id={self.id}, name={self.name}, description={self.description}, post_date={self.post_date}, img={self.img})>"

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __init__(self, email, username, password, role="normal"):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.role = role


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        new_user = User(email="admin@example.com", username="admin", password="password")
        db.session.add(new_user)

        new_blog = Blog(name="AI Blog", post_date=datetime(2023, 2, 19), img="/static/AI.PNG")
        db.session.add(new_blog)

        db.session.commit()
