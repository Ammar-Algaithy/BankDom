from flask import Flask, render_template, request, redirect, url_for, session, flash
from app.models.user import User

app = Flask(__name__, template_folder='app/templates')
app.secret_key = 'your_secret_key_here'



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userName = request.form.get('userName')
        password = request.form.get('password')
        result = User.check_credentials(userName, password)
        check = result[0]
        userID = result[1]
        if check:
            session['user_id'] = userID
            session['userName'] = userName
            return redirect(url_for('account'))
        
    return render_template('auth/login.html', error="Invalid credentials")

@app.route('/register', methods=['GET', 'POST'])
def register():
    user1 = None
    if request.method == 'POST':
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        email = request.form.get('email')
        user_name = request.form.get('userName')
        password = request.form.get('password')
        account_type = request.form.get('accountType')
        balance = request.form.get('balance')
        user1 = User(
            customer_user_name= user_name,
            customer_first_name= first_name,
            customer_last_name= last_name,
            customer_email= email,
            customer_password= password,
            account_type= account_type,
            balance= balance
        )
        user1.insert_into_database()
        userID = User.getUserID(user_name)
        session['user_id'] = userID
        return render_template('account.html', user=session['user_id'])
    return render_template('auth/register.html')
@app.route('/account')
def account():
    # Check if the user is logged in (you can implement this logic)
    if 'user_id' in session:
        # Fetch user data or perform any necessary operations here
        # For example, you can retrieve user data from the database
        # user_id = session['user_id']
        # user = User.query.filter_by(customer_user_name=user_id).first()
        accounts = User.getAccounts(session['user_id'])
        print("================================", accounts)
        # Render the account settings template with user data
        return render_template('account.html', userID=session['user_id'], accounts=accounts, userName=session['userName'])  # Pass user data to the template
    else:
        # If the user is not logged in, you can redirect them to the login page
        return redirect(url_for('login'))


@app.route('/create/account', methods=['GET'])
def create_account():
    if request.method == 'GET':
        data = User.get_user_info(session['user_id'])
        User.createAccount(data)
        accounts = User.getAccounts(session['user_id'])
        print('Account created', accounts)
        return redirect(url_for('account'))
    else:
        return render_template('account.html', error="Invalid credentials")


@app.route('/logout', methods=['GET'])
def logout():
    # Clear session data
    session.pop('user_id', None)  # Replace 'user_id' with the key(s) you want to clear
    
    # Optionally, you can add a message to indicate that the user is logged out
    flash('You have been logged out', 'success')  # You should import 'flash' from flask
    
    # Redirect the user to the login or home page
    return redirect(url_for('login'))  # Replace 'login' with the appropriate route

    
if __name__ == '__main__':
    User.getAccounts('20240203223405-244917')
    app.run(debug=True)
