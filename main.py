from flask import Flask, request, jsonify
import requests
from pdfminer.high_level import extract_text
from io import BytesIO
from io import BytesIO
from io import BytesIO
import driver
import structured
import xlrd
import zipfile

sagicor_id1 = '1N4DlNDyL2pOipQtDrAOG10FHesGBblekGkIl-FrrCPY'
sagicor_id2 = '1S0hP3rC2aeBEA9rg0t5ixa_MhwOu7qKlX7zqhjesJ9Y'




guardian_id1 = '1bYVknK75j9wDW-c3H-SYjWw7XRk0AEtg3oWigsX9MoA'
guardian_id2 = '1oGKk4ig7eJnV-mSw_jg-pGxcRW3iuzKw7HVVHJTrrr0'


def driver_add_new_row_pdf(to_email,from_email, text):
    sheet = []
    id=''
    if to_email == 'info@primedicalja.com':
        if from_email == 'noreply@sagicor.com':
            data = structured.extract_structured_data(text)
            id = sagicor_id1    
        else:
            data = structured.extract_structured_data_guardian(text)
            id = guardian_id1
    else:
        if from_email == 'noreply@sagicor.com':
            data = structured.extract_structured_data(text)
            id = sagicor_id2 
        else:
            data = structured.extract_structured_data_guardian(text)
            id = guardian_id2





    for i in range(len(data)):
        new_list = []
        for key, value in data[i].items():
            new_list.append(value)
        sheet.append(new_list)

    driver.add_row(id,'Sheet1',sheet)
    return

def driver_add_new_row_xls(to_email,from_email,sheet):
    id = ''
    if to_email == 'info@primedicalja.com':
        if from_email == 'noreply@sagicor.com':
            id = sagicor_id1    
        else:
            id = guardian_id1
    else:
        if from_email == 'noreply@sagicor.com':
            id = sagicor_id2 
        else:
            id = guardian_id2   
            
    new_sheet = []
    for i in range(5, len(sheet)):
        list1 = [sheet[0][1],sheet[1][1],sheet[2][1],sheet[3][1],sheet[0][12],sheet[1][12],sheet[2][12]]
        
        list1 += sheet[i][:9]+sheet[i][-5:]
        new_sheet.append(list1)

    driver.add_row(id,'Sheet2', new_sheet)
    return


app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_xls_to_string():
   
    # Get the file path from the request (assuming it's part of the form data)
    url = request.form['file_path']
    to_email = request.form['to']
    from_email = request.form['from']


       
   
    if url is None:
        return 'No file path provided'
    # Decode the URL containing the PDF data
    response = requests.get(url)




    xls_file = BytesIO(response.content)

    workbook = xlrd.open_workbook(file_contents=xls_file.getvalue())

    sheet = workbook.sheet_by_index(0)
    sheet_list = []
    for row in range(sheet.nrows):
        # Extract the row values
        row_values = sheet.row_values(row)
        # Append the row values to the 'sheet_list'
        sheet_list.append(row_values)
    # print(sheet_list)
    driver_add_new_row_xls(to_email,from_email, sheet_list)
    return 'success'


    
@app.route('/pdf_convert', methods=['POST'])
def convert_pdf_to_string():
    url = request.form['file_path']

    to_email = request.form['to']
    from_email = request.form['from']



    if url is None:
        return 'No file path provided'
    response = requests.get(url)
    pdf_io = BytesIO(response.content)
    text = extract_text(pdf_io)



    
    driver_add_new_row_pdf(to_email,from_email, text)
    return 'success'


@app.route('/pdf_text', methods=['POST'])
def convert_pdf_to_text():
    url = request.form['file_path']

    if url is None:
        return 'No file path provided'
    response = requests.get(url)
    

    print(url)



    attachment_zip = response.headers['Content-Disposition'].__contains__('zip')
    text = ''
    
    if attachment_zip:
        
    
        zip_file_bytes = BytesIO(response.content)

        with zipfile.ZipFile(zip_file_bytes, 'r') as zip_ref:
            # This list comprehension gets all the names of the files that end with '.pdf'
            pdf_files = [file for file in zip_ref.namelist() if file.endswith('.pdf')]
            print(len(pdf_files))
            # Ensure there are at least two PDF files
            if len(pdf_files) >= 2:
                # Step 4: Extract the second PDF file assuming the files are correctly ordered
                second_pdf_name = pdf_files[1]  # Get the name of the second PDF file
                zip_ref.extract(second_pdf_name, path='desired/output/directory')  # Extract it to a directory
                print(f"The second PDF '{second_pdf_name}' has been extracted.")
            else:
                print("The ZIP archive does not contain two PDF files.")
    else: 
        

        
        pdf_io = BytesIO(response.content)


        text = extract_text(pdf_io)
    return text


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

