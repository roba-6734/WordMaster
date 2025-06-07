# Detailed API Planning

Now let's plan each API group in detail, considering what data each endpoint needs to handle and how they'll work together.

## Authentication API Group

The authentication system forms the foundation of your app's security. Users need to register, log in, and maintain secure sessions across both the web app and Chrome extension.

Registration Process: When users register, they provide an email and password. The system needs to validate the email format, ensure the email isn't already registered, hash the password securely, and create a user record in the database.

Login Process: Users provide credentials, the system validates them against stored data, and returns an authentication token that can be used for subsequent API calls.

Token Management: The system needs to generate secure tokens, validate tokens on each API call, and handle token expiration and refresh.

Google OAuth Integration: Since you want to support Google login, the system needs to handle OAuth flows and integrate with Google's authentication services.

## Word Management API Group

This group handles all operations related to a user's vocabulary collection. These APIs are among the most frequently used in your application.

Adding Words: Users can add words either manually through the web interface or automatically through the Chrome extension. The system needs to validate that the word doesn't already exist in the user's collection, fetch definition data from the dictionary service, and create appropriate learning progress records.

Retrieving Words: Users need to view their word collection with various filtering and sorting options. They might want to see all words, recently added words, words due for review, or search for specific words.

Updating Words: Users might want to add personal notes to words, mark words as favorites, or modify other word-specific settings.

Deleting Words: Users should be able to remove words from their collection, which also requires cleaning up associated learning progress data.

## Dictionary Integration API Group

These APIs handle communication with external dictionary services to fetch word definitions, examples, pronunciations, and related information.

Word Lookup: When a user adds a new word, the system queries external dictionary APIs to gather comprehensive information about the word.

Caching Strategy: To improve performance and reduce external API calls, the system should cache dictionary responses for commonly looked-up words.

Fallback Handling: If the primary dictionary service is unavailable or doesn't have information for a specific word, the system should have fallback strategies.

## Learning System API Group

This group implements the core learning functionality that makes your app effective for vocabulary acquisition.

Spaced Repetition Algorithm: The system calculates when each word should be reviewed next based on the user's performance history and the spaced repetition algorithm.

Progress Tracking: Each time a user reviews a word, the system updates the word's learning progress, including strength scores and next review dates.

Due Words Calculation: The system determines which words are due for review based on the current date and each word's next review date.

Performance Analytics: The system tracks overall learning statistics to show users their progress over time.

## Quiz Generation API Group

These APIs create engaging quiz experiences to help users practice their vocabulary.

Quiz Type Selection: The system supports multiple quiz formats and selects appropriate words for each quiz type based on the user's learning progress.

Question Generation: For each quiz type, the system generates questions using the user's vocabulary words and their definitions.

Answer Validation: The system checks user responses and provides immediate feedback on correctness.

Results Processing: After quiz completion, the system updates learning progress for each word based on the user's performance.

## Chrome Extension API Group

These APIs provide specific functionality needed by the Chrome extension to integrate seamlessly with the main application.

Word Addition from Extension: The extension needs a streamlined way to add words that users encounter while browsing.

Authentication Sync: The extension needs to authenticate users and maintain session state consistent with the web application.

Data Synchronization: The extension should sync with the main application to ensure users see consistent data across platforms.

## Data Models and Relationships

Understanding the data structure is crucial for designing effective APIs. Let's examine the key data models and how they relate to each other.

User Model

The user model stores essential information about each registered user. This includes authentication credentials, profile information, and user preferences that affect how the learning system behaves.

Key attributes include the user's email address (used for login), securely hashed password, display name, registration timestamp, last login time, and various preference settings like daily learning goals and notification preferences.

Word Model

The word model represents each vocabulary word in a user's collection. This model connects to external dictionary data while maintaining user-specific information.

Essential attributes include the word text itself, the user who owns this word entry, when the word was added, complete definition data fetched from dictionary services, user-added notes or comments, and any user-specific tags or categories.

Learning Progress Model

This model tracks how well a user is learning each word, implementing the spaced repetition algorithm's data requirements.

Critical attributes include references to both the user and the specific word, the current learning strength (a score indicating mastery level), the calculated next review date, a complete history of review sessions, and algorithm-specific data like easiness factors.

Quiz Result Model

This model stores information about completed quizzes, enabling progress tracking and analytics.

Important attributes include the user who took the quiz, when the quiz was completed, the quiz type and configuration, overall score and performance metrics, and detailed results for each word included in the quiz.

# API Endpoint Specifications

Now let's define the specific endpoints for each API group, including their URLs, HTTP methods, required parameters, and expected responses.

## Authentication Endpoints

User Registration

•
Endpoint: POST /api/auth/register

•
Purpose: Create a new user account

•
Required Data: email, password, display_name

•
Response: user_id, success message

•
Error Cases: email already exists, invalid email format, weak password

User Login

•
Endpoint: POST /api/auth/login

•
Purpose: Authenticate user and return access token

•
Required Data: email, password

•
Response: access_token, refresh_token, user_info

•
Error Cases: invalid credentials, account not found

Google OAuth Login

•
Endpoint: POST /api/auth/google

•
Purpose: Authenticate user via Google OAuth

•
Required Data: google_token

•
Response: access_token, refresh_token, user_info

•
Error Cases: invalid Google token, OAuth service unavailable

Token Refresh

•
Endpoint: POST /api/auth/refresh

•
Purpose: Get new access token using refresh token

•
Required Data: refresh_token

•
Response: new_access_token

•
Error Cases: invalid refresh token, token expired

User Logout

•
Endpoint: POST /api/auth/logout

•
Purpose: Invalidate user session

•
Required Data: access_token (in header)

•
Response: success confirmation

•
Error Cases: invalid token

## User Management Endpoints

Get User Profile

•
Endpoint: GET /api/user/profile

•
Purpose: Retrieve current user's profile information

•
Required Data: access_token (in header)

•
Response: user profile data

•
Error Cases: unauthorized access

Update User Profile

•
Endpoint: PUT /api/user/profile

•
Purpose: Update user profile information

•
Required Data: access_token, profile_data

•
Response: updated profile data

•
Error Cases: unauthorized access, invalid data format

Get User Settings

•
Endpoint: GET /api/user/settings

•
Purpose: Retrieve user's app settings and preferences

•
Required Data: access_token (in header)

•
Response: user settings object

•
Error Cases: unauthorized access

Update User Settings

•
Endpoint: PUT /api/user/settings

•
Purpose: Update user's app settings

•
Required Data: access_token, settings_data

•
Response: updated settings

•
Error Cases: unauthorized access, invalid settings

## Word Management Endpoints

Get User's Words

•
Endpoint: GET /api/words

•
Purpose: Retrieve user's vocabulary collection

•
Optional Parameters: limit, offset, search_term, sort_by

•
Required Data: access_token (in header)

•
Response: array of word objects with pagination info

•
Error Cases: unauthorized access

Add New Word

•
Endpoint: POST /api/words

•
Purpose: Add a new word to user's vocabulary

•
Required Data: access_token, word_text

•
Optional Data: user_notes, tags

•
Response: created word object with definitions

•
Error Cases: unauthorized access, word already exists, dictionary lookup failed

Get Specific Word

•
Endpoint: GET /api/words/{word_id}

•
Purpose: Retrieve detailed information about a specific word

•
Required Data: access_token (in header), word_id (in URL)

•
Response: complete word object with definitions and progress

•
Error Cases: unauthorized access, word not found, word doesn't belong to user

Update Word

•
Endpoint: PUT /api/words/{word_id}

•
Purpose: Update word information (notes, tags, etc.)

•
Required Data: access_token, word_id, update_data

•
Response: updated word object

•
Error Cases: unauthorized access, word not found, invalid update data

Delete Word

•
Endpoint: DELETE /api/words/{word_id}

•
Purpose: Remove word from user's vocabulary

•
Required Data: access_token (in header), word_id (in URL)

•
Response: deletion confirmation

•
Error Cases: unauthorized access, word not found

## Dictionary Integration Endpoints

Lookup Word Definition

•
Endpoint: GET /api/dictionary/lookup/{word}

•
Purpose: Get definition data for a word from external dictionary

•
Required Data: access_token (in header), word (in URL)

•
Response: comprehensive word definition data

•
Error Cases: unauthorized access, word not found in dictionary, external service unavailable

Get Cached Definitions

•
Endpoint: GET /api/dictionary/cache/{word}

•
Purpose: Retrieve previously cached definition data

•
Required Data: access_token (in header), word (in URL)

•
Response: cached definition data or cache miss indicator

•
Error Cases: unauthorized access, no cached data available

Learning System Endpoints

Get Due Words for Review

•
Endpoint: GET /api/learning/due-words

•
Purpose: Retrieve words that are due for review

•
Optional Parameters: limit, review_type

•
Required Data: access_token (in header)

•
Response: array of words due for review with progress data

•
Error Cases: unauthorized access

Submit Word Review

•
Endpoint: POST /api/learning/review

•
Purpose: Record user's performance on word review

•
Required Data: access_token, word_id, performance_score

•
Response: updated learning progress, next_review_date

•
Error Cases: unauthorized access, invalid word_id, invalid performance score

Get Learning Statistics

•
Endpoint: GET /api/learning/stats

•
Purpose: Retrieve user's overall learning progress and statistics

•
Optional Parameters: time_period, stat_type

•
Required Data: access_token (in header)

•
Response: comprehensive learning statistics

•
Error Cases: unauthorized access

Update Learning Settings

•
Endpoint: PUT /api/learning/settings

•
Purpose: Update spaced repetition algorithm settings

•
Required Data: access_token, settings_data

•
Response: updated learning settings

•
Error Cases: unauthorized access, invalid settings

## Quiz Generation Endpoints

Generate Quiz

•
Endpoint: POST /api/quiz/generate

•
Purpose: Create a new quiz based on user's vocabulary

•
Required Data: access_token, quiz_type

•
Optional Data: word_count, difficulty_level, specific_words

•
Response: generated quiz with questions

•
Error Cases: unauthorized access, insufficient words for quiz, invalid quiz type

Submit Quiz Results

•
Endpoint: POST /api/quiz/submit

•
Purpose: Process completed quiz and update learning progress

•
Required Data: access_token, quiz_id, user_answers

•
Response: quiz results, score, updated progress

•
Error Cases: unauthorized access, invalid quiz_id, malformed answers

Get Quiz History

•
Endpoint: GET /api/quiz/history

•
Purpose: Retrieve user's past quiz results

•
Optional Parameters: limit, offset, quiz_type, date_range

•
Required Data: access_token (in header)

•
Response: array of past quiz results

•
Error Cases: unauthorized access

## Chrome Extension Endpoints

Add Word from Extension

•
Endpoint: POST /api/extension/add-word

•
Purpose: Add word to vocabulary from Chrome extension

•
Required Data: access_token, word_text, source_url

•
Optional Data: context_sentence, page_title

•
Response: created word object

•
Error Cases: unauthorized access, word already exists

Sync Extension Data

•
Endpoint: GET /api/extension/sync

•
Purpose: Synchronize data between extension and web app

•
Optional Parameters: last_sync_timestamp

•
Required Data: access_token (in header)

•
Response: updated data since last sync

•
Error Cases: unauthorized access

Extension Authentication Check

•
Endpoint: GET /api/extension/auth-status

•
Purpose: Verify extension authentication status

•
Required Data: access_token (in header)

•
Response: authentication status and user info

•
Error Cases: unauthorized access, token expired

