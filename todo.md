- [] finish auth flow
- [] display list of available user on the /dashboard page
- [] link the /check-match endpoint to compare current user with any user.

need the flow to go authorize -> profile() 


# /auth
POST /api/auth/spotify-login      # Handle Spotify OAuth login
POST /api/auth/refresh-token      # Refresh access token
POST /api/auth/logout             # Logout user

# /users
GET /api/users/me                 # Get current user profile
PUT /api/users/me                 # Update user profile
PUT /api/users/me/social-links    # Update social media links
GET /api/users/{user_id}          # Get public user profile
GET /api/users/recommendations    # Get recommended users based on music taste


# /connections
POST /api/connections/request/{user_id}    # Send connection request
PUT /api/connections/{request_id}/accept   # Accept connection request
PUT /api/connections/{request_id}/reject   # Reject connection request
GET /api/connections/requests              # Get pending connection requests
GET /api/connections/                      # Get all connections
DELETE /api/connections/{connection_id}     # Remove connection


# /music
GET /api/music/top-artists              # Get user's top artists
GET /api/music/top-genres               # Get user's top genres
GET /api/music/recommendations          # Get personalized music recommendations
GET /api/music/mutual/{user_id}         # Get mutual music interests with another user

# /playlists
GET /api/playlists/mutual/{user_id}     # Get mutual playlists with another user
POST /api/playlists/create              # Create new playlist
PUT /api/playlists/{playlist_id}        # Update playlist
DELETE /api/playlists/{playlist_id}     # Delete playlist


# /mood-rooms
GET /api/mood-rooms/                    # List all mood rooms
GET /api/mood-rooms/{room_id}           # Get room details
POST /api/mood-rooms/join/{room_id}     # Join a mood room
POST /api/mood-rooms/leave/{room_id}    # Leave a mood room
GET /api/mood-rooms/{room_id}/users     # Get users in a room
POST /api/mood-rooms/{room_id}/track    # Update current track in room


# /ws
WS /ws/mood-rooms/{room_id}            # Real-time mood room updates
WS /ws/notifications                    # Real-time notifications


# Core Models
User
  - id: UUID
  - name: str
  - email: str
  - spotify_id: str
  - image_url: str
  - social_links: JSON
  - created_at: datetime

Connection
  - id: UUID
  - requester_id: UUID (FK User)
  - receiver_id: UUID (FK User)
  - status: Enum (pending, accepted, rejected)
  - created_at: datetime

MoodRoom
  - id: UUID
  - name: str
  - mood: str
  - description: str
  - current_track_id: str
  - created_at: datetime

MoodRoomUser
  - room_id: UUID (FK MoodRoom)
  - user_id: UUID (FK User)
  - joined_at: datetime

UserMusicProfile
  - user_id: UUID (FK User)
  - top_artists: JSON
  - top_genres: JSON
  - music_soul_level: int
  - last_updated: datetime
