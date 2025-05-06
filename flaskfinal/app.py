import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta


from flask import Flask, render_template, redirect, request, url_for, flash,session, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + \
    os.path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SECRET_KEY"] = "Your secret key"
app.config['WTF_CSRF_ENABLED'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
# app.config['MAIL_PASSWORD'] = 'your_app_password'
app.config['MAIL_PASSWORD'] = 'xzywabcdefghijkl'
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'


db = SQLAlchemy(app)
mail = Mail(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

# class ContactForm(FlaskForm):
#     name = StringField('Name')
#     submit = SubmitField('Submit')


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.Text)

# Initialize DB once
# with app.app_context():
#     db.create_all()


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)


class User(db.Model, UserMixin):
    _tablename_ = "user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False )
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(10), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_jwt_token(self, expires_in=3600):
        expiration = datetime.utcnow() + timedelta(seconds=expires_in)
        return jwt.encode(
            {'user_id': self.id, 'exp': expiration, 'role': self.role},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    image_path = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db.create_all()
    
    if not User.query.filter_by(role="admin").first():
        admin_user = User(name="Admin", email="admin@gmail.com", mobile="1234567890", role="admin")
        admin_user.set_password("admin123")  
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created with email: admin@gmail.com and password: admin123")



@app.route("/choose-role")
def choose_role():
    action = request.args.get('action', 'login')
    return render_template("choose_role.html", action=action)

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     role = request.args.get('role', 'user')
    
#     if request.method == "POST":
#         email = request.form.get("email")
#         password = request.form.get("password")
#         role = request.form.get("role")

#         user = User.query.filter_by(email=email, role=role).first()
#         if user and user.check_password(password):
#             login_user(user)
#             flash("Login successful!", "success")
#             return redirect(url_for("dashboard"))
#         else:
#             flash("Invalid credentials!", "danger")

#     return render_template("login.html", selected_role=role)


# @app.route("/register", methods=["GET", "POST"])
# def register():
#     role = request.args.get('role', 'user')
    
#     if request.method == "POST":
#         name = request.form.get("name")
#         email = request.form.get("email")
#         password = request.form.get("password")
#         confirm_password = request.form.get("confirm_password")
#         mobile = request.form.get("mobile")
#         role = request.form.get("role")

#         if password != confirm_password:
#             flash("Passwords do not match!", "danger")
#             return redirect(url_for("register", role=role))

#         if User.query.filter_by(email=email).first():
#             flash("Email already exists!", "danger")
#             return redirect(url_for("register", role=role))

#         new_user = User(name=name, email=email, mobile=mobile, role=role)
#         new_user.set_password(password)
#         db.session.add(new_user)
#         db.session.commit()

#         flash("Registration successful! Please log in.", "success")
#         return redirect(url_for("login", role=role))
    
#     return render_template("register.html", selected_role=role)
    

# @app.route("/logout")
# @login_required
# def logout():
#     logout_user()
#     flash("Logged out successfully!", "info")
#     return redirect(url_for("home"))

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route('/music')
def music():
    return render_template('music.html')

@app.route('/arts')
def arts():
    return render_template('arts.html')

@app.route('/food')
def food():
    return render_template('food.html')

@app.route('/sports')
def sports():
    return render_template('sports.html')

@app.route('/tech')
def tech():
    return render_template('tech.html')

@app.route('/edu')
def edu():
    return render_template('edu.html')

@app.route('/business')
def business():
    return render_template('business.html')

@app.route('/lifestyle')
def lifestyle():
    return render_template('lifestyle.html')


app.config['UPLOAD_FOLDER'] = 'static/uploads'


os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



@app.route('/dashboard')
def user_dashboard():
    return render_template('dashboard.html')


@app.route('/event_creation')
def event_creation_page():
    categories = [
        'Music', 'Dance', 'Clubbing', 'Theatre',
        'Sports', 'Technology', 'Food & Drinks', 'Art'
    ]
    return render_template('event_creation.html', categories=categories)


@app.route('/event_creation', methods=['POST'])
def event_creation():
    try:
        if request.method == 'POST':
            category = request.form['category']
            title = request.form['title']
            date = datetime.strptime(request.form['date'], '%Y-%m-%d')
            time = request.form['time']
            description = request.form['description']
        
            image = request.files['image']
            if image:
                from werkzeug.utils import secure_filename
                filename = secure_filename(image.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{filename}"
            
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

                image.save(image_path)
                
                db_image_path = f"static/uploads/{filename}"
            
            new_event = Event(
                category=category,
                title=title,
                image_path=db_image_path,
                date=date,
                time=time,
                description=description
            )
            
            db.session.add(new_event)
            db.session.commit()
            
            return redirect(url_for('dashboard'))  
            
    except Exception as e:
        print(f"Error creating event: {str(e)}")
        flash("An error occurred while creating the event. Please try again.", "error")
        return redirect(url_for('event_creation_page'))


@app.route('/manage_events')
def manage_events():
    events = Event.query.all()
    return render_template('manage_events.html', events=events)


@app.route('/view_event/<int:event_id>')
def view_event(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template('view_event.html', event=event)


events = []



@app.route('/create_event')
def create_event():
    # if request.method == 'POST':
    #     event_name = request.form['event_name']
    #     event_date = request.form['event_date']
    #     events.append({'name': event_name, 'date': event_date})
    #     return redirect(url_for('find_events'))
    return render_template('create_event.html')

@app.route("/find_events")
def find_events():
    return render_template("find_events.html", events=events)


events = [
    {
        "title": "Tech Conference 2025",
        "date": "March 15, 2025",
        "location": "New York, NY",
        "image": "https://source.unsplash.com/600x400/?technology,conference",
    },
    {
        "title": "Music Fest",
        "date": "April 20, 2025",
        "location": "Los Angeles, CA",
        "image": "https://source.unsplash.com/600x400/?concert,music",
    },
    {
        "title": "Startup Pitch Night",
        "date": "May 10, 2025",
        "location": "San Francisco, CA",
        "image": "https://source.unsplash.com/600x400/?startup,business",
    },
]

@app.route('/')
def home():
    interests = [
        "Comedy", "Food", "Education", "Pop", "Design", "R&B", "Hip Hop / Rap", 
        "Film", "Personal health", "Blues & Jazz", "Travel", "Rock", "Yoga", 
        "Country", "Startups & Small Business", "Classical", "Mental health", "TV", 
        "Alternative", "Musical"]
    return render_template('index.html', events=events)   

# @app.route('/help')
# def help():
#     featured_articles = [
#         {"title": "Find your tickets"},
#         {"title": "Request a refund"},
#         {"title": "Contact the event organizer"},
#         {"title": "What is this charge from Eventbrite?"},
#         {"title": "Transfer tickets to someone else"},
#         {"title": "Edit your order information"}
#     ]
#     return render_template('help_center.html', featured_articles=featured_articles)







@app.route('/about')
def about():
    team_members = [
      {
            "name": "Milanjot Kaur",
            "description": "Hi! I am Milanjot Kaur, Co-founder of the app 'Your Second'.",
            "education": "Pursuing B.E. in CSE-AI from Chitkara University, Punjab. 12th from Shemford Futuristic School, Ambala, Haryana.",
            "skills": "Soft Skills: Problem Solving, Leadership Qualities, Keen Learner. Technical Skills: Basics in Front-End Engineering, Python, Java.",
            "language": {"hindi": 95, "english": 75}
        },
        {
            "name": "Divyanjali Tiwari",
            "description": "Hi!, I am Divyanjali Tiwari",
            "education": "Pursuing B.E. in CSE-AI from Chitkara University, Punjab. 12th from City Montessori School, Lucknow, Uttar Pradesh.",
            "skills": "Soft Skills: Problem Solving, Leadership Qualities. Technical Skills: Basics in Front-End Engineering, Python, Java.",
            "language": {"hindi": 90, "english": 80}
        },
        {
            "name": "Drishti Bansal",
            "description": "Hi!, I am Drishti Bansal",
            "education": "Pursuing B.E. in CSE-AI from Chitkara University, Punjab. 12th from Cambridge International School, Sunam, Punjab.",
            "skills": "Soft Skills: Problem Solving, Leadership Qualities. Technical Skills: Basics in Front-End Engineering, Python, Java.",
            "language": {"hindi": 95, "english": 80}
        },
        {
            "name": "Himani Batra",
            "description": "I am Himani Batra, co-founder of the app Your Second.",
            "education": "Persuing B.E. in CSE-AI fron Chitkara University,Punjab. 12th form Siddhartha Public School, New Delhi",
            "skills": "Soft Skills: Problem Solving, leadership qualities, keen learner. Technical skills Basics in front end engineering, python and java",
            "language": {"hindi": 80, "english": 95}
        }
        
    ]
    return render_template('about.html', team_members=team_members)

app.secret_key = 'eventora_key' 

events = [
      {
        "id": 0,
        "title": "Become a Profitable Crypto Trader Overnight – Free Webinar",
        "date": "Monday, February 17 · 12:30 - 2:30pm GMT+5:30",
        "location": "Online",
        "category": "Finance",
        "image_url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F957562763%2F2608572851411%2F1%2Foriginal.20250211-002128?w=940&auto=format%2Ccompress&q=75&sharp=10&s=209166176cf21ab7c3f6ceea88be25a8",
         "description":"Welcome to Profitable Crypto Trader Overnight! Are you ready to unlock the potential of cryptocurrency trading and start earning profits today? This exclusive, FREE webinar will guide you through the essential steps and strategies to become a profitable crypto trader. In this session, expert traders with years of experience in the market will reveal the secrets to navigating the fast-paced world of cryptocurrency trading. Whether you're a beginner or someone looking to fine-tune your skills, you'll discover actionable insights that can help you make informed decisions, minimize risks, and maximize your returns."
    },
    {
        "id": 1,
        "title": "Solar Asia Expo 2025",
        "date": "March 21 · 11am - March 23 · 7pm IST",
        "location": "Kuala Lumpur, Malaysia",
        "category": "Technology",
        "image_url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F925688313%2F2413292386383%2F1%2Foriginal.20250101-093800?crop=focalpoint&fit=crop&w=940&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.0127431669124&fp-y=0.0120622508721&s=2935f3b822863eb2db72c37a12b2f09c",
         "description":"Welcome to Solar Asia Expo 2025! The future of energy is here, and it’s shining brighter than ever at the Solar Asia Expo 2025! Join us for this groundbreaking event where industry professionals, innovators, and enthusiasts come together to explore the latest developments in solar technology and renewable energy solutions.Whether you are an established player in the renewable energy sector or just starting your journey toward sustainable solutions, the Solar Asia Expo 2025 is the perfect platform for you. This three-day expo will showcase cutting-edge technologies, feature insightful seminars, and provide unparalleled networking opportunities to help you stay ahead of the curve in the rapidly evolving solar industry."
    },
    {
        "id": 2,
        "title": "Mental Health First Aid",
        "date": "Today · 7:30 - 8:30pm GMT+5:30",
        "location": "Online",
        "category": "Health",
        "image_url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F921409953%2F445073201422%2F1%2Foriginal.20241221-150919?w=940&auto=format%2Ccompress&q=75&sharp=10&rect=0%2C40%2C1280%2C640&s=ce9499e646925819a7aa59a944e27e7c",
         "description":"Welcome to Mental Health First Aid! Mental health is just as critical as physical health, yet many of us feel unprepared when faced with someone in distress. The Mental Health First Aid course aims to equip you with the knowledge and skills to recognize the signs of mental health and substance use challenges, and provide immediate help until professional support is available. This engaging and informative training will teach you how to respond compassionately and effectively to individuals experiencing mental health crises, ensuring that you can offer support in a way that fosters safety and understanding. Whether you are a caregiver, educator, colleague, or friend, the skills gained in this course will empower you to make a real difference in the lives of those struggling with mental health issues."
    },
      {
          "id": 3,
        "title": "Entrepreneur Exclusive Power Hour",
        "date": "Tomorrow · 1:00 AM GMT+5:30",
        "location": "Online",
        "category": "Business",
        "image_url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F928717573%2F92877393397%2F1%2Foriginal.20250106-171926?crop=focalpoint&fit=crop&w=940&auto=format%2Ccompress&q=75&sharp=10&fp-x=5e-07&fp-y=5e-07&s=e997f98bd3c225fcd118ec2417a99d56",
          "description":"Welcome to Entrepreneur Exclusive Power Hour! Are you an ambitious entrepreneur looking to elevate your business to new heights? The Entrepreneur Exclusive Power Hour is the perfect opportunity for you to fast-track your entrepreneurial journey with insightful strategies, expert advice, and actionable tips that you can apply immediately to scale your business. This exclusive session is designed to empower entrepreneurs by focusing on the critical elements that drive success in today’s competitive market. Whether you are just starting out or looking to take your existing business to the next level, this power hour will provide you with the tools, inspiration, and networking opportunities you need to make bold moves and achieve your goals." 
    },
    {  
         "id": 4,
        "title": "Glow from Within",
        "date": "Sunday, February 23 · 10:30 - 11:30pm GMT+5:30",
        "location": "Online",
        "category": "Fashion",
        "image_url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F959265793%2F188282376934%2F1%2Foriginal.20250212-183950?crop=focalpoint&fit=crop&w=940&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.215909090909&fp-y=0.350993377483&s=9630388d9e6cdf48c61c4a522765df8b",
        "description":"Welcome to Glow from Within! Are you ready to tap into your inner radiance and experience a deeper sense of self-love, balance, and energy? Glow from Within is a transformative wellness workshop designed to help you cultivate your inner beauty and well-being, empowering you to live a more balanced and fulfilling life. In today’s fast-paced world, it's easy to forget the importance of nurturing our inner selves. This workshop is here to remind you that true beauty comes from within, and when you align your mind, body, and soul, you can achieve a glowing, healthy, and vibrant life."
    },
    {   
         "id": 5,
        "title": "Radioactive Words: Warnings to Tomorrow",
        "date": "February 23 · 10:30pm - February 24 · 12:30am GMT+5:30",
        "location": "Online",
        "category": "Performing & Visual Arts categories",
        "image_url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F956750513%2F2536935747501%2F1%2Foriginal.20250210-063028?crop=focalpoint&fit=crop&w=940&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.5&fp-y=0.5&s=571479a5ef96bd5803926112dbaa7561",
        "description":"Welcome to Radioactive Words: Warnings to Tomorrow!The power of language is undeniable. It shapes our thoughts, our actions, and ultimately, the future we create. At Radioactive Words: Warnings to Tomorrow, we will explore how the words we use today carry weight, influence perceptions, and shape the world of tomorrow. This compelling seminar will delve into the far-reaching impact of language on society, the environment, and our collective future. As we face critical global challenges, understanding the responsibility that comes with the words we speak and write is more important than ever. In this thought-provoking event, we will examine how words can both inspire and harm, offering insight into the delicate balance between communication and responsibility. "
    }, 
    {   
        "id": 6,
        "title": "Wedding Syrup Fashion, Jewelry, Lifestyle Exhibition",
        "date": "March 1 · 11am - March 2 · 8pm IST",
        "location": "Online",
        "category": "Home & Lifestyle",
        "image_url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F955390423%2F2611010526521%2F1%2Foriginal.20250207-161747?crop=focalpoint&fit=crop&w=940&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.502901353965&fp-y=0.485401459854&s=ca79452d43977f5e7d65de332f5a3799",
        "description":"Welcome to Wedding Syrup Fashion, Jewelry, Lifestyle Exhibition! Step into a world of elegance, luxury, and timeless beauty at the Wedding Syrup Fashion, Jewelry, and Lifestyle Exhibition! This exclusive event is a one-stop destination for brides, grooms, and fashion enthusiasts to explore the finest collections in fashion, jewelry, and lifestyle products, all curated to make your wedding experience extraordinary. Whether you’re preparing for your big day, seeking the latest trends in wedding attire and accessories, or simply indulging in the art of fine living, this exhibition has something for everyone. From haute couture wedding gowns to statement jewelry and unique lifestyle products, the Wedding Syrup Exhibition offers an array of luxurious products and services to help you make your dreams come true. "
    }, 
     {  
         "id": 7,
        "title": "Soulful Experience River Cruises with Integrity Elite Travel & AmaWaterways",
        "date": "Friday, February 21 · 7:30 - 8:30am GMT+5:30",
        "location": "Online",
        "category": "Travel & Outdoor",
        "image_url": "https://img.evbuc.com/https%3A%2F%2Fcdn.evbuc.com%2Fimages%2F954868953%2F1221262430133%2F1%2Foriginal.20250206-232747?crop=focalpoint&fit=crop&w=940&auto=format%2Ccompress&q=75&sharp=10&fp-x=0.0461346633416&fp-y=0.912946428571&s=5fcce7340dcb0fb1fa40228f15d55766",
        "description":"Welcome to Soulful Experience River Cruises with Integrity Elite Travel & AmaWaterways! Embark on a journey like no other with Integrity Elite Travel & AmaWaterways as we invite you to experience the art of river cruising at its finest. The Soulful Experience River Cruise offers you a unique blend of cultural discovery, breathtaking views, and luxurious comfort—all while cruising along the world’s most iconic rivers. Imagine cruising on a beautifully designed riverboat, with panoramic windows offering scenic views of picturesque landscapes. Explore vibrant cities, hidden gems, and historic landmarks along the banks, all while enjoying unparalleled service and five-star amenities. This exceptional river cruise will take you on a journey of discovery and serenity, combining the pleasures of travel with the benefits of mindfulness, wellness, and soul-enriching experiences"
    },



]

@app.route("/browse")
def browse():
    return render_template("browse.html", events=events)


@app.route("/event/<int:index>")
def event_details(index):
    if 0 <= index < len(events):
        event = events[index]
        return render_template("event_details.html", event=event)
    else:
        return "Event not found", 404


@app.route("/add_to_cart/<int:event_id>")
def add_to_cart(event_id):
    if 'cart' not in session:
        session['cart'] = []

    if event_id not in session['cart']:
        session['cart'].append(event_id)
        session.modified = True

    return redirect(url_for('cart'))


@app.route("/remove_from_cart/<int:event_id>")
def remove_from_cart(event_id):
    if 'cart' in session:
        session['cart'] = [e for e in session['cart'] if e != event_id]
        session.modified = True

    return redirect(url_for('cart'))


@app.route("/cart")
def cart():
    cart_items = [e for e in events if e["id"] in session.get('cart', [])]
    return render_template("cart.html", cart=cart_items)



# @app.before_request
# def create_tables():
#     db.create_all()

@app.route('/contact',methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.form
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        # Do something with the data (save/email/etc)
        print(f"Received message from {name} ({email}): {message}")

        return redirect(url_for('submit_contact'))

    return render_template('contact.html')
    # return render_template('contact.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    # name = request.form['name']
    # email = request.form['email']
    # message = request.form['message']
    return render_template('submit_contact.html')


@app.route('/api/contact', methods=['POST'])
def contact_api():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data received'}), 400

    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    if not name or not email or not message:
        return jsonify({'error': 'Missing fields'}), 400
    

    # Save to database
    new_contact = Contact(name=name, email=email, message=message)
    db.session.add(new_contact)
    db.session.commit()

    # Send email notification
    # msg = Message(
    #     subject="New Contact Form Submission",
    #     sender=app.config['MAIL_USERNAME'],
    #     recipients=[app.config['MAIL_USERNAME']],  # or any target email
    #     body=f"Name: {name}\nEmail: {email}\nMessage:\n{message}"
    # )
    # mail.send(msg)


    # Save to DB, send email, etc.
    return jsonify({'message': 'Contact submitted successfully'}), 200



# Function to Send Email
def send_email(name, email, message):
    try:
        msg = Message('New Contact Message',
                  sender='your_email@gmail.com',
                  recipients=[email])  # send to user
        msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
        mail.send(msg)
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", e)

    # msg = Message('New Contact Form Submission',
    #               sender='your_email@gmail.com',
    #               recipients=['admin@example.com'])
    # msg.body = f"New message from {name} ({email}):\n\n{message}"
    # mail.send(msg)


@app.route('/show_contacts')
def show_contacts():
    contacts = Contact.query.all()
    return jsonify([{"name": c.name, "email": c.email, "message": c.message} for c in contacts])

def get_jwt_token(self, expires_in=3600):
        expiration = datetime.utcnow() + timedelta(seconds=expires_in)
        auth_token = jwt.encode(
            {'user_id': self.id, 'exp': expiration, 'role': self.role},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return auth_token

@staticmethod
def verify_jwt_token(token):
    try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = data.get('user_id')
            if user_id:
                return db.session.get(User, user_id) # Use get directly with user_id
            return None
    except Exception as e:
            return None
    

@app.route("/login-page", methods=["GET", "POST"]) # Renamed to avoid conflict with API route
def login_page():
    role = request.args.get('role', 'user')

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        user = User.query.filter_by(email=email, role=role).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid credentials!", "danger")

    return render_template("login.html", selected_role=role)


@app.route("/register-page", methods=["GET", "POST"]) # Added a dedicated route for the registration page
def register_page():
    role = request.args.get('role', 'user')

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        mobile = request.form.get("mobile")
        role = request.form.get("role")

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("register_page", role=role))

        if User.query.filter_by(email=email).first():
            flash("Email already exists!", "danger")
            return redirect(url_for("register_page", role=role))

        new_user = User(name=name, email=email, mobile=mobile, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login_page", role=role))

    return render_template("register.html", selected_role=role)


@app.route("/api/login", methods=["POST"]) # Dedicated API endpoint for login
def api_login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400

    email = data.get("email")
    password = data.get("password")
    role = data.get("role", 'user')  # Assuming role can be sent in the JSON

    user = User.query.filter_by(email=email, role=role).first()
    if user and user.check_password(password):
        auth_token = user.get_jwt_token()
        return jsonify({'message': 'Login successful!', 'token': auth_token, 'role': user.role, 'user_id': user.id}), 200
    else:
        return jsonify({'error': 'Invalid credentials! Please check your email and role.'}), 401

@app.route("/api/register", methods=["POST"]) # Dedicated API endpoint for registration
def api_register():
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    mobile = data.get("mobile")
    role = data.get("role", 'user') # Assuming role can be sent in the JSON

    if password != confirm_password:
        return jsonify({'error': 'Passwords do not match!'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists!'}), 409

    new_user = User(name=name, email=email, mobile=mobile, role=role)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Registration successful! Please log in.'}), 201


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "info")
    return redirect(url_for("home"))


featured_articles_data = [
    {"title": "Find your tickets"},
    {"title": "Request a refund"},
    {"title": "Contact the event organizer"},
    {"title": "What is this charge from Eventbrite?"},
    {"title": "Transfer tickets to someone else"},
    {"title": "Edit your order information"}
]

@app.route('/help')
def help():
    return render_template('help_center.html', featured_articles=featured_articles_data)

@app.route('/api/featured_articles')
def get_featured_articles():
    return jsonify(featured_articles_data)

@app.route('/api/users', methods=['GET'])
def get_all_users():
    try:
        users = User.query.all()
        user_list = []
        for user in users:
            user_data = {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'mobile': user.mobile,
                'role': user.role
            }
            user_list.append(user_data)
        return jsonify({'users': user_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)