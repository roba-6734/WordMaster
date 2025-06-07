import firebase_admin
from firebase_admin import firestore, credentials
from httplib2 import Credentials

credential: Credentials = credentials.Certificate(
    "./../config/wordmaster-42b21-firebase-adminsdk-fbsvc-9cc735e8a9.json"
)
app = firebase_admin.initialize_app(credential=credential)

db = firestore.client()


