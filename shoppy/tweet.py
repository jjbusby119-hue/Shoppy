import json
from requests_oauthlib import OAuth1Session


class Tweet:
    _instance = None

    CONSUMER_KEY = 'your_key'
    CONSUMER_SECRET = 'your_secret'


    # Creates a new instance of Tweet if one doesn't exist
    def __new__(cls):
        if cls._instance is None:
            print('Creating the Tweet instance...')
            cls._instance = super(Tweet, cls).__new__(cls)
            cls._instance.oauth = None
            cls._instance.authenticate()
        return cls._instance


    # This method handles the login process with Twitter
    def authenticate(self):
        request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
        oauth = OAuth1Session(self.CONSUMER_KEY, client_secret=self.CONSUMER_SECRET)

        # Get temporary login tokens from Twitter
        try:
            fetch_response = oauth.fetch_request_token(request_token_url)
        except ValueError:
            print("Invalid consumer key or secret.")
            return

        # Store the tokens from the response
        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print("Got request token.")

        # Build the link where the user must go to allow access
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth.authorization_url(base_authorization_url)
        print("Please go here and authorize: ", authorization_url)

        # Ask the user to enter the code they get from Twitter
        verifier = input("Enter the PIN from Twitter: ")

        # Ask Twitter for the final access token
        oauth = OAuth1Session(
            self.CONSUMER_KEY,
            client_secret=self.CONSUMER_SECRET,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=verifier,
        )

        # Ask Twitter to give final permission
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth_tokens = oauth.fetch_access_token(access_token_url)

        # Save the tokens
        access_token = oauth_tokens["oauth_token"]
        access_token_secret = oauth_tokens["oauth_token_secret"]

        self.oauth = OAuth1Session(
            self.CONSUMER_KEY,
            client_secret=self.CONSUMER_SECRET,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret,
        )

        print("Authentication complete.")


    # This function sends a tweet
    def make_tweet(self, tweet_text):
        from .models import Store, Product
        if not self.oauth:
            raise ValueError('Authentication failed!')

        # Try to post the tweet
        response = self.oauth.post(
            "https://api.twitter.com/2/tweets",
            json={"text": tweet_text},
        )

        # If tweet fails show error
        if response.status_code != 201:
            raise Exception(
                f"Tweet failed: {response.status_code} — {response.text}"
            )

        # Tweet went through successfully
        print("Tweet posted successfully!")
        json_response = response.json()  # Get details about the tweet
        print(json.dumps(json_response, indent=4, sort_keys=True))

        if tweet_text.startswith("A new store just arrived at Shoppy!"):
            # If the tweet is about a new store
            store_id = int(tweet_text.split(" ")[-1])
            store = Store.objects.get(pk=store_id)
            if store.logo:
                media_url = store.logo.url
                media_id = self._get_media_id(media_url)
                self._add_media_to_tweet(media_id)

        elif tweet_text.startswith("A new product just arrived at Shoppy!"):
            # If the tweet is about a new product         
            product_id = int(tweet_text.split(" ")[-1])
            product = Product.objects.get(pk=product_id)
            if product.image:
                media_url = product.image.url
                media_id = self._get_media_id(media_url)
                self._add_media_to_tweet(media_id)

            print("Tweet posted successfully!")
            json_response = response.json()
            print(json.dumps(json_response, indent=4, sort_keys=True))
