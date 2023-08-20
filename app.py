import dbm
import io
from flask import Flask, render_template, request, redirect, session, url_for, flash
import pyrebase
from datetime import datetime
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure secret key
import csv
from flask import Response


import pyrebase

#firebase start
config = {
    "apiKey": "AIzaSyD565dx672kuJqDlzO1Lsb1Q9ClJPxbBYc",
    "authDomain": "smart-parking-system-edcde.firebaseapp.com",
    "databaseURL": "https://smart-parking-system-edcde-default-rtdb.firebaseio.com/",
    "projectId": "smart-parking-system-edcde",
    "storageBucket": "smart-parking-system-edcde.appspot.com",
    "messagingSenderId": "1053910320425",
    "appId": "1:1053910320425:web:c4d6735ec1764bcea56338",
    "measurementId": "MRRBHF1GGT"
}

firebase  = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
#firebase end

@app.route('/dashboard')
def dashboard():
    try:
        # Fetch all invoices from Firebase and convert to a list of dictionaries
        all_invoices_data = db.child('invoices').get().val()
        all_invoices_list = []
        
        if all_invoices_data:
            for user_id, user_invoices in all_invoices_data.items():
                for invoice_key, invoice_values in user_invoices.items():
                    invoice_dict = {'user_id': user_id, 'id': invoice_key, **invoice_values}
                    all_invoices_list.append(invoice_dict)
        
        return render_template('dashboard.html', invoices=all_invoices_list)
    except Exception as e:
        # Handle error here
        return render_template('dashboard.html', invoices=[])




@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            if email == 'admin11@gmail.com' and password == 'admin123':
                # Special case for admin login, redirect to dashboard
                return redirect(url_for('dashboard'))
            else:
                # Sign in with email and password using Firebase
                user = auth.sign_in_with_email_and_password(email, password)
                # If successful, redirect to the home page
                return redirect(url_for('home'))
        except Exception as e:
            # Handle login error, show error message
            flash(f'Login failed: {str(e)}', 'error')

    return render_template('login.html')

@app.route('/remove-invoice', methods=['POST'])
def remove_invoice():
    try:
        user = auth.current_user
        user_id = user['localId']
        
        record_id = request.form['recordId']
        
        # Remove record from Firebase
        db.child('invoices').child(user_id).child(record_id).remove()
        
        return 'Record removed successfully'
    except Exception as e:
        return 'An error occurred while removing the record: ' + str(e)



@app.route('/form')
def form():
    slot_name = request.args.get('slot') 
    return render_template('form.html', slot_name=slot_name)


@app.route('/invoice', methods=['GET', 'POST'])
def invoice():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form['name']
        car_name = request.form['carName']
        car_number = request.form['carNumber']
        start_time = datetime.strptime(request.form['startTime'], '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(request.form['endTime'], '%Y-%m-%dT%H:%M')
        slot_name = request.form['slot']
        phone_number = request.form['phoneNumber']

        # Calculate parking duration in hours and minutes
        duration_seconds = (end_time - start_time).total_seconds()  # Get total seconds between start and end
        duration_hours = duration_seconds / 3600  # Convert seconds to hours

# Calculate total parking fee based on duration (example: 30 rupees per hour)
        parking_fee_per_hour = 30
        parking_fee = duration_hours * parking_fee_per_hour

# Format the total duration as a string in hours and minutes
        total_duration_hours = int(duration_hours)
        total_duration_minutes = int((duration_hours - total_duration_hours) * 60)
        formatted_duration = f"{total_duration_hours} hours {total_duration_minutes} minutes"

        try:
            # Save data under the user's ID
            user = auth.current_user
            user_id = user['localId']
            invoice_data = {
                'name': name,
                'car_name': car_name,
                'car_number': car_number,
                'start_time': str(start_time),
                'end_time': str(end_time),
                'duration': formatted_duration,
                'parking_fee': parking_fee,
                'slot': slot_name,
                'phone_number': phone_number
            }
            db.child('invoices').child(user_id).push(invoice_data)

            # Pass form data and calculated fee to the template
            return render_template('invoice.html', name=name, car_name=car_name, car_number=car_number,
                                   start_time=start_time, end_time=end_time, duration=formatted_duration,
                                   parking_fee=parking_fee, slot_name=request.form['slot'], phone_number=phone_number)

        except Exception as e:
            # Handle error here
            return render_template('invoice.html')

#download history invoice
@app.route('/download-csv')
def download_csv():
    try:
        user = auth.current_user
        user_id = user['localId']
        
        invoices_data = db.child('invoices').child(user_id).get().val()
        
        if invoices_data:
            csv_data = []
            for invoice_key, invoice_values in invoices_data.items():
                csv_row = [
                    invoice_values['name'],
                    invoice_values['car_name'],
                    invoice_values['car_number'],
                    invoice_values['start_time'],
                    invoice_values['end_time'],
                    invoice_values['duration'],
                    invoice_values['parking_fee'],
                    invoice_values['slot'],
                    invoice_values['phone_number']
                ]
                csv_data.append(csv_row)
                
            # Create a CSV file in-memory and send it as a response
            csv_output = io.StringIO()
            csv_writer = csv.writer(csv_output)
            csv_writer.writerow(['Name', 'Car Name', 'Car Number', 'Start Time', 'End Time', 'Duration (hours)', 'Parking Fee (rupees)', 'Slot Name', 'Phone Number'])
            csv_writer.writerows(csv_data)
            
            response = Response(csv_output.getvalue(), content_type='text/csv')
            response.headers['Content-Disposition'] = 'attachment; filename=invoice_data.csv'
            return response
        else:
            return "No invoice data available for download."
    except Exception as e:
        # Handle error here
        return "An error occurred while generating the CSV file."


@app.route('/history')
def history():
    try:
        user = auth.current_user
        user_id = user['localId']
        
        # Fetch invoices for the current user from Firebase and convert to a list of dictionaries
        user_invoices = db.child('invoices').child(user_id).get().val()
        invoices_list = []
        
        if user_invoices:
            for invoice_key, invoice_values in user_invoices.items():
                invoice_dict = {'id': invoice_key, **invoice_values}
                invoices_list.append(invoice_dict)
        
        return render_template('history.html', invoices=invoices_list)
    except Exception as e:
        # Handle error here
        return render_template('history.html', invoices=[])



@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match!', 'error')
        else:
            try:
                # Create a user account using Firebase authentication
                user = auth.create_user_with_email_and_password(email, password)
                # Optionally, store additional user data in the database under the 'users' node
                user_data = {
                    'email': email,
                }
                db.child('users').child(user['localId']).set(user_data)

                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                # Handle specific Firebase errors
                if 'EMAIL_EXISTS' in str(e):
                    flash('The email is already registered. Please use a different email.', 'error')
                else:
                    flash('Registration failed. Please try again later.', 'error')

    return render_template('register.html')


parking_slots = [
    {'id': 1, 'available': True},
    {'id': 2, 'available': False},
    # Add more slots here
]

@app.route('/update-slot-count', methods=['POST'])
def update_slot_count():
    slot_count = int(request.form.get('slot_count', 0))

    # Update slot count in Firebase
    db.child('slot_count').set(slot_count)

    # Update slot statuses
    for slot_id in range(1, slot_count + 1):
        slot_status = 1 if db.child(f'slot_{slot_id}').get().val() == 1 else 0
        db.child(f'slot_{slot_id}').set(slot_status)

    return redirect(url_for('book'))

@app.route('/book')  # Add the '/book' route for the Book page
def book():
    return render_template('book.html')




@app.route('/logout')  # Add the '/logout' route for logout functionality
def logout():
    # Your logout logic here
    return redirect(url_for('login'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']

        try:
            # Send reset password email using Firebase
            auth.send_password_reset_email(email)
            flash('A password reset email has been sent. Please check your inbox.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Failed to send password reset email. Please check your email address.', 'error')

    return render_template('forgotPassword.html')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']
        confirm_new_password = request.form['confirm_new_password']

        if new_password != confirm_new_password:
            flash('Passwords do not match. Please try again.', 'error')
            return redirect(url_for('forgot_password'))

        try:
            # Reset password using Firebase
            user = auth.get_user_by_email(email)
            auth.update_user(user['localId'], password=new_password)
            flash('Password successfully updated. You can now log in with the new password.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Failed to update password. Please check your email address.', 'error')
            return redirect(url_for('forgot_password'))

    return redirect(url_for('forgot_password'))

if __name__ == '__main__':
    app.run(debug=True)
