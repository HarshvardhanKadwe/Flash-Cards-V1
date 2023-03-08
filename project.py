from flask import Flask,render_template,request,redirect,session
from flask.helpers import flash
from flask_login.utils import login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from werkzeug.utils import redirect
from flask_login import LoginManager, UserMixin, login_manager,login_user,logout_user,current_user
from datetime import datetime



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///flaskrelation.db'
app.secret_key="hello"

#initialize the data base
db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)


#Create db model

class users(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(50),nullable=False)
    password=db.Column(db.String(20))
    decks=db.relationship('Deck', backref='owner')

class Deck(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    deckname=db.Column(db.String(50),nullable=False)
    ownerid=db.Column(db.Integer, db.ForeignKey('users.id'))
    pub_date = db.Column(db.DateTime, nullable=False,default=datetime.utcnow)
    cards=db.relationship('Card',backref='owndeck')

class Card(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    question=db.Column(db.String(50),nullable=False)
    answer=db.Column(db.String(50),nullable=False)
    score=db.Column(db.Integer ,nullable=False)
    deckid=db.Column(db.Integer, db.ForeignKey('deck.id'))
    

@login_manager.user_loader
def load_user(user_id):
    return users.query.get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = users.query.filter_by(username = username).first()

        if not user:
            new_user = users(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            return render_template('signup.html',content="You have successfully signed up, now please login")
    else:
      return render_template('signup.html')

    return render_template('signup.html')



@app.route('/login', methods= ['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = users.query.filter_by(username = username).first()

        if not user:
            return render_template('login.html',content="PLease SignUp first")
        else:
            if (user.password== password):
                login_user(user)
                return redirect('/dashboard')
            else:
                return redirect('/login')
    return render_template('login.html')
    
  


@app.route('/dashboard')
@login_required
def dashboard():
    cscore=0
    cdeck=Card.query.all()
    ndeck = Deck.query.all()
    
    return render_template('dashboard.html', text=current_user.username, deck=ndeck, cdeck=cdeck)

@app.route('/createdeck',methods=["POST","GET"])
@login_required
def createdeck():
    user = users.query.filter_by(username = current_user.username).first()
    if request.method == "POST":
        deckname = request.form['deckname']
        deckob= Deck.query.filter_by(deckname = deckname).first()
        if not deckob:
            new_deckob = Deck(deckname=deckname ,owner=user)
            db.session.add(new_deckob)
            db.session.commit()
            return redirect("/createcard")
    else:
      return render_template('createdeck.html')

    return render_template('createdeck.html')

@app.route('/createcard',methods=["POST","GET"])
@login_required
def createcard():
    user = users.query.filter_by(username = current_user.username).first()
    
    if request.method == "POST":
        question = request.form['question']
        answer = request.form['answer']
        score=0
        newcard= Card(question=question , answer=answer , score=score, owndeck=user.decks[0])
        db.session.add(newcard)
        db.session.commit()
        
        
        return render_template("createcard.html")
    return render_template('createcard.html')

@app.route('/viewcard',methods=["POST","GET"])
@login_required
def viewcard():
    temdeck=Card.query.all()
    if request.method == "POST":
        score=0
        scored=request.form['scored']
        score=score+int(scored)
        ndeck = Card.query.first()
        temdeck=Card.query.all()
        ndeck.score=ndeck.score+score
        db.session.flush()
        db.session.commit()
        if ndeck.score==25:
            rev=ndeck.answer
            return render_template("viewcard.html", lans=rev,temdeck=temdeck )


        return render_template("viewcard.html", ans=score, lans=" ",temdeck=temdeck)
    else:
        return render_template("viewcard.html",temdeck=temdeck)


    










if __name__=='__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
