from datetime import timedelta
# перписать в текстовый вместо жтого блять
invited_users = set()
last_photo_requests = {}
PHOTO_COOLDOWN = timedelta(minutes=10)
user_joins = {}