import requests

response  =requests.post(
    "http://localhost:5000/home/tasks/add_Tasks",
    json={'description': 'Buy groceries'}
)
print(response.json())