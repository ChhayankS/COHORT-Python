Python 3.12.0 (v3.12.0:0fb18b02c8, Oct  2 2023, 09:45:56) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> from flask import Flask, render_template_string, request, redirect, url_for, Response, send_from_directory
... import threading
... from pymongo import MongoClient
... from bson.objectid import ObjectId
... from flask_mail import Mail, Message
... from werkzeug.utils import secure_filename
... import pandas as pd
... import pdfkit  # PDF generation using pdfkit
... import os
... import json
... 
... # Create Flask app
... app = Flask(__name__)
... 
... # Set up MongoDB connection (local MongoDB instance)
... client = MongoClient('mongodb://localhost:27017/')
... db = client['doss_database']
... collection = db['form_entries']
... 
... # Mail configuration
... app.config['MAIL_SERVER'] = 'smtp.gmail.com'
... app.config['MAIL_PORT'] = 465
... app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Update with your email
... app.config['MAIL_PASSWORD'] = 'your_password'  # Update with your password
... app.config['MAIL_USE_TLS'] = False
... app.config['MAIL_USE_SSL'] = True
... 
... mail = Mail(app)
... 
... # File Uploads Configuration
... UPLOAD_FOLDER = 'uploads'
... app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
... os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create upload folder if it doesn't exist
... 
... # Home Route - Form Creation (Create Entry)
@app.route('/')
def index():
    # HTML content for the form goes here (already present in your code)
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <!-- ...head content... -->
    </head>
    <body>
        <!-- ...body content with form... -->
    </body>
    </html>
    """
    return render_template_string(html_content)

# Submit form (Create operation)
@app.route('/submit', methods=['POST'])
def submit_form():
    try:
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        file = request.files['file']
        
        filename = None
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        entry = {'name': name, 'email': email, 'message': message, 'file': filename if file else None}
        collection.insert_one(entry)

        return redirect(url_for('view_entries'))
    except Exception as e:
        return str(e)

# Read Operation - View Entries
@app.route('/entries')
def view_entries():
    try:
        entries = list(collection.find())
        # HTML content to view entries goes here
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <!-- ...head content... -->
        </head>
        <body>
            <!-- ...body content with table of entries... -->
        </body>
        </html>
        """
        return render_template_string(html_content, entries=entries)
    except Exception as e:
        return str(e)

# Edit Operation - Load Entry Data for Editing
@app.route('/edit/<id>')
def edit_entry(id):
    try:
        entry = collection.find_one({'_id': ObjectId(id)})
        if not entry:
            return "Entry not found!"

        # HTML content for the edit form goes here
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <!-- ...head content... -->
        </head>
        <body>
            <!-- ...body content for editing entry... -->
        </body>
        </html>
        """
        return render_template_string(html_content)
    except Exception as e:
        return str(e)

# Update Operation - Save the Edited Entry
@app.route('/update/<id>', methods=['POST'])
def update_entry(id):
    try:
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        file = request.files['file']

        update_data = {'name': name, 'email': email, 'message': message}

        # If a new file is uploaded, replace the old file
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            update_data['file'] = filename

        # Update the database entry
        collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})
        
        return redirect(url_for('view_entries'))
    except Exception as e:
        return str(e)

# File Upload Handling
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Delete Operation
@app.route('/delete/<id>', methods=['POST'])
def delete_entry(id):
    try:
        collection.delete_one({'_id': ObjectId(id)})
        return redirect(url_for('view_entries'))
    except Exception as e:
        return str(e)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
