import os
from flask import Flask, render_template, request, redirect, session,flash
from models import init_db, get_db_connection


app = Flask(__name__)
app.secret_key = 'secret123'

init_db()


# Home Route
@app.route('/')
def home():
    return render_template('index.html')

# about

@app.route('/about')
def about():
    return render_template('about.html')


# ✅ Register Route

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (name, email, password, role)
                VALUES (?, ?, ?, ?)
            ''', (name, email, password, role))

            conn.commit()
            flash("Registration successful ✅")

            # ✅ Role-based redirect
            if role == 'student':
                return redirect('/login')   # go to login

            elif role == 'tutor':
                return redirect('/form')    # go to form

        except Exception as e:
            print("ERROR:", e)
            flash("Email already exists ❌")
            return redirect('/register')

        finally:
            conn.close()

    return render_template('register.html')



# @form

# @app.route('/form', methods=['GET', 'POST'])
# def details():
#     if request.method == 'POST':
#         # 📥 Get form data
#         name = request.form['name']
#         email = request.form['email']
#         phone = request.form['phone']
#         qualification = request.form['qualification']
#         years = request.form['years']
#         subjects = request.form['subjects']
#         mode = request.form['mode']
#         address = request.form['address']
#         skills = request.form['skills']

        # # 📁 Handle file upload
        # file = request.files['file']

      
        # if file and file.filename != '':
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # 💾 Store in database
        # conn = get_db_connection()
        # cursor = conn.cursor()

        # filename = None

        # cursor.execute('''
        #     INSERT INTO details 
        #     (name, email, phone, qualification,years, subjects, mode,address, skills)
        #     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        # ''', (name, email, phone,  qualification,years, subjects, mode, address, skills))

    

       

    #     cursor.execute('''
    #           INSERT INTO details 
    #           (name, email, phone, qualification, years, subjects, mode, address, file, skills)
    #           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    #       ''', (name, email, phone, qualification, years, subjects, mode, address, filename, skills))



    #     conn.commit()
    #     conn.close()

    #     flash("Details submitted successfully ✅")

    #     return redirect('/login')  # or redirect somewhere else

    # return render_template('form.html')

@app.route('/form', methods=['GET', 'POST'])
def details():
    if request.method == 'POST':

        user_id = session['user_id']   # 🔥 IMPORTANT

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        qualification = request.form['qualification']
        years = request.form['years']
        subjects = request.form['subjects']
        mode = request.form['mode']
        address = request.form['address']
        skills = request.form['skills']

        conn = get_db_connection()
        cursor = conn.cursor()

        filename = None

        cursor.execute('''
            INSERT INTO details 
            (user_id, name, email, phone, qualification, years, subjects, mode, address, file, skills)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, email, phone, qualification, years, subjects, mode, address, filename, skills))

        conn.commit()
        conn.close()

        flash("Details submitted successfully ✅")
        return redirect('/login')

    return render_template('form.html')

# Admin/View Users dashboard
@app.route('/admin/users')
def view_users():
    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return "Access Denied ❌"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()

    conn.close()

    return render_template('view_users.html', users=users)

# Admin/View tutors dashboard
@app.route('/admin/tutors')
def view_tutors():
    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return "Access Denied ❌"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users 
        WHERE role = 'tutor' AND is_approved = 0
    ''')

    tutors = cursor.fetchall()
    conn.close()

    return render_template('approve_tutors.html', tutors=tutors)

# Admin-tutors-approval
# @app.route('/admin/approve/<int:user_id>')
# def approve_tutor(user_id):
#     if 'user_id' not in session:
#         return redirect('/login')

#     if session['role'] != 'admin':
#         return "Access Denied ❌"

#     conn = get_db_connection()
#     cursor = conn.cursor()

#     cursor.execute('''
#         UPDATE users SET is_approved = 1 WHERE id = ?
#     ''', (user_id,))

#     conn.commit()
#     conn.close()

#     return redirect('/admin/tutors')

@app.route('/admin/approve/<int:user_id>')
def approve_tutor(user_id):
    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'admin':
        return "Access Denied ❌"

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ Approve tutor
    cursor.execute('UPDATE users SET is_approved = 1 WHERE id = ?', (user_id,))
    conn.commit()

    # ✅ GET tutor details
    cursor.execute('SELECT email, name FROM users WHERE id = ?', (user_id,))
    tutor = cursor.fetchone()

    conn.close()

    # ✅ SEND EMAIL HERE
    # send_approval_email(tutor['email'], tutor['name'])

    flash("Tutor approved and email sent ✅")
    return redirect('/admin/tutors')


# ✅ Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM users WHERE email = ? AND password = ?
        ''', (email, password))

        user = cursor.fetchone()
        conn.close()

        if user:
            # ✅ Tutor approval check
            if user['role'] == 'tutor' and user['is_approved'] == 0:
                return "Waiting for Admin Approval ⏳"

            # ✅ Store session
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']

            return redirect('/dashboard')

        else:
            return "Invalid Credentials ❌"

    return render_template('login.html')


# ✅ Dashboard (Role-Based)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    role = session['role']

    if role == 'student':
        return render_template('student_dashboard.html')

    elif role == 'tutor':
        return render_template('tutor_dashboard.html')

    elif role == 'admin':
        return render_template('admin_dashboard.html')

    else:
        return "Invalid Role ❌"


# ✅ Add Slot (ONLY Tutor)
@app.route('/add-slot', methods=['GET', 'POST'])
def add_slot():
    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'tutor':
        return "Access Denied ❌"

    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        tutor_id = session['user_id']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO slots (tutor_id, date, time)
            VALUES (?, ?, ?)
        ''', (tutor_id, date, time))

        conn.commit()
        conn.close()

        return "Slot Added Successfully ✅"

    return render_template('add_slot.html')


# ✅ View Tutor Slots
@app.route('/my-slots')
def my_slots():
    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'tutor':
        return "Access Denied ❌"

    tutor_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM slots WHERE tutor_id = ?
    ''', (tutor_id,))

    slots = cursor.fetchall()
    conn.close()

    return render_template('view_slots.html', slots=slots)


# ✅ View All Available Slots (ONLY Student)
@app.route('/all-slots')
def all_slots():
    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] not in ['student', 'admin']:
        return "Access Denied ❌"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM slots WHERE is_booked = 0
    ''')

    slots = cursor.fetchall()
    conn.close()

    return render_template('all_slots.html', slots=slots)


# ✅ Book Slot (ONLY Student)
@app.route('/book/<int:slot_id>')
def book_slot(slot_id):
    if 'user_id' not in session:
        return redirect('/login')

    if session['role'] != 'student':
        return "Access Denied ❌"

    student_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check slot availability
    cursor.execute('SELECT * FROM slots WHERE id = ? AND is_booked = 0', (slot_id,))
    slot = cursor.fetchone()

    if slot is None:
        return "Slot not available ❌"

    # Insert booking
    cursor.execute('''
        INSERT INTO bookings (student_id, tutor_id, slot_id, status)
        VALUES (?, ?, ?, ?)
    ''', (student_id, slot['tutor_id'], slot_id, 'booked'))

    # Mark slot booked
    cursor.execute('''
        UPDATE slots SET is_booked = 1 WHERE id = ?
    ''', (slot_id,))

    conn.commit()
    conn.close()

    return "Slot Booked Successfully ✅"


# ✅ My Bookings (ONLY Student)
@app.route('/my-bookings')
def my_bookings():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ If admin → show all bookings
    if session['role'] == 'admin':
        cursor.execute('''
            SELECT bookings.*, slots.date, slots.time
            FROM bookings
            JOIN slots ON bookings.slot_id = slots.id
        ''')

    # ✅ If student → show only their bookings
    elif session['role'] == 'student':
        student_id = session['user_id']
        cursor.execute('''
            SELECT bookings.*, slots.date, slots.time
            FROM bookings
            JOIN slots ON bookings.slot_id = slots.id
            WHERE bookings.student_id = ?
        ''', (student_id,))

    else:
        return "Access Denied ❌"

    bookings = cursor.fetchall()
    conn.close()

    return render_template('bookings.html', bookings=bookings)

# ✅ Cancel Booking
@app.route('/cancel/<int:booking_id>')
def cancel_booking(booking_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT slot_id FROM bookings WHERE id = ?', (booking_id,))
    booking = cursor.fetchone()

    if booking:
        slot_id = booking['slot_id']

        cursor.execute('UPDATE slots SET is_booked = 0 WHERE id = ?', (slot_id,))
        cursor.execute('UPDATE bookings SET status = "cancelled" WHERE id = ?', (booking_id,))

        conn.commit()

    conn.close()

    return redirect('/my-bookings')

# @ for table links
@app.route('/user/<int:user_id>')
def user_details(user_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT users.*, details.phone, details.qualification, details.years,
               details.subjects, details.mode, details.address, details.skills
        FROM users
        LEFT JOIN details ON users.email = details.email
        WHERE users.id = ?
    ''', (user_id,))

    user = cursor.fetchone()

    conn.close()

    return render_template('user_details.html', user=user)


# ✅ Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)