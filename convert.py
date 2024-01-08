from flask import Flask, request, jsonify
import os
import requests
import pandas as pd

from urllib.parse import urlparse, parse_qs
import os
import PyPDF2
from io import BytesIO
from urllib.parse import unquote
from urllib.parse import unquote
from io import StringIO, BytesIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from io import BytesIO



app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_xls_to_csv():
    try:
        # Get the file path from the request (assuming it's part of the form data)
        
        url = request.form['file_path']
       
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # If the response contains header information indicating that the content is an xls file,
            # or you know beforehand that the content will be in Excel format, read it into a DataFrame
            excel_data = pd.read_excel(BytesIO(response.content))

        result = excel_data.to_string()
   

        return result
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500
    
@app.route('/pdf_convert', methods=['POST'])
def convert_pdf_to_string():
    try:
        # Get the file path from the request (assuming it's part of the form data)
        
        url = request.form['file_path']
       
        encoded_url = url
        try:
            # Make a HEAD request to the encoded URL
            response = requests.head(encoded_url)
            decoded_url = unquote(encoded_url)
            response1 = requests.get(decoded_url, stream=True)
            content = None

            contains_pdf = response.headers.get('Content-Type', '').lower() == 'application/pdf'
            file_name = None

            if contains_pdf:

                content = response
                pdf_full_text= None

                file_like_object = BytesIO(response1.content)
                output_string = StringIO()
                laparams = LAParams()


                extract_text_to_fp(file_like_object, output_string, laparams=laparams)

                text_content = output_string.getvalue()

                content_disposition = response.headers.get('Content-Disposition')
                
                if content_disposition:
                    # Parse the filename from the Content-Disposition header
                    disposition_parts = content_disposition.split(';')
                    for part in disposition_parts:
                        if 'filename=' in part:
                            file_name = part.replace('filename=', '').strip().strip('"')
                            break
                else:
                    # Fallback to parsing the filename from the URL if no Content-Disposition header
                    url_path = urlparse(encoded_url).path
                    file_name = os.path.basename(url_path)

        except Exception as e:
            # Return an error message in case of an exception
            result = {'error': str(e)}
        else:
            # Return a dictionary with the result
            result = text_content
        print(result)
        # You would typically send 'result' back to Zapier or use it in further processing
        return result
    except Exception as e:
        # Handle any exceptions that occur
        return jsonify({"error": str(e)}), 500   



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)





# Assuming 'input_data' is provided by Zapier
# encoded_url = input_data['attachment']
