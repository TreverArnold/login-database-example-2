import json
from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone
from flask_jwt_extended import create_access_token,get_jwt,get_jwt_identity, \
                               unset_jwt_cookies, jwt_required, JWTManager


api = Flask(__name__) # Initilizing a flask web app names api

api.config["JWT_SECRET_KEY"] = "SuperSecret" # SeTs key to encode and decode tokens
api.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1) # Sets the expiration time for tokens for 1 hour
jwt = JWTManager(api) # creates instance of JWTManager directly for this flak application and assigns it to the variable jwt

@api.after_request # after any request run code below
def refresh_expiring_jwts(response): # defines function to be run after a request
    try: # attempts code below
        exp_timestamp = get_jwt()["exp"] # sets exp_timestamp to the expiration timestamp of the access token
        now = datetime.now(timezone.utc) # sets variable now to the current time
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30)) # sets target_timestamp to 30 minutes from current time
        if target_timestamp > exp_timestamp: #if the target is futher in the future than the current expiration, run the code below
            access_token = create_access_token(identity=get_jwt_identity()) # makes a new access token with the same user information
            data = response.get_json() # sets data to the json response
            if type(data) is dict: # checks to make sure the json data was retreived correctly by checking data type
                data["access_token"] = access_token  # updates the key access_token to have the value of the new token just created
                response.data = json.dumps(data) # turns the data dictonary back into json format and puts it into response
        return response # returns response after making the previous changes
    except (RuntimeError, KeyError): # if and error is encountered and it is either runtime or key, execute following code:
        return response # returns response as it was, as a runtime, or key error happened

@api.route('/token', methods=["POST"]) #sets up a new route or /token that only accepts posts
def create_token(): #defines function to be called when /token is posted to
    email = request.json.get("email", None) # checks the json which was posted to this endpoint for an email key,
    #if there is one it sets email to its value otherwise it sets email to None
    password = request.json.get("password", None) # same thig but for password
    if email != "test" or password != "test": # checks email and password against preset defaults
        return {"msg": "Wrong email or password"}, 401 # if email or password are wrong, returns a 401 error

    access_token = create_access_token(identity=email) # creates an access token based off of the users email
    response = {"access_token":access_token} # assigns the token to the access_token key in the response dict
    return response #returns response

@api.route("/logout", methods=["POST"]) # sets /logout endpoint which accepts only posts
def logout(): # func definition for logout
    response = jsonify({"msg": "logout successful"}) # adds msg key of logout successful to response object
    unset_jwt_cookies(response) # removes jwt cookies from resopnse
    return response # returns response

@api.route('/profile') # new route of /profile, is not set up to handle any specific methods
@jwt_required() # requires a valid jwt to execute the code below
def my_profile(): # function definition
    response_body = {
        "name": "Trever",
        "about" :"Hello! I'm a full stack developer that tolerates python and javascript"
    } # json response body difinition

    return response_body # returns said response body