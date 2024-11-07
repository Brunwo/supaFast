export $(grep -v '^#' .env | xargs)

http GET http://127.0.0.1:8000/public

http GET http://127.0.0.1:8000/protected 

http GET http://127.0.0.1:8000/not_anonymous "Authorization: Bearer $TEST_TOKEN"

http GET http://127.0.0.1:8000/protected "Authorization: Bearer $TEST_TOKEN"

#not working ?
# dotenv -f .env run http GET http://127.0.0.1:8000/protected "Authorization: Bearer $TEST_TOKEN"
