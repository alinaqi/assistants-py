from fastapi import FastAPI, File, UploadFile, HTTPException, Form
import openai
import uuid
import asyncio
import base64
from concurrent.futures import ThreadPoolExecutor
from fastapi.middleware.cors import CORSMiddleware
import json
import requests


app = FastAPI()

# List of allowed origins (use ["*"] for development)
origins = [
    "http://localhost:3000",  # Adjust the port if your React app runs on a different port
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

openai.api_key = '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'  # In production move it to enviornment 

# our test assistant for csv data
OUR_TEST_ASSISTANT = "asst_ovs3qFQR4JtWNtGFRylkkst7" #"asst_HEnJEXsBxBdHa73BP4lrhCOp"

#our test assistant for email2experiencejson
OUR_EXPERIENCE_ASSISTANT = "asst_ovs3qFQR4JtWNtGFRylkkst7"

def post_experience_data(actual_experience_data):
    # Your API endpoint
    url = "https://api.backendless.com/CCC0AD14-8743-9138-FFEA-DB55C204F200/AFA2BCE4-1F87-409E-AC9A-8DD80E7EB119/data/Experiences"
    
    # Your data to be posted, including orgid and experienceJSON
    data_to_post = {
        "orgid": 1,
        "experienceJSON": json.dumps(actual_experience_data)  # Convert the experience data to a JSON string
    }

    # Headers to include with your request, such as Content-Type or Authentication
    headers = {
        "Content-Type": "application/json",
        # Add any other necessary headers like authentication tokens here
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data_to_post))

    # Check the response
    if response.status_code == 200 or response.status_code == 201:
        print("Data posted successfully!")
        print(response.json())  # Prints the response from the server
    else:
        print(f"Failed to post data. Status code: {response.status_code}")
        print(response.text)  # Prints the error message from the server

#API to create an assistant with a name, description, model, tools and file uploads
@app.post("/create-assistant/")
async def create_assistant(name: str, description: str, model: str, tools: list, file: UploadFile = File(...)):
    try:
        #read the file contents first
        file_content = await file.read()

        # get the uploadedFile and use openai.files.create to store the file with the purpose of "assistants"
        file = openai.files.create(file=file_content, purpose="assistants")  

        # Create a new assistant
        assistant = openai.beta.assistants.create(
            name=name,
            description=description,
            model=model,
            tools=tools
            )
        
        return {"assistant_id": assistant.id} 
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

#API to upload a file, pass a user query and get thread id and messages from assistant. Assistant id is optional 
# if assistant id is not passed we will use OUR_TEST_ASSISTANT
@app.post("/upload-file/")
async def upload_file(query: str = Form(...), uploadedFile: UploadFile = File(...), assistant_id: str = OUR_TEST_ASSISTANT):
    try:
        #read the file contents first
        file_content = await uploadedFile.read()

        # get the uploadedFile and use openai.files.create to store the file with the purpose of "assistants"
        file = openai.files.create(file=file_content, purpose="assistants")  

        # STEP1: Create a new assistant
        # in our case we will use an existing assistent.
        my_assistant = openai.beta.assistants.retrieve(assistant_id)        

        # STEP 2: Create a new thread (your implementation might differ)
        print("user query: ", query)
        thread = openai.beta.threads.create(
            messages=[
                {
                "role": "user",
                "content": query,
                "file_ids": [file.id]
                }
            ]
            )
        
        #STEP 3: Add query to a thread
        message = openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=query
        )

        # STEP 4: Start a new run with the Assistant & Thread id
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=my_assistant.id
            )

        run_in_progress = True

        #initialize run
        response = ''

        # STEP 5: Poll the run until it's complete
        while run_in_progress:
            print("Processing... thread id: ", thread.id, " run id: ", run.id)

            run = openai.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            


            if run.status == "completed":

                #display the completion status
                print("run is complete!")

                run_in_progress = False
                break


        #STEP 6: retrieve complete message against the thread id
        thread_messages = openai.beta.threads.messages.list(thread.id)

        #print the thread
        print("thread: ", thread_messages.data)
        
        return {"thread_id": thread.id, "thread_messages": thread_messages.data, "assistant_id": my_assistant.id} 
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#API to add a message to the query and continue discission. 
#Pass the thread id, query and assistant id. 
@app.post("/add-query")
async def add_query(thread_id: str, query: str, assistant_id: str):

    try:

        # STEP1: Create a new assistant
        # in our case we will use an existing assistent.
        my_assistant = openai.beta.assistants.retrieve(assistant_id) 
        

        # STEP 3: Directly going to step 3 as we already have a thread id
        print("user query: ", query)

        thread_message = openai.beta.threads.messages.create(
            thread_id,
            role="user",
            content=query,
        )

        # STEP 4: Start a new run with the Assistant & Thread id
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=my_assistant.id
        )

        run_in_progress = True


        # STEP 5: Poll the run until it's complete
        while run_in_progress:
            print("Processing... thread id: ", thread_id, " run id: ", run.id)

            run = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            

            if run.status == "completed":

                #display the completion status
                print("run is complete!")

                run_in_progress = False
                break


        #STEP 6: retrieve complete message against the thread id
        thread_messages = openai.beta.threads.messages.list(thread_id)

        #print the thread
        print("thread: ", thread_messages.data)
        
        return {"thread_messages": thread_messages.data} 
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


#get content from an image file generated by openai by passing file id
@app.get("/get-image-file/{file_id}")
async def get_image_file(file_id: str):
    try:

        image_file_id = file_id
        # Assuming `openai.files.content` properly retrieves the file content as bytes
        image_content =  openai.files.content(image_file_id)  # This is a placeholder; you'll need the correct method

            
        file_name = f"{image_file_id}.png"
        file_path = f"workhub-assistants/public/{file_name}"

        # Ensure the directory exists or handle directory creation here

        with open(file_path, "wb") as f:
            f.write(image_content.content)

        return {"file_name": file_name}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))