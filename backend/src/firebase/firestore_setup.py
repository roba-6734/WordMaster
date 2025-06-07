from typing import Optional
from firebase_setup import db

"""
We initialize the collections here

"""

users_ref = db.collection('users')
words_ref = db.collection('words')
progress_ref = db.collection('progress')
quiz_result_ref = db.collection('quizzes')
user_session_ref = db.collection('sessions')


"""
users/
  {userId}/  # Use Firebase Auth UID as document ID
    email: "user@example.com"
    displayName: "John Doe"
    createdAt: ""
    lastLoginAt: ""
    profilePicture: "https://..." (optional )
    settings: {
      dailyGoal: 10,
      notificationsEnabled: true,
      preferredQuizTypes: ["mcq", "matching"],
      timezone: "America/New_York"
    }
    stats: {
      totalWordsAdded: 0,
      totalQuizzesTaken: 0,
      currentStreak: 0,
      longestStreak: 0
    }

"""
users_ref.add({
    "email":"ro@gmail.com",
    "displayName": "RoAb",
    "createdAt":"",
    "lastLoginAt":"",
    "profilePicture":"",
    "stats":{
        "totalWordAdded":0,
        "totalQuizzesTaken":0,
        "CurrentStreak":0,
        "LongestStreak":0
    }
})

"""
words/
  {auto-generated-id}/
    userId: "reference-to-user-id"
    word: "vocabulary"
    addedAt: ""
    source: "manual" | "extension"  # How word was added
    sourceUrl: "https://..." (optional, from extension )
    definitions: [
      {
        partOfSpeech: "noun",
        definition: "The body of words used in a particular language",
        example: "Reading helps expand your vocabulary"
      },
      {
        partOfSpeech: "noun", 
        definition: "A list of words with explanations",
        example: "The textbook includes a vocabulary at the end"
      }
    ]
    phonetics: [
      {
        text: "/vəˈkæbjʊˌlɛri/",
        audio: "https://audio-url.com/vocab.mp3" (optional )
      }
    ]
    synonyms: ["lexicon", "terminology", "words"]
    antonyms: []
    userNotes: "Important for language learning" (optional)
    tags: ["education", "language"] (optional)
    isFavorite: false
    difficultyLevel: "intermediate" (optional)

"""

words_ref.add({
    "userId": "",
    "word":"Nonchalant",
    "addedAt":"",
    "definitions":[{
        'partOfSpeech':"adjectives",
        "definition":"Someone cold",
        "Example": "He is hella nonchalant"
    }],
    "phonetics":[
        {
            "text":"",
            "audio":""

        }
    ],
    "synonyms":["Cold"],
    "antonyms":[],
    "difficultyLevel":"easy",
    "isFav":False

})

"""
progress/
  {auto-generated-id}/
    userId: "reference-to-user-id"
    wordId: "reference-to-word-id"
    
    # Spaced Repetition Data
    strength: 0.0  # 0.0 to 1.0 (mastery level)
    easinessFactor: 2.5  # SM-2 algorithm factor
    interval: 1  # Days until next review
    nextReviewAt: ""
    
    # Review History
    reviewCount: 0
    correctCount: 0
    incorrectCount: 0
    lastReviewedAt: "" (optional)
    
    reviewHistory: [
      {
        reviewedAt: "",
        performance: 4,  # 0-5 scale (0=complete blackout, 5=perfect)
        responseTime: 3.2,  # seconds taken to answer
        reviewType: "flashcard" | "quiz"
      }
    ]
    
    # Metadata
    createdAt: ""
    updatedAt: ""

"""

progress_ref.add({
    "userId":"",
    "wordId":"",
    "strength":0,
    "easinessFactor":"",
    "interval":1,
    "nextReviewAt":"",
    "reviewCount":0,
    "correctCount":0,
    "incorrectCount":0,
    "lastReviewedAt":"",
    "createdAt":"",
    "updatedAt":"",
})

"""
quiz_results/
  {id}/
    userId: "user-id"
    score: 8
    totalQuestions: 10
    completedAt: ""
    wordIds: ["word1", "word2", "word3"]  # Just track which words

"""

quiz_result_ref.add({
    "userId":"",
    "score":10,
    "totalQuestions":10,
    "wordIds":[""],
    "completedAt":""
})

"""
user_sessions/
  {auto-generated-id}/
    userId: "reference-to-user-id"
    deviceType: "web" | "extension"
    deviceInfo: "Chrome Extension v1.0"
    lastActiveAt: ""
    isActive: true
    createdAt: ""

"""

user_session_ref.add({
    "userId":"",
    "userId" :"",
    "deviceType": "",
    "deviceInfo":"",
    "lastActiveAt":"",
    "isActive":"",
    "createdAt":"",
    
})