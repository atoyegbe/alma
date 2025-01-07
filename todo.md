# Alma Project TODOs

## Implementation Tasks

### Authentication
- [ ] Implement proper logout functionality
- [ ] Add Apple Music login capability

### Real-time Features
- [ ] Consider using Redis for real-time updates in handlers
- [ ] Implement proper WebSocket connection handling

### Mood Rooms
- [ ] Implement logic to add users to room participants
- [ ] Implement logic to remove users from room participants
- [ ] Implement logic to get room participants

### Playlists
- [ ] Add error handling for playlist operations
- [ ] Implement limit on tracks that can be added to a playlist
- [ ] Implement self-generating playlists based on user taste

### Connections
- [ ] Optimize compatibility calculation logic

## Unit Tests Needed

### Authentication Endpoints
- [ ] GET /callback
- [ ] GET /refresh-token
- [ ] GET /logout

### User Endpoints
- [ ] GET /me
- [ ] GET /me/music-profile
- [ ] PUT /me
- [ ] PUT /me/social-links
- [ ] GET /{user_id}
- [ ] GET /{user_id}/music-profile
- [ ] GET /recommendations

### Connections Endpoints
- [x] GET /connections
- [x] POST /request/{target_user_id}
- [x] POST /accept/{connection_id}
- [x] POST /reject/{connection_id}
- [x] DELETE /{connection_id}

### Mood Rooms Endpoints
- [ ] GET /
- [ ] GET /{room_id}
- [ ] POST /join/{room_id}
- [ ] POST /leave/{room_id}
- [ ] GET /{room_id}/users
- [ ] POST /{room_id}/track

### Music Endpoints
- [ ] GET /top-artists
- [ ] GET /top-genres
- [ ] GET /recommendations
- [ ] GET /mutual/{user_id}
- [ ] POST /spotify/sync
- [ ] GET /profile/metrics

### Playlists Endpoints
- [ ] GET /
- [ ] GET /mutual/{user_id}
- [ ] POST /
- [ ] PUT /{playlist_id}
- [ ] DELETE /{playlist_id}
- [ ] GET /{playlist_id}/tracks

### Recommendation Endpoints
- [ ] GET /recommendations/users
- [ ] GET /recommendations/compatibility/{user_id}

### WebSocket Endpoints
- [ ] WS /mood-rooms/{room_id}
- [ ] WS /notifications

## Core Components Testing

### Database Layer
- [ ] Test database connection and session management
- [ ] Test model relationships and constraints
- [ ] Test database migrations

### Authentication (auth/)
- [ ] Test Spotify OAuth flow
- [ ] Test token refresh mechanism
- [ ] Test session management
- [ ] Test user logout process

### User Management (users/)
- [ ] Test user profile CRUD operations
- [ ] Test music profile synchronization
- [ ] Test social links management
- [ ] Test user recommendations

### Music Integration (music/)
- [ ] Test Spotify API integration
- [ ] Test top artists/genres calculation
- [ ] Test music recommendations algorithm
- [ ] Test mutual music interests calculation
- [ ] Test music profile metrics generation

### Connections System (connections/)
- [ ] Test connection request flow
- [ ] Test connection acceptance/rejection
- [ ] Test connection removal
- [ ] Test connection status management

### Mood Rooms (moodrooms/)
- [ ] Test room creation and management
- [ ] Test participant handling
- [ ] Test real-time updates
- [ ] Test track management within rooms

### Playlists (playlists/)
- [ ] Test playlist CRUD operations
- [ ] Test track management
- [ ] Test playlist sharing
- [ ] Test mutual playlist discovery

### Real-time Features (realtime/)
- [ ] Test WebSocket connections
- [ ] Test real-time notifications
- [ ] Test room state synchronization
- [ ] Test connection state updates

### Recommendation Engine (recommendation/)
- [ ] Test user recommendation algorithm
- [ ] Test compatibility scoring
- [ ] Test music taste analysis
- [ ] Test recommendation filtering

### Helpers and Utilities
- [ ] Test helper functions in helpers/
- [ ] Test constant values and configurations
- [ ] Test Apple Music integration utilities

## Testing Priorities
1. [ ] Core authentication and user management
2. [ ] Database operations and data integrity
3. [ ] Real-time communication features
4. [ ] Music integration and synchronization
5. [ ] Social features (connections, rooms)
6. [ ] Recommendation systems

## Testing Types Needed
- [ ] Unit tests for individual components
- [ ] Integration tests for API endpoints
- [ ] End-to-end tests for critical user flows
- [ ] Performance tests for real-time features
- [ ] Security tests for authentication