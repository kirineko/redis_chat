from flask import (
    Flask,
    render_template,
    redirect,
    request,
    Response,
    session
)
import redis
import time


app = Flask(__name__)
app.secret_key = '123456'

r = redis.StrictRedis(charset='utf-8', decode_responses=True)

@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['user'] = request.form['user']
        return redirect('/chat')
    else:
        return render_template('login.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        msg = request.form['msg']
        ctime = time.strftime('%H:%M:%S')
        user = session['user']
        data = '[{}] {}: {}'.format(ctime, user, msg)
        r.publish('chat', data)
        return Response(status=203)
    else:
        if 'user' in session:
            user = session['user']
            return render_template('chat.html', user=user)
        return redirect('/login')


def stream():
    p = r.pubsub(ignore_subscribe_messages=True)
    p.subscribe('chat')
    for message in p.listen():
        print(message)
        data = 'data: {}\n\n'.format(message['data'])
        yield(data)


@app.route('/msg')
def msg():
    return Response(stream(), mimetype='text/event-stream')