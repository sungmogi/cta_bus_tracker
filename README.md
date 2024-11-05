# cta_bus_tracker

## Architecture and Design
The web service is built using AWS Lambda functions, API Gateway, and an RDS (Relational Database Service) for data storage. Lambda functions handle the core logic for each feature. API Gateway triggers the Lambda functions via HTTP endpoints. Lastly, client side is used for users to interact with the server side using python. 

## Database Schema
We utilize a database named “bustracker” stored in AWS RDS. We have two tables: “users” and “fav_routes”. The "users" table tracks registered users, storing userid, username, and password hash generated with the bcrypt library, where the userid is the primary key. 

<img width="684" alt="Screen Shot 2024-11-05 at 10 34 52 AM" src="https://github.com/user-attachments/assets/f80ba3bd-a5de-4bc8-8c91-673b7ce8fcc9">

The "fav_routes" table stores route id, userid, route numbers, and stop IDs. The column “routeid” is the primary key that identifies each row in this table and “userid” is a foreign key that references the users table. 

<img width="416" alt="Screen Shot 2024-11-05 at 10 35 12 AM" src="https://github.com/user-attachments/assets/b34f8b1f-ff1e-4937-b332-e9a913e89da5">

## Lambda functions & API
### create_user
  The Lambda function create_user is a function for user registration that uses the pymysql and bcrypt Lambda layers. It is triggered by a POST request to the /user endpoint. It takes a username and password, hashes the password using bcrypt library and inserts a row consisting of the username and the hashed password into the "users" table.
The Lambda function login uses the pymysql, bcrypt, and pyjwt layers. It is triggered by a POST request to the /login endpoint. This function takes a username and password, retrieves the stored password hash for the user, and compares the provided password, which is also hashed, with the stored hash using bcrypt. Upon successful authentication, we first create a payload that consists of the user’s id, username, and the time of expiration for JWT token generation. For the purpose of our project, we set the time of expiration to be 5 minutes after the token generation. We then generate the JWT token by encrypting the payload using a secret key.
### add_fav_route and view_fav_routes
 The Lambda function auth is a function for user authentication called by two other Lambda functions add_fav_route and view_fav_routes. It is triggered by a POST request to the /auth endpoint. auth takes in a JWT token in the request body and uses pyjwt to decrypt the token. It then determines if the stateless token is valid by comparing the expiration time in the payload and the current time. If the token is valid, we return a success response with the userid and the username. 
### view_routes
  The view_routes Lambda function uses the requests layer. It is triggered by a GET request to the /routes endpoint. This function makes a GET request to the /getroutes endpoint in the CTA Bus Tracker API to fetch all bus routes and returns a JSON object that contains route numbers and names. 
### view_stops
  The view_stops Lambda function, which also uses the requests layer, is triggered by a GET request to the /stops endpoint. It accepts a route number and direction, calls the CTA Bus Tracker API endpoint to fetch stops for the specified route and direction, and returns a JSON object containing stop IDs and names. The services view_routes and view_stops are intended to accommodate the user as they can look up the route number and stop id that they want to add as their favorite route. 
### add_fav_route
  The add_fav_route Lambda function uses the pymysql and requests layers. It is triggered by a POST request to the /fav-routes endpoint and accepts the JWT token in the request header and the route number and stop id from the body. It first uses the requests library to make a POST request to auth. If the request returns an unsuccessful response, we throw an error. Upon successful authentication, we insert a new row consisting of the authenticated user’s id, favorite route number, stop id into the “fav_routes” table.
### view_fav_routes
  The view_fav_routes Lambda function uses the pymysql and requests layers. It is triggered by a GET request to the /fav-routes endpoint. This function accepts the JWT token in the request header and validates the token by making a POST request to auth in the same way as in the add_fav_route function. Upon successful authentication, the function uses the pymysql library to retrieve all the rows from the “fav_routes” table where the userid column matches the authenticated user. Then, we respond with the JSON object containing favorite route numbers and stop ids. 
### get_pred
  The get_pred Lambda function uses the requests layer. It is triggered by a GET request to the /preds endpoint. This function accepts a route number and stop id in the body and calls the /getpredictions endpoint in the CTA Bus Tracker API to get the ETA of different vehicles for the specified bus route at the specified stop. For each vehicle, it subtracts the current time from the ETA to calculate the number of minutes that the user would have to wait. If there is no active service scheduled for the bus route at the bus stop, this function will return with an error message.

## Client-side workflow
  From the client side, the user can interact with the server-side with 6 commands: register, login, view routes, view stops, add favorite route, and view ETA. 

 When the user selects the register option, they are asked to input the username and password. This will then make a POST request to the /user endpoint with the username and password in the body. 
 
 When the user selects the login option, they are asked to input the username and password. This will then make a POST request to the /login endpoint with the username and password in the body. The Lambda function will return a token upon successful login, and the client-side login function will return the token so that other client-side functions that require authentication can use it. 

When the user selects the view routes option, a GET request to the /routes endpoint will be made. The endpoint will respond with a JSON object of the route number and name of all the bus routes, which will be formatted and printed for the user.

When the user selects the view stops option, they are asked to input the bus route number and direction that they want to view the stops for. This will then make a GET request to the /stops endpoint which will either throw an error if there is no such route in such direction or respond with a JSON object of the stop id and name of all the corresponding stops. This will be formatted and printed for the user.

When the user selects the add favorite route option, assuming that they are logged in, they are asked to input the bus route and stop that they want to add as their favorite route to track. If the client is storing a token, this will then make a POST request to the /fav-routes endpoint with the token in the header and the bus route and stop in the body. If the request is successful, the user will receive the message that the favorite route has been added successfully.
	
 When the user selects the view ETA option, assuming that they are logged in, this will first make a GET request to the /fav-routes endpoint with the token in the header. If the request is successful, the user will be asked to select from the fetched favorite routes. After the user inputs a number that corresponds to the favorite route, another GET request will be made to the /preds endpoint with the route number and stop id in the body. If the request is successful, the response will be formatted and printed.

