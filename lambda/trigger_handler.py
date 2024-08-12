import json
import boto3
from botocore.config import Config
import time
import fitz 
import urllib.parse
import os
import uuid
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Extract bucket name and object key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Decode the URL-encoded object key
    decoded_key = urllib.parse.unquote_plus(key)
    
    print(f'Decoded key: {decoded_key}')
    decoded_key_without_extension = os.path.splitext(decoded_key)[0]
    s3_client = boto3.client('s3')

    try:
        # Check if the object exists
        s3_client.head_object(Bucket=bucket, Key=decoded_key)
        
        pdf_file_path = f'/tmp/{decoded_key.split("/")[-1]}'  # Ensure file name is safe for file system
        s3_client.download_file(bucket, decoded_key, pdf_file_path)
        
        
        # Read the PDF content using PyMuPDF
        document = fitz.open(pdf_file_path)
        pdf_text = ""
        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            pdf_text += page.get_text()

        document.close()
        os.remove(pdf_file_path)
        
        print(" pdf read complete")
        
        ClauseList = ["Minimum Transfer Amount", "Threshold", "Rounding"]
        
        final_response = ""
        
        # Initialize Bedrock client
        configure = Config(read_timeout=1000)
        bedrock_client = boto3.client('bedrock-agent-runtime', config=configure)  
        session_id = str(uuid.uuid4())
        agent_id = os.environ['AGENT_ID']
        agent_alias_id = os.environ['AGENT_ALIAS_ID']
        
        text_prompt = f''' 
              I'm going to provide you a document which is a ISDA Master Agreement. Remember this document. Wait until I ask about specific clauses.
        '''
            
        document_text = f''' 
            Here is the document:
            <Document>
            {pdf_text}
            </Document>
            '''
        final_prompt = text_prompt + document_text

        # Invoke Bedrock agent
        response = bedrock_client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                endSession=False,
                enableTrace=True,
                inputText=final_prompt
        )

        resBody = response['completion']
        answer = ""
        for event in resBody:
            if 'chunk' in event:
                chunk = event['chunk']['bytes'].decode('utf-8')
                answer += chunk
                print("Answer: ", answer)
        
        
        
         # Loop through each clause and call the agent
        for clause in ClauseList:
            loop_text_prompt = f''' 
            Apply the rules of Common Domain Model (CDM) json generation on the earlier provided document for the clause: {clause}. After processing, print the final CDM json output of this clause.strictly follow all the instructions and formats
            Please make sure to thoroughly review the entire document, including all schedules and annexes, even if they appear after the main body of the agreement. Carefully read through each section and paragraph, paying close attention to the headings and subheadings to identify relevant clauses. Before providing your final response, double-check your findings and conclusions to ensure accuracy and completeness.
            '''

            # Invoke Bedrock agent
            response = bedrock_client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                endSession=False,
                enableTrace=True,
                inputText=loop_text_prompt
            )

            resBody = response['completion']
            answer = ""
            for event in resBody:
                if 'chunk' in event:
                    chunk = event['chunk']['bytes'].decode('utf-8')
                    answer += chunk
                    print("Answer: ", answer)
            final_response += answer
        
        text_prompt = f''' 
             Apply the rules of Common Domain Model (CDM) JSON generation to this document for the following clauses: Base Currency and Eligible Currency. If not stated explicitly, assume USD as the base currency. Always generate two separate JSON outputs, one for each of Base Currency and Eligible Currency. Pay special attention to accurately search and process the Eligible Currency clause. After processing, print the individual JSON outputs for both clauses. Strictly follow all instructions and formats.
        '''
        response = bedrock_client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                endSession=False,
                enableTrace=True,
                inputText=text_prompt
            )

        resBody = response['completion']
        answer = ""
        for event in resBody:
                if 'chunk' in event:
                    chunk = event['chunk']['bytes'].decode('utf-8')
                    answer += chunk
                    print("Answer: ", answer)
        final_response += answer
        print("Final Response: ", final_response)   
            
        
        
        com_prompt = f''' 
                Add the final cdm json outputs of all these clauses into an array of json objects and print it: 
        '''
        f_com_prompt = com_prompt + final_response
        # Invoke Bedrock agent
        response = bedrock_client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                endSession=False,
                enableTrace=True,
                inputText=f_com_prompt
        )

        resBody = response['completion']
        answer = ""
        for event in resBody:
            if 'chunk' in event:
                chunk = event['chunk']['bytes'].decode('utf-8')
                answer += chunk
                print("Answer: ", answer)
        final_json_response = answer
        

        
        output_bucket_name = os.environ['OUTPUT_BUCKET']

        # Generate a unique key using the current timestamp
        timestamp = int(time.time())
        new_key = f'responses/response_{decoded_key_without_extension}_{timestamp}.txt'

        s3_client.put_object(Bucket=output_bucket_name, Key=new_key, Body=answer)

        # Return the response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'PDF processed successfully!',
                'agentResponse': final_json_response
            })
        }

    except ClientError as e:
        # Log the error
        print("ClientError occurred: ", e)
        # Return an error response
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
    except Exception as e:
        # Log any other error
        print("An error occurred: ", e)
        # Return an error response
        return {
            'statusCode': 500,
            'body': json.dumps({"error": str(e)})
        }
