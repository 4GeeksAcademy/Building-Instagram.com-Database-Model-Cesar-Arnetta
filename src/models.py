from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import List
from sqlalchemy import String, Boolean, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

post_type = Enum('reel', 'post', 'story', name="post_type_enum")


class Follower(db.Model):
    __tablename__ = "followers"
    follower_id: Mapped[int] = mapped_column(primary_key=True)
    user_from_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id'), nullable=False)
    user_to_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id'), nullable=False)
    # 1
    following_user: Mapped["User"] = relationship(
        # 2
        back_populates="following",
        foreign_keys=[user_from_id]
        # 3
    )
    followed_user: Mapped["User"] = relationship(
        back_populates="followers",
        foreign_keys=[user_to_id]
    )


class User(db.Model):
    __tablename__ = "users"
    user_id: Mapped[int] = mapped_column(primary_key=True)
    user_name: Mapped[str] = mapped_column(
        String(250), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    following: Mapped[List[Follower]] = relationship(
        foreign_keys=[Follower.user_from_id],
        back_populates="following_user",
        # 4
        overlaps="following_user",
        viewonly=True
    )
    followers: Mapped[List[Follower]] = relationship(
        foreign_keys=[Follower.user_to_id],
        back_populates="follower_user",
        overlaps="follower_user",
        # 5
        viewonly=True
    )


class Post(db.Model):
    __tablename__ = "posts"
    post_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    update_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now())


class Media(db.Model):
    __tablename__ = "medias"
    media_id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(post_type, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    post_id: Mapped[int] = mapped_column(
        ForeignKey('posts.post_id'), nullable=False)


class Comment(db.Model):
    __tablename__ = "comments"
    comment_id: Mapped[int] = mapped_column(primary_key=True)
    comment_text: Mapped[str] = mapped_column(String(250), nullable=False)
    author_id: Mapped[int] = mapped_column(
        ForeignKey('users.user_id'), nullable=False)
    post_id: Mapped[int] = mapped_column(
        ForeignKey('posts.post_id'), nullable=False)

#  Observations

# Why I don't do an intermediate table and use de class Follower?,
# beacause it's cleaner use a class with realtionships and we can scale that with more information/columns
# For excample: We can add column with the date has been followed that user, we can indicate the followed status (Enum) and other usefull information.

# I indicate observations with numbers to make the code easier to read and understand.

# 1 Notice that we use the same user_id for two keys, "from" is for who follow, and "to" is for who has been followed.
#      Now is mandatory to stablish a relationship between follower and user_id, and we created a descriptional relationship
#      case name of these associations.

# 2 We do a relation, in this case directly for the class User, whitout using the List typing, because the nature of the relationship
#         # which is in one directtion: id who following to id has been followed. If the relation it's one to many, we must use the typing List
#         # as we indicate above in the class User. In this case (Follower) we repsent the realtionships: one to one,
#         # beacuase every row has 1 id who follow and 1 id has been followed.

# 3  As we describe before, "from" is for de id who follow/following

# 4 What overlaps do? In this case, we use it, because we autoreference the same user_id as a ForeignKey in two columns in the class Follower.
#         # In SQLAlchemy when you use the same entity for another table two or more times, its produce a warning alert, in this case,
#         # the followers.user_from_id conflicts with followers.user_to_id. With overlaps we tell SQLAlchemy that we know and intentionaly
#         # autorenference that id two times.

# 5 What viewnonly do? I use this atribute in this case to only view the reference data with their followers. With this we can't edit the data from the class User.
#         # That's keep the focus on the class Follower, to edit only there and not in another class. That can prevent conflicts with sincronizations of other tables in the database,
#         # the idea is that we oly edit the Follower information in its own class.


# cascade="all, delete-orphan"
    # First try: cascade its an important atribute for this case, because when we use cascade "all", we indicate is the user has been errease an
    # the database do an automatic edit, save and commit, etc, (all) steps, in the related case Follower to his parent User.
    # Also, we indicate "delete orphan" who its use to indicate if a Follower if removed from his retionship of his parente User, this will be autmatic delete from the database.
    #
    # After of hours of searching: I can understand that all, is used later for simplify the edition of the database. We can edit the database, in manual ways of simple create
    # a variable, put the value as we need and save, an then commit. Or we can created a function that allow us to add, edit, etc, data in our database.
    # delete orphan is not recommended beacuse can we finally eliminate an id has been related as following o followed other user.
    # For example Ana follow Lucas, but then Ana unfollow Lucas. Lucas will been delete, he has been followed from Sophia, in this case, Sophia will not be allowed to
    # see Lucas in this followings.
    #
    # In conclusion: use cascade="all" for convenience in session handling,
    # but avoid "delete-orphan" when dealing with many-to-many or shared relationships.


# Follower
# --
# user_from_id int FK >- User.id
# user_to_id int FK >- User.id

# User x
# --
# id int pk
# user_name str(250) unique
# fisrt_name varchar(250)
# last_name string
# password string(128)
# email string(250) unique

# Post x
# --
# id int pk
# user_id int FK >- User.id

# Media x
# --
# id int pk
# type enum
# url str
# post_id int FK >- Post.id

# Comment x
# --
# id int pk FK >- User.id
# comment_text str
# author_id int fk
# post_id int FK >- Post.id
