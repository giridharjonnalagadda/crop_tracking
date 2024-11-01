from flask import Flask, render_template, redirect, url_for, request, flash, session
from pymongo import MongoClient 
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong, unique key for sessions

# Connect to MongoDB
client = MongoClient('mongodb+srv://giri:1234567890@cluster0.7qqi0.mongodb.net/')  # Replace with your MongoDB URI
db = client['crop']
users_collection = db['users']
products_collection=db['products']
orders=db['orders']
producers_collection=db['producers']

@app.route("/")
def home():
    return render_template('consumer_login.html')

@app.route('/login/producer', methods=['GET', 'POST'])
def login_producer():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user with the producer role in MongoDB
        user = producers_collection.find_one({'username': username})

        if user['username']==username and user['password']==password:
            # Store user info in session and redirect to the producer dashboard
            session['user_id'] = str(user['_id'])  # MongoDB IDs are ObjectIds
            return redirect(url_for('producer_dashboard'))
        else:
            # Invalid credentials: flash an error message
            flash('Invalid username or password', 'danger')
    
    # Render the login template for GET request
    return render_template('login_producer.html')

@app.route("/c_register")
def clogin():
    return render_template("consumer_register.html")

@app.route("/producer_register")
def prodreg():
    return render_template("producer_register.html")

@app.route('/consumer_register', methods=['GET', 'POST'])
def register1():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email already exists
        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose a different username.")
            return render_template("consumer_register.html")
        
        if users_collection.find_one({"email": email}):
            flash("Email already registered. Please use a different email or log in.")
            return redirect(url_for('register'))

        user_data = {
            "username": username,
            "email": email,
            "password":password
        }
        users_collection.insert_one(user_data)

        flash("Registration successful! Please log in.")
        return render_template('consumer_login.html')

    return render_template('consumer_login.html')

@app.route('/producer_register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email already exists
        if producers_collection.find_one({"username": username}):
            flash("Username already exists. Please choose a different username.")
            return render_template("producer_register.html")
        
        if producers_collection.find_one({"email": email}):
            flash("Email already registered. Please use a different email or log in.")
            return render_template("producer_register.html")

        user_data = {
            "username": username,
            "email": email,
            "password":password
        }
        producers_collection.insert_one(user_data)

        flash("Registration successful! Please log in.")
        return render_template("producer_login.html")

    return render_template('producer_register.html')

@app.route('/login/consumer', methods=['GET', 'POST'])
def login_consumer():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user with the consumer role in MongoDB
        user = users_collection.find_one({'username': username})

        if user and user['username'] == username and user['password'] == password:
            # Store user info in session and redirect to the consumer dashboard
            session['user_id'] = str(user['_id'])  # MongoDB IDs are ObjectIds
            return redirect(url_for('consumer_dashboard'))
        else:
            # Invalid credentials: flash an error message
            flash('Invalid username or password', 'danger')
    
    # Render the login template for GET request
    return render_template('consumer_login.html')

@app.route('/consumer_dashboard')
def consumer_dashboard():
    # Fetch all products from the products collection
    products = products_collection.find()  # Assuming products_collection is the products collection in MongoDB
    
    # Convert MongoDB cursor to a list of dictionaries for easier template rendering
    product_list = list(products)
    
    # Render the consumer dashboard template and pass the product list
    return render_template('consumer_dashboard.html', products=product_list)

@app.route("/consumer_login")
def cons_log():
    return render_template("consumer_login.html")

@app.route("/producer_login")
def prod_log():
    return render_template("producer_login.html")

@app.route('/producer_dashboard')
def producer_dashboard():
    # Retrieve the current user's ID from the session
    
    # Query to fetch only products that belong to the logged-in producer
    products = products_collection.find()
    
    # Convert the cursor to a list for rendering
    product_list = list(products)
    
    return render_template('producer_dashboard.html', products=product_list)


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        # Collect form data
        product_data = {
            "crop_name": request.form['crop_name'],
            "fertilizers_used": request.form['fertilizers_used'],
            "crop_type": request.form['crop_type'],
            "price_per_quintal": float(request.form['price_per_quintal']),
            "year_of_production": int(request.form['year_of_production']),
            "location": request.form['location'],
            "moisture_content": float(request.form['moisture_content']),
            "pesticides_used": request.form['pesticides_used'],
            "soil_ph": float(request.form['soil_ph']),
            "harvest_method": request.form['harvest_method'],
            # "added_by":session['user_id']
        }
        
        # Insert the product into MongoDB
        products_collection.insert_one(product_data)
        
        # Redirect to a success page or dashboard
        flash('Product added successfully!', 'success')
        return redirect(url_for('producer_dashboard'))
    
    # Render form for GET request
    return render_template('add_product.html')

@app.route('/place_order',methods=['post'])
def place_order():
    quantity = request.form['quantity']
    name=request.form['name']
    contact_info = request.form['contact_info']
    delivery_address = request.form['delivery_address']
    product=products_collection.find_one({"_id":ObjectId(session['id'])})

    # Here, you would typically process the order, e.g., save to database
    # For now, let's just flash a message and redirect back to the dashboard

    data={
        "name":name,
        "quantity":quantity,
        "contact_info":contact_info,
        "delivery_address":delivery_address,
        "crop_name": product.get("crop_name"),
        "fertilizers_used": product.get("fertilizers_used"),
        "crop_type": product.get("crop_type"),
        "price_per_quintal": product.get("price_per_quintal"),
        "year_of_production": product.get("year_of_production"),
        "location": product.get("location"),
        "moisture_content": product.get("moisture_content"),
        "pesticides_used": product.get("pesticides_used"),
        "soil_ph": product.get("soil_ph")
    }
    # data['ordered_by']=session['user_id']

    orders.insert_one(data)

    flash('Order placed successfully!', 'success')
    return redirect(url_for('consumer_dashboard'))

@app.route("/myorders")
def myorders():
    data=orders.find()
    return render_template("my_orders.html",product_details=data)

@app.route("/ordernow")
def onow():
    id=request.args.get("id")
    session['id']=id
    return render_template("order_now.html")


if __name__=="__main__":
    app.run(debug=True)


