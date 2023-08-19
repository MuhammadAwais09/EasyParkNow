import pyrebase

#firebase start
config = {
    "apiKey": "AIzaSyD565dx672kuJqDlzO1Lsb1Q9ClJPxbBYc",
    "authDomain": "smart-parking-system-edcde.firebaseapp.com",
    "databaseURL": "https://smart-parking-system-edcde-default-rtdb.firebaseio.com/",
    "projectId": "smart-parking-system-edcde",
    "storageBucket": "smart-parking-system-edcde.appspot.com",
    "messagingSenderId": "1053910320425",
    "appId": "1:1053910320425:web:c4d6735ec1764bcea56338",
    "measurementId": "MRRBHF1GGT"
}

firebase  = pyrebase.initialize_app(config)
db = firebase.database()
db.child("names").push({"name": "awais"})




#firebase end


