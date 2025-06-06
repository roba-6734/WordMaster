import firebase_admin
from firebase_admin import firestore, credentials
 

credential = credentials.Certificate('./../config/wordmaster-42b21-firebase-adminsdk-fbsvc-9cc735e8a9.json')
app = firebase_admin.initialize_app(credential=credential)

db = firestore.client()


doc_ref = db.collection('Users').document('rabera')
doc_ref.set({"first":"RObera", "last":"Abera"}) 