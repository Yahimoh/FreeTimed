# FreeTimed

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd FreeTimed
   ```

2. Create a virtual environment:
   ```
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   ```
   source venv/bin/activate
   ```
   Note: Use `source` — running `venv/bin/activate` directly will not work.

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set the secret key environment variable:
   ```
   export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
   ```

6. Run the application:
   ```
   flask run
   ```

7. Open http://127.0.0.1:5000 in your browser.

## Planned Features ##
* User can submit reviews on recently seen or listened stuff like:
  * Music
  * Movies
  * Series
  * Videogames
* User can see other followed users reviews
* Other people can review same stuff and see stats for it
* User can make an account and log in
* User can follow other people and be followed
* User can see newly created profiles
  
## Current features
- **Review Submission:**  
  Users can submit reviews for recently seen or listened items such as:
  - Music
  - Movies
  - Series
  - Videogames

- **User Profiles & Account Management:**  
  Users can create an account, log in, and log out. Each user has a profile page displaying their reviews.

- **Review Management:**  
  Logged-in users can edit or delete their own reviews.

- **Follow System:**  
  Users can follow other users and see reviews posted by those they follow.

- **Seing new profiles:**  
  Users can view newly created profiles.
  Users can see other profiles review stats.
