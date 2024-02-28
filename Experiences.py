import requests
import json

# Your API endpoint
url = "https://api.backendless.com/CCC0AD14-8743-9138-FFEA-DB55C204F200/AFA2BCE4-1F87-409E-AC9A-8DD80E7EB119/data/Experiences"

# The actual experience JSON data you're getting from another API
# Replace this with your actual experience data
actual_experience_data = {
    "experienceId": "VP_1K2NF80H",
    "user": {
        "userId": "N/A",
        "name": "Ali Shaheen",
        "email": "ashaheen@workhub.ai",
        "phone": "N/A",
        "address": "N/A"
    },
    "channel": "web",
    "language":"de",
    "type": "post_transaction",
    "dateTime": "2024-02-27T00:00:00Z",
    "details": {
        "experienceType": "Mixed",
        "productsPurchased": [
        {
            "productName": "Standard-Visitenkarten",
            "productQuantity": 250,
            "productPrice": 36.99,
            "productUrl": "N/A",
            "productImageUrl": "N/A",
            "productType": "Office Supplies",
            "productFeedbackDimensions": [
            {
                "dimensionName": "Quality",
                "scale": ["Poor", "Fair", "Good", "Excellent"]
            },
            {
                "dimensionName": "Design",
                "scale": ["Poor", "Fair", "Good", "Excellent"]
            }
            ]
        },
        {
            "productName": "Visitenkartenetuis aus schwarzem Leder, vertikal",
            "productQuantity": 1,
            "productPrice": 15.44,
            "productUrl": "N/A",
            "productImageUrl": "N/A",
            "productType": "Accessories",
            "productFeedbackDimensions": [
            {
                "dimensionName": "Quality",
                "scale": ["Poor", "Fair", "Good", "Excellent"]
            },
            {
                "dimensionName": "Utility",
                "scale": ["Poor", "Fair", "Good", "Excellent"]
            }
            ]
        }
        ],
        "servicesReceived": []
    },
    "experienceFeedbackDimensions": [
        {
        "dimensionName": "Overall Satisfaction",
        "scale": ["Poor", "Fair", "Good", "Excellent"]
        }
    ],
    "transactionSubtotal": 52.43
}


# Your data to be posted, including orgid and experienceJSON
data_to_post = {
    "orgid": 1,
    "experienceJSON": json.dumps(actual_experience_data)  # Convert the experience data to a JSON string
}

# Headers to include with your request, such as Content-Type or Authentication
headers = {
    "Content-Type": "application/json",
    # Add any other necessary headers like authentication tokens
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
