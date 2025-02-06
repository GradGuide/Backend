Invoke-WebRequest -Uri "http://127.0.0.1:8000/users/15/" `
-Method PUT `
-Headers @{Authorization="Token 0e56077b5fdb6cd91338646e39d56c6a14148006"; "Content-Type"="application/json"} `
-Body '{"email": "example4000@gmail.com", "phone": "1234567890", "first_name": "Ahmed", "last_name": "Ali", "password": "newpassword123", "user_type": "researcher", "gender": "male", "address": "New Address"}' `
-ContentType "application/json"
