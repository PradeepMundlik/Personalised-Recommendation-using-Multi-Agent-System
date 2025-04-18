from agno.agent import Agent
from agno.models.ollama import Ollama
from user_item_db import UserItemDB

class UserAnalystAgent(Agent):
    def __init__(self, user_id):
        super().__init__(
            model = Ollama(id="llama3.2"),
            description = "An agent that analyzes user preferences and item attributes for personalized movie recommendations."
        )
        self.user_item_db = UserItemDB("movies_database.db")
        self.user_id = user_id
        self.user_profile = self.user_item_db.get_user_profile(self.user_id)

    def get_user_profile(self):
        """Retrieve the user profile from the info database."""
        return self.user_item_db.get_user_profile(self.user_id)

    def get_item_attributes(self, item_id):
        """Retrieve item attributes from the info database."""
        return self.user_item_db.get_item_attributes(item_id)
    
    def get_user_item_history(self):
        """Retrieve user item history from the info database."""
        return self.user_item_db.get_user_item_history(self.user_id)

    def analyze_user_preferences(self):
        """Analyze user preferences based on past interactions."""
        user_history = self.get_user_item_history()
        if not user_history:
            return "No history found for this user."
        
        past_item_ids = user_history['history_item_ids']
        past_item_ratings = user_history['history_ratings']


        
        # Count the number of ratings per genre
        genre_count = {}
        titles = {}

        time_count = 0

        for item_id, rating in zip(past_item_ids, past_item_ratings):
            item_attributes = self.get_item_attributes(item_id)
            if not item_attributes:
                continue
            
            # Update genre count
            for genre in item_attributes['genres']:
                genre_count[genre] = genre_count.get(genre, 0) + rating

            # Store title and rating
            titles[item_attributes['title']] = (rating, time_count)

            time_count = time_count + 1
        
        # get recently watched movies
        titles = dict(sorted(titles.items(), key=lambda item: item[1][1], reverse=True))
        recent_movies = list(titles.keys())[:5]

        # Get highest rated movies
        highest_rated_movies = sorted(titles.items(), key=lambda item: item[1][0], reverse=True)[:5]
        highest_rated_movies = dict(highest_rated_movies)
        highest_rated_movies = list(highest_rated_movies.keys())

        # Sort genres by count
        genre_count = dict(sorted(genre_count.items(), key=lambda item: item[1], reverse=True))

        # Create a summary of the analysis
        summary = {
            "user_profile": self.user_profile,
            "top_genres": genre_count,
            "highest_rated_movies_by_user": highest_rated_movies,
            "recent_movies": recent_movies
        }

        return summary