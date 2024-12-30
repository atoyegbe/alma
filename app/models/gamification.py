from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    xp_points: int = Field(default=0)
    current_level: int = Field(default=1)

class User(UserBase, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    classes: List["UserClass"] = Relationship(back_populates="user")
    achievements: List["UserAchievement"] = Relationship(back_populates="user")
    quest_progress: List["UserQuestProgress"] = Relationship(back_populates="user")

class CharacterClass(SQLModel, table=True):
    class_id: Optional[int] = Field(default=None, primary_key=True)
    class_name: str = Field(unique=True, index=True)
    description: str
    
    # Relationships
    users: List["UserClass"] = Relationship(back_populates="character_class")

class UserClass(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.user_id", primary_key=True)
    class_id: int = Field(foreign_key="characterclass.class_id", primary_key=True)
    level: int = Field(default=1)
    xp_points: int = Field(default=0)
    
    # Relationships
    user: User = Relationship(back_populates="classes")
    character_class: CharacterClass = Relationship(back_populates="users")

class Quest(SQLModel, table=True):
    quest_id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    quest_type: str
    required_level: int = Field(default=1)
    xp_reward: int
    class_requirement: Optional[int] = Field(foreign_key="characterclass.class_id")
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: bool = Field(default=True)
    
    # Relationships
    user_progress: List["UserQuestProgress"] = Relationship(back_populates="quest")

class UserQuestProgress(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.user_id", primary_key=True)
    quest_id: int = Field(foreign_key="quest.quest_id", primary_key=True)
    progress_percentage: int = Field(default=0)
    status: str = Field(default="in_progress")
    completed_at: Optional[datetime]
    
    # Relationships
    user: User = Relationship(back_populates="quest_progress")
    quest: Quest = Relationship(back_populates="user_progress")

class Achievement(SQLModel, table=True):
    achievement_id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    achievement_type: str
    xp_reward: int
    badge_icon_url: Optional[str]
    
    # Relationships
    users: List["UserAchievement"] = Relationship(back_populates="achievement")

class UserAchievement(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.user_id", primary_key=True)
    achievement_id: int = Field(foreign_key="achievement.achievement_id", primary_key=True)
    earned_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user: User = Relationship(back_populates="achievements")
    achievement: Achievement = Relationship(back_populates="users")

class Genre(SQLModel, table=True):
    genre_id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    parent_genre_id: Optional[int] = Field(foreign_key="genre.genre_id")
    
    # Relationships
    user_progress: List["UserGenreProgress"] = Relationship(back_populates="genre")

class UserGenreProgress(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.user_id", primary_key=True)
    genre_id: int = Field(foreign_key="genre.genre_id", primary_key=True)
    songs_listened: int = Field(default=0)
    total_listen_time: int = Field(default=0)
    mastery_level: int = Field(default=0)
    
    # Relationships
    genre: Genre = Relationship(back_populates="user_progress")

class Playlist(SQLModel, table=True):
    playlist_id: Optional[int] = Field(default=None, primary_key=True)
    creator_id: int = Field(foreign_key="user.user_id")
    title: str
    description: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_collaborative: bool = Field(default=False)

class PlaylistBattle(SQLModel, table=True):
    battle_id: Optional[int] = Field(default=None, primary_key=True)
    playlist1_id: int = Field(foreign_key="playlist.playlist_id")
    playlist2_id: int = Field(foreign_key="playlist.playlist_id")
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime]
    winner_playlist_id: Optional[int] = Field(foreign_key="playlist.playlist_id")
    total_votes: int = Field(default=0)
    
    # Relationships
    votes: List["BattleVote"] = Relationship(back_populates="battle")

class BattleVote(SQLModel, table=True):
    battle_id: int = Field(foreign_key="playlistbattle.battle_id", primary_key=True)
    user_id: int = Field(foreign_key="user.user_id", primary_key=True)
    voted_playlist_id: int = Field(foreign_key="playlist.playlist_id")
    voted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    battle: PlaylistBattle = Relationship(back_populates="votes")

class Leaderboard(SQLModel, table=True):
    leaderboard_id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    start_date: datetime
    end_date: datetime
    
    # Relationships
    rankings: List["LeaderboardRanking"] = Relationship(back_populates="leaderboard")

class LeaderboardRanking(SQLModel, table=True):
    leaderboard_id: int = Field(foreign_key="leaderboard.leaderboard_id", primary_key=True)
    user_id: int = Field(foreign_key="user.user_id", primary_key=True)
    score: int
    rank: int
    
    # Relationships
    leaderboard: Leaderboard = Relationship(back_populates="rankings")

class GroupQuest(SQLModel, table=True):
    group_quest_id: Optional[int] = Field(default=None, primary_key=True)
    quest_id: int = Field(foreign_key="quest.quest_id")
    min_participants: int
    max_participants: int
    current_participants: int = Field(default=0)
    status: str = Field(default="forming")
    
    # Relationships
    participants: List["GroupQuestParticipant"] = Relationship(back_populates="group_quest")

class GroupQuestParticipant(SQLModel, table=True):
    group_quest_id: int = Field(foreign_key="groupquest.group_quest_id", primary_key=True)
    user_id: int = Field(foreign_key="user.user_id", primary_key=True)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    contribution_score: int = Field(default=0)
    
    # Relationships
    group_quest: GroupQuest = Relationship(back_populates="participants")