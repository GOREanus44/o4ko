import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Users(db.Model):
    app_user_id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=True)
    username = db.Column(db.String(100), nullable=False)
    photo_url = db.Column(db.String(255), nullable=True)
    first_launch_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Event(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)  # Уникальный идентификатор события
    event_name = db.Column(db.String(200), nullable=False)  # Название события
    event_description = db.Column(db.String(500), nullable=True)  # Описание события (по умолчанию пусто)
    event_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Дата и время события (по умолчанию текущее время)
    invite_link = db.Column(db.String(36), unique=True, nullable=False, default=str(uuid.uuid4()))  # UUID ссылка для приглашения
    creator_id = db.Column(db.Integer, db.ForeignKey('users.app_user_id'), nullable=False)  # Идентификатор создателя события (связь с пользователем)
    creator = db.relationship('Users', backref=db.backref('events', lazy=True))  # Связь с пользователем (создателем)

    # Множество пользователей, которые присоединились к событию
    users = db.relationship('Users', secondary='event_user', backref='joined_events')


class EventUser(db.Model):
    __tablename__ = 'event_user'
    
    event_id = db.Column(db.Integer, db.ForeignKey('event.event_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.app_user_id'), primary_key=True)

    # Связь с пользователями и событиями
    event = db.relationship('Event', backref=db.backref('event_users', lazy=True))
    user = db.relationship('Users', backref=db.backref('user_events', lazy=True))


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dolg')
def dolg():
    return render_template('dolg.html')

@app.route('/dolg2')
def dolg2():
    return render_template('dolg2.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    telegram_id = data.get('telegram_id')
    name = data.get('name')
    username = data.get('username')
    photo_url = data.get('photo_url')

    if not telegram_id or not username:
        return jsonify({'error': 'Invalid data'}), 400

    user = Users.query.filter_by(telegram_id=telegram_id).first()
    if not user:
        user = Users(
            telegram_id=telegram_id,
            name=name,
            username=username,
            photo_url=photo_url
        )
        db.session.add(user)
        db.session.commit()

    return jsonify({'message': 'User registered successfully'})

@app.route('/create_event', methods=['POST'])
def create_event():
    data = request.json
    event_name = data.get('event_name')
    creator_id = data.get('creator_id')

    if not event_name or not creator_id:
        return jsonify({'error': 'Event name and creator ID are required'}), 400

    new_event = Event(
        event_name=event_name,
        creator_id=creator_id
    )

    db.session.add(new_event)
    db.session.commit()

    return jsonify({
        'message': 'Event created successfully',
        'event_id': new_event.event_id,
        'invite_link': new_event.invite_link
    })

@app.route('/add_users_to_event', methods=['POST'])
def add_users_to_event():
    data = request.json
    event_id = data.get('event_id')
    telegram_ids = data.get('telegram_ids')

    if not event_id or not telegram_ids:
        return jsonify({'error': 'Invalid data'}), 400

    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    users = Users.query.filter(Users.telegram_id.in_(telegram_ids)).all()
    if len(users) != len(telegram_ids):
        return jsonify({'error': 'Some users not found'}), 404

    for user in users:
        if not any(user.user_id == event.creator_id for user in event.event_users):
            event_user = EventUser(event_id=event_id, user_id=user.app_user_id)
            db.session.add(event_user)

    db.session.commit()

    return jsonify({'message': 'Users added to event successfully'})

@app.route('/event_users/<int:event_id>', methods=['GET'])
def get_event_users(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404

    participants = [user.username for user in event.event_users]
    return jsonify({'event_id': event_id, 'participants': participants})


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
