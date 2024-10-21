{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 35,
   "id": "b201b058-f5ee-40e0-ac95-27fb2dbeac3f",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " * Serving Flask app '__main__'\n",
      " * Debug mode: off\n"
     ]
    },
    {
     "data": {
      "text/html": [
       "<a href='http://127.0.0.1:5000' target='_blank'>Click here to view the CRUD form</a>"
      ],
      "text/plain": [
       "<IPython.core.display.HTML object>"
      ]
     },
     "metadata": {},
     "output_type": "display_data"
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.\n",
      " * Running on http://127.0.0.1:5020\n",
      "Press CTRL+C to quit\n"
     ]
    }
   ],
   "source": [
    "from flask import Flask, render_template_string, request, redirect, url_for, Response, send_from_directory\n",
    "import threading\n",
    "from pymongo import MongoClient\n",
    "from bson.objectid import ObjectId\n",
    "from flask_mail import Mail, Message\n",
    "from werkzeug.utils import secure_filename\n",
    "import pandas as pd\n",
    "import pdfkit  # PDF generation using pdfkit\n",
    "import os\n",
    "import json\n",
    "\n",
    "# Create Flask app\n",
    "app = Flask(__name__)\n",
    "\n",
    "# Set up MongoDB connection (local MongoDB instance)\n",
    "client = MongoClient('mongodb://localhost:27017/')\n",
    "db = client['doss_database']\n",
    "collection = db['form_entries']\n",
    "\n",
    "# Mail configuration\n",
    "app.config['MAIL_SERVER'] = 'smtp.gmail.com'\n",
    "app.config['MAIL_PORT'] = 465\n",
    "app.config['MAIL_USERNAME'] = 'your_email@gmail.com'  # Update with your email\n",
    "app.config['MAIL_PASSWORD'] = 'your_password'  # Update with your password\n",
    "app.config['MAIL_USE_TLS'] = False\n",
    "app.config['MAIL_USE_SSL'] = True\n",
    "\n",
    "mail = Mail(app)\n",
    "\n",
    "# File Uploads Configuration\n",
    "UPLOAD_FOLDER = 'uploads'\n",
    "app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER\n",
    "os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create upload folder if it doesn't exist\n",
    "\n",
    "# Home Route - Form Creation (Create Entry)\n",
    "@app.route('/')\n",
    "def index():\n",
    "    html_content = \"\"\"\n",
    "    <!DOCTYPE html>\n",
    "    <html lang=\"en\">\n",
    "    <head>\n",
    "        <meta charset=\"UTF-8\">\n",
    "        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n",
    "        <title>DOSS MEDIATECH CRUD Form</title>\n",
    "        <!-- Bootstrap 5 CSS -->\n",
    "        <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css\" rel=\"stylesheet\">\n",
    "        <!-- Google Fonts -->\n",
    "        <link href=\"https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap\" rel=\"stylesheet\">\n",
    "        <style>\n",
    "            body {\n",
    "                font-family: 'Roboto', sans-serif;\n",
    "                background-color: #f7f7f7;\n",
    "                color: #333;\n",
    "                padding-top: 50px;\n",
    "                transition: background-color 0.5s ease, color 0.5s ease;\n",
    "            }\n",
    "            body.dark {\n",
    "                background-color: #1a1a1a;\n",
    "                color: #f7f7f7;\n",
    "            }\n",
    "            .container {\n",
    "                background: #fff;\n",
    "                padding: 40px;\n",
    "                border-radius: 8px;\n",
    "                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);\n",
    "            }\n",
    "            .container.dark {\n",
    "                background-color: #333;\n",
    "            }\n",
    "            header {\n",
    "                background-color: #c8102e;\n",
    "                color: #fff;\n",
    "                padding: 20px;\n",
    "                border-radius: 8px;\n",
    "                margin-bottom: 30px;\n",
    "                display: flex;\n",
    "                justify-content: space-between;\n",
    "                align-items: center;\n",
    "            }\n",
    "            header h1 {\n",
    "                font-size: 2rem;\n",
    "                font-weight: 700;\n",
    "                margin: 0;\n",
    "                color: white;\n",
    "            }\n",
    "            header .logo img {\n",
    "                max-width: 100px;  /* Adjust this value as needed */\n",
    "                height: auto;      /* Maintain aspect ratio */\n",
    "                margin-right: 20px; /* Space between logo and text */\n",
    "            }\n",
    "            header .toggle-btn {\n",
    "                font-size: 1.5rem;\n",
    "                background-color: transparent;\n",
    "                border: none;\n",
    "                color: #fff;\n",
    "                cursor: pointer;\n",
    "            }\n",
    "            header .toggle-btn:hover {\n",
    "                color: #f7f7f7;\n",
    "            }\n",
    "            .form-label {\n",
    "                font-weight: 500;\n",
    "                color: #333;\n",
    "            }\n",
    "            .form-label.dark {\n",
    "                color: #f7f7f7;\n",
    "            }\n",
    "            .btn-custom {\n",
    "                background-color: #c8102e;\n",
    "                color: white;\n",
    "                border-radius: 8px;\n",
    "                font-weight: 500;\n",
    "                transition: background-color 0.3s ease;\n",
    "            }\n",
    "            .btn-custom:hover {\n",
    "                background-color: #a60d25;\n",
    "            }\n",
    "            .export-btn-group {\n",
    "                margin-top: 20px;\n",
    "            }\n",
    "            .export-btn-group a {\n",
    "                margin-right: 10px;\n",
    "            }\n",
    "        </style>\n",
    "        <script>\n",
    "            function toggleTheme() {\n",
    "                document.body.classList.toggle('dark');\n",
    "                const container = document.querySelector('.container');\n",
    "                container.classList.toggle('dark');\n",
    "                const labels = document.querySelectorAll('.form-label');\n",
    "                labels.forEach(label => label.classList.toggle('dark'));\n",
    "            }\n",
    "        </script>\n",
    "    </head>\n",
    "    <body>\n",
    "        <header>\n",
    "            <div class=\"logo\">\n",
    "                <img src=\"https://i.postimg.cc/WbsKPNZ0/temp-Imager-WOd-Kx.avif\"> <!-- Replace with actual logo -->\n",
    "            </div>\n",
    "            <div>\n",
    "                <h1>DOSS MEDIATECH</h1>\n",
    "                <small>CRUD Application</small>\n",
    "            </div>\n",
    "            <button class=\"toggle-btn\" onclick=\"toggleTheme()\">\n",
    "                <span class=\"bi bi-moon-fill\"></span> <!-- Toggle icon, replace with an icon font or graphic -->\n",
    "            </button>\n",
    "        </header>\n",
    "        <div class=\"container\">\n",
    "            <h2>Create a New Entry</h2>\n",
    "            <form action=\"/submit\" method=\"POST\" enctype=\"multipart/form-data\">\n",
    "                <div class=\"mb-3\">\n",
    "                    <label for=\"name\" class=\"form-label\">Name</label>\n",
    "                    <input type=\"text\" id=\"name\" name=\"name\" class=\"form-control\" required>\n",
    "                </div>\n",
    "                <div class=\"mb-3\">\n",
    "                    <label for=\"email\" class=\"form-label\">Email</label>\n",
    "                    <input type=\"email\" id=\"email\" name=\"email\" class=\"form-control\" required>\n",
    "                </div>\n",
    "                <div class=\"mb-3\">\n",
    "                    <label for=\"message\" class=\"form-label\">Message</label>\n",
    "                    <textarea id=\"message\" name=\"message\" class=\"form-control\" rows=\"4\" required></textarea>\n",
    "                </div>\n",
    "                <div class=\"mb-3\">\n",
    "                    <label for=\"file\" class=\"form-label\">Upload File</label>\n",
    "                    <input type=\"file\" id=\"file\" name=\"file\" class=\"form-control\">\n",
    "                </div>\n",
    "                <button type=\"submit\" class=\"btn btn-custom\">Submit</button>\n",
    "            </form>\n",
    "\n",
    "            <div class=\"export-btn-group mt-5\">\n",
    "                <h4>Export Options</h4>\n",
    "                <a href=\"/export/csv\" class=\"btn btn-info\">Export CSV</a>\n",
    "                <a href=\"/export/excel\" class=\"btn btn-success\">Export Excel</a>\n",
    "                <a href=\"/export/pdf\" class=\"btn btn-warning\">Export PDF</a>\n",
    "                <a href=\"/export/json\" class=\"btn btn-dark\">Export JSON</a>\n",
    "            </div>\n",
    "            <div class=\"mt-3\">\n",
    "                <a href=\"/entries\" class=\"btn btn-custom\">View Entries</a>\n",
    "            </div>\n",
    "        </div>\n",
    "\n",
    "        <!-- Bootstrap 5 JS -->\n",
    "        <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js\"></script>\n",
    "    </body>\n",
    "    </html>\n",
    "    \"\"\"\n",
    "    return render_template_string(html_content)\n",
    "\n",
    "# Submit form (Create operation)\n",
    "@app.route('/submit', methods=['POST'])\n",
    "def submit_form():\n",
    "    try:\n",
    "        name = request.form['name']\n",
    "        email = request.form['email']\n",
    "        message = request.form['message']\n",
    "        file = request.files['file']\n",
    "        \n",
    "        filename = None\n",
    "        if file:\n",
    "            filename = secure_filename(file.filename)\n",
    "            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))\n",
    "\n",
    "        entry = {'name': name, 'email': email, 'message': message, 'file': filename if file else None}\n",
    "        collection.insert_one(entry)\n",
    "\n",
    "        return redirect(url_for('view_entries'))\n",
    "    except Exception as e:\n",
    "        return str(e)\n",
    "\n",
    "# Read Operation - View Entries\n",
    "@app.route('/entries')\n",
    "def view_entries():\n",
    "    try:\n",
    "        entries = list(collection.find())\n",
    "        html_content = \"\"\"\n",
    "        <!DOCTYPE html>\n",
    "        <html lang=\"en\">\n",
    "        <head>\n",
    "            <meta charset=\"UTF-8\">\n",
    "            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n",
    "            <title>View Entries</title>\n",
    "            <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css\" rel=\"stylesheet\">\n",
    "            <style>\n",
    "                body { font-family: 'Roboto', sans-serif; line-height: 1.6; background-color: #f7f7f7; }\n",
    "                .container { padding: 40px; background: #fff; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); margin-top: 30px; }\n",
    "                .table th, .table td { padding: 12px 15px; }\n",
    "                .btn-custom { background-color: #c8102e; color: white; border-radius: 8px; font-weight: 500; }\n",
    "            </style>\n",
    "        </head>\n",
    "        <body>\n",
    "            <div class=\"container\">\n",
    "                <h1>View Form Entries</h1>\n",
    "                <table class=\"table table-striped table-hover\">\n",
    "                    <thead>\n",
    "                        <tr>\n",
    "                            <th>Name</th>\n",
    "                            <th>Email</th>\n",
    "                            <th>Message</th>\n",
    "                            <th>File</th>\n",
    "                            <th>Actions</th>\n",
    "                        </tr>\n",
    "                    </thead>\n",
    "                    <tbody>\n",
    "                        {% for entry in entries %}\n",
    "                        <tr>\n",
    "                            <td>{{ entry['name'] }}</td>\n",
    "                            <td>{{ entry['email'] }}</td>\n",
    "                            <td>{{ entry['message'] }}</td>\n",
    "                            <td>\n",
    "                                {% if entry['file'] %}\n",
    "                                    <a href=\"{{ url_for('uploaded_file', filename=entry['file']) }}\">Download</a>\n",
    "                                {% else %}\n",
    "                                    No file\n",
    "                                {% endif %}\n",
    "                            </td>\n",
    "                            <td>\n",
    "                                <a href=\"/edit/{{ entry['_id'] }}\" class=\"btn btn-primary btn-sm\">Edit</a>\n",
    "                                <form action=\"/delete/{{ entry['_id'] }}\" method=\"POST\" style=\"display:inline;\">\n",
    "                                    <button type=\"submit\" class=\"btn btn-danger btn-sm\">Delete</button>\n",
    "                                </form>\n",
    "                            </td>\n",
    "                        </tr>\n",
    "                        {% endfor %}\n",
    "                    </tbody>\n",
    "                </table>\n",
    "                <a href=\"/\" class=\"btn btn-custom mt-3\">Back to Form</a>\n",
    "            </div>\n",
    "\n",
    "            <!-- Bootstrap 5 JS -->\n",
    "            <script src=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js\"></script>\n",
    "        </body>\n",
    "        </html>\n",
    "        \"\"\"\n",
    "        return render_template_string(html_content, entries=entries)\n",
    "    except Exception as e:\n",
    "        return str(e)\n",
    "\n",
    "# Edit Operation - Load Entry Data for Editing\n",
    "@app.route('/edit/<id>')\n",
    "def edit_entry(id):\n",
    "    try:\n",
    "        entry = collection.find_one({'_id': ObjectId(id)})\n",
    "        if not entry:\n",
    "            return \"Entry not found!\"\n",
    "\n",
    "        # Populate the form with existing data\n",
    "        html_content = f\"\"\"\n",
    "        <!DOCTYPE html>\n",
    "        <html lang=\"en\">\n",
    "        <head>\n",
    "            <meta charset=\"UTF-8\">\n",
    "            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n",
    "            <title>Edit Entry</title>\n",
    "            <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css\" rel=\"stylesheet\">\n",
    "        </head>\n",
    "        <body>\n",
    "            <div class=\"container\">\n",
    "                <h1>Edit Entry</h1>\n",
    "                <form action=\"/update/{id}\" method=\"POST\" enctype=\"multipart/form-data\">\n",
    "                    <div class=\"mb-3\">\n",
    "                        <label for=\"name\" class=\"form-label\">Name</label>\n",
    "                        <input type=\"text\" id=\"name\" name=\"name\" class=\"form-control\" value=\"{entry['name']}\" required>\n",
    "                    </div>\n",
    "                    <div class=\"mb-3\">\n",
    "                        <label for=\"email\" class=\"form-label\">Email</label>\n",
    "                        <input type=\"email\" id=\"email\" name=\"email\" class=\"form-control\" value=\"{entry['email']}\" required>\n",
    "                    </div>\n",
    "                    <div class=\"mb-3\">\n",
    "                        <label for=\"message\" class=\"form-label\">Message</label>\n",
    "                        <textarea id=\"message\" name=\"message\" class=\"form-control\" required>{entry['message']}</textarea>\n",
    "                    </div>\n",
    "                    <div class=\"mb-3\">\n",
    "                        <label for=\"file\" class=\"form-label\">Upload New File (Leave blank to keep the current file)</label>\n",
    "                        <input type=\"file\" id=\"file\" name=\"file\" class=\"form-control\">\n",
    "                    </div>\n",
    "                    <button type=\"submit\" class=\"btn btn-primary\">Update</button>\n",
    "                    <a href=\"/entries\" class=\"btn btn-secondary\">Cancel</a>\n",
    "                </form>\n",
    "            </div>\n",
    "        </body>\n",
    "        </html>\n",
    "        \"\"\"\n",
    "        return render_template_string(html_content)\n",
    "    except Exception as e:\n",
    "        return str(e)\n",
    "\n",
    "# Update Operation - Save the Edited Entry\n",
    "@app.route('/update/<id>', methods=['POST'])\n",
    "def update_entry(id):\n",
    "    try:\n",
    "        name = request.form['name']\n",
    "        email = request.form['email']\n",
    "        message = request.form['message']\n",
    "        file = request.files['file']\n",
    "\n",
    "        update_data = {'name': name, 'email': email, 'message': message}\n",
    "\n",
    "        # If a new file is uploaded, replace the old file\n",
    "        if file:\n",
    "            filename = secure_filename(file.filename)\n",
    "            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))\n",
    "            update_data['file'] = filename\n",
    "\n",
    "        # Update the database entry\n",
    "        collection.update_one({'_id': ObjectId(id)}, {'$set': update_data})\n",
    "        \n",
    "        return redirect(url_for('view_entries'))\n",
    "    except Exception as e:\n",
    "        return str(e)\n",
    "\n",
    "# File Upload Handling\n",
    "@app.route('/uploads/<filename>')\n",
    "def uploaded_file(filename):\n",
    "    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)\n",
    "\n",
    "# Delete Operation\n",
    "@app.route('/delete/<id>', methods=['POST'])\n",
    "def delete_entry(id):\n",
    "    try:\n",
    "        collection.delete_one({'_id': ObjectId(id)})\n",
    "        return redirect(url_for('view_entries'))\n",
    "    except Exception as e:\n",
    "        return str(e)\n",
    "\n",
    "# Export to CSV\n",
    "@app.route('/export/csv')\n",
    "def export_csv():\n",
    "    entries = list(collection.find())\n",
    "    df = pd.DataFrame(entries)\n",
    "    csv_data = df.to_csv(index=False)\n",
    "\n",
    "    return Response(\n",
    "        csv_data,\n",
    "        mimetype=\"text/csv\",\n",
    "        headers={\"Content-disposition\": \"attachment; filename=entries.csv\"}\n",
    "    )\n",
    "\n",
    "# Export to Excel\n",
    "@app.route('/export/excel')\n",
    "def export_excel():\n",
    "    entries = list(collection.find())\n",
    "    df = pd.DataFrame(entries)\n",
    "    excel_data = df.to_excel(index=False)\n",
    "\n",
    "    return Response(\n",
    "        excel_data,\n",
    "        mimetype=\"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet\",\n",
    "        headers={\"Content-disposition\": \"attachment; filename=entries.xlsx\"}\n",
    "    )\n",
    "\n",
    "# Export to PDF\n",
    "@app.route('/export/pdf')\n",
    "def export_pdf():\n",
    "    entries = list(collection.find())\n",
    "    html = render_template_string('<h1>Entries</h1><ul>{% for entry in entries %}<li>{{ entry }}</li>{% endfor %}</ul>', entries=entries)\n",
    "    pdf = pdfkit.from_string(html, False)  # Generate PDF from HTML string\n",
    "\n",
    "    return Response(\n",
    "        pdf,\n",
    "        mimetype='application/pdf',\n",
    "        headers={\"Content-disposition\": \"attachment; filename=entries.pdf\"}\n",
    "    )\n",
    "\n",
    "# Export to JSON\n",
    "@app.route('/export/json')\n",
    "def export_json():\n",
    "    entries = list(collection.find())\n",
    "    json_data = json.dumps(entries, default=str)  # Convert to JSON, handle ObjectId\n",
    "\n",
    "    return Response(\n",
    "        json_data,\n",
    "        mimetype='application/json',\n",
    "        headers={\"Content-disposition\": \"attachment; filename=entries.json\"}\n",
    "    )\n",
    "\n",
    "# Run Flask in a separate thread\n",
    "def run_flask():\n",
    "    app.run(port=5020, debug=False, use_reloader=False)\n",
    "\n",
    "# Run Flask in the background\n",
    "flask_thread = threading.Thread(target=run_flask)\n",
    "flask_thread.start()\n",
    "\n",
    "# Show localhost link in Jupyter notebook\n",
    "from IPython.display import display, HTML\n",
    "display(HTML(\"<a href='http://127.0.0.1:5000' target='_blank'>Click here to view the CRUD form</a>\"))\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2584f024-e939-4989-9a93-5ef8b2b1e1ad",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}