from flask import Flask, render_template, request, flash, redirect, url_for, send_file
import os
import sys
import traceback
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename
sys.path.append(os.path.join(os.path.dirname(__file__), 'engine'))
from engine.inference import evaluate_loan_facts

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/evaluate', methods=['GET', 'POST'])
def evaluate_single():
    if request.method == 'GET':
        return render_template('index.html')
        
    try:
        annual_income = float(request.form['annual_income'])
        total_debt = float(request.form['total_debt'])
        income_sources = int(request.form['income_sources'])
        credit_score = int(request.form['credit_score'])
        bankruptcy = request.form['bankruptcy'] == 'yes'
        insurance = request.form['insurance'] == 'yes'
        
        if annual_income < 0 or total_debt < 0:
            raise ValueError('Income and debt must be non-negative numbers')
        if not (0 <= credit_score <= 100):
            raise ValueError('Credit score must be between 0 and 100')
            
        facts = {
            'income': annual_income,
            'debt': total_debt,
            'sources': income_sources,
            'credit_score': credit_score,
            'bankruptcy': bankruptcy,
            'insurance': insurance
        }
        result = evaluate_loan_facts(facts)
        return render_template('result.html', result=result)
    except Exception as e:
        print('Exception in /evaluate:', e)
        traceback.print_exc()
        return render_template('index.html', error=str(e))

@app.route('/upload', methods=['GET', 'POST'])
def upload_batch():
    if request.method == 'GET':
        return render_template('upload.html')
        
    if 'file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(request.url)
        
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(request.url)
        
    if not allowed_file(file.filename):
        flash('Invalid file type. Please upload .csv or .xlsx files only.', 'danger')
        return redirect(request.url)
        
    try:
        # Read the file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
            
        # Validate columns
        required_columns = ['income', 'debt', 'sources', 'credit_score', 'bankruptcy', 'insurance']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            flash(f'Missing required columns: {", ".join(missing_columns)}', 'danger')
            return redirect(request.url)
            
        # Process each row
        results = []
        for _, row in df.iterrows():
            facts = {
                'income': float(row['income']),
                'debt': float(row['debt']),
                'sources': int(row['sources']),
                'credit_score': int(row['credit_score']),
                'bankruptcy': str(row['bankruptcy']).lower() == 'yes',
                'insurance': str(row['insurance']).lower() == 'yes'
            }
            result = evaluate_loan_facts(facts)
            results.append({
                'decision': 'Approved' if result['approved'] else 'Declined',
                'explanation': '; '.join([f"{rule['message']}: {'Passed' if rule['passed'] else 'Failed'}" 
                                      for rule in result['rules'].values()])
            })
            
        # Add results to dataframe
        df['decision'] = [r['decision'] for r in results]
        df['explanation'] = [r['explanation'] for r in results]
        
        # Save processed file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'processed_{timestamp}_{secure_filename(file.filename)}'
        output_path = os.path.join(UPLOAD_FOLDER, output_filename)
        
        if output_filename.endswith('.csv'):
            df.to_csv(output_path, index=False)
        else:
            df.to_excel(output_path, index=False)
            
        # Send the file back to user
        return send_file(output_path, as_attachment=True, download_name=output_filename)
        
    except Exception as e:
        print('Exception in /upload:', e)
        traceback.print_exc()
        flash(f'Error processing file: {str(e)}', 'danger')
        return redirect(request.url)

@app.route('/about')
def about():
    return render_template('about.html')

@app.errorhandler(Exception)
def handle_exception(e):
    print('Global Exception:', e)
    traceback.print_exc()
    return render_template('index.html', error='A server error occurred: ' + str(e)), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
