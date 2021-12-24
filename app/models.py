from flask_login import UserMixin
from flask import current_app, render_template, url_for
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from hashlib import md5
import jwt
from time import time
# from app.search import add_to_index, remove_from_index, query_index
import json
from datetime import timedelta, datetime
from pytz import timezone
from indeed import IndeedClient
from sqlalchemy import or_
import os


# class SearchableMixin(object):
#     @classmethod
#     def search(cls, expression, page, per_page):
#         # ids, total = query_index(cls.__tablename__, expression, page, per_page)
#         # if total == 0:
#         #     return cls.query.filter_by(id=0), 0
#         # when = []
#         # for i in range(len(ids)):
#         #     when.append((ids[i], i))
#         # return cls.query.filter(cls.id.in_(ids)).order_by(
#         #     db.case(when, value=cls.id)), total
#         results = query_index(cls.__tablename__, expression, page, per_page)
#         return results
#
#
#     @classmethod
#     def before_commit(cls, session):
#         session._changes = {
#             'add': list(session.new),
#             'update': list(session.dirty),
#             'delete': list(session.deleted)
#         }
#
#     @classmethod
#     def after_commit(cls, session):
#         for obj in session._changes['add']:
#             if isinstance(obj, SearchableMixin):
#                 add_to_index(obj.__tablename__, obj)
#         for obj in session._changes['update']:
#             if isinstance(obj, SearchableMixin):
#                 add_to_index(obj.__tablename__, obj)
#         for obj in session._changes['delete']:
#             if isinstance(obj, SearchableMixin):
#                 remove_from_index(obj.__tablename__, obj)
#         session._changes = None
#
#     @classmethod
#     def reindex(cls):
#         for obj in cls.query:
#             add_to_index(cls.__tablename__, obj)
#
#
# db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
# db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# Association Table for multiple forums with multiple users
ForumAssociations = db.Table('ForumAssociations',
                             db.Column('forum_id', db.Integer, db.ForeignKey('forum.id')),
                             db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                             )

MessageBoardAssociations = db.Table('MessageBoardAssociations',
                             db.Column('message_board_id', db.Integer, db.ForeignKey('message_board.id')),
                             db.Column('user_id', db.Integer, db.ForeignKey('user.id')))

#
JobSearchIndustryAssociations = db.Table('JobSearchIndustryAssociations',
                               db.Column('search_id', db.Integer, db.ForeignKey('job_saved_search.id')),
                               db.Column('industry_id', db.Integer, db.ForeignKey('industry.id'))
                                   )


JobListingSSAssociagtions = db.Table('JobListingSSAssociagtions',
                                 db.Column('search_id', db.Integer, db.ForeignKey('job_saved_search.id')),
                                 db.Column('job_id', db.Integer, db.ForeignKey('job_listing.id'))
                                     )

JobIndustryAssociations = db.Table('JobIndustryAssociations',
                                 db.Column('industry_id', db.Integer, db.ForeignKey('industry.id')),
                                 db.Column('job_id', db.Integer, db.ForeignKey('job_listing.id'))
                                     )


JobKeywordAssociations = db.Table('JobKeywordAssociations',
                                 db.Column('keyword_id', db.Integer, db.ForeignKey('job_keyword.id')),
                                 db.Column('job_id', db.Integer, db.ForeignKey('job_listing.id'))
                                     )

JobSSKeywordAssociations = db.Table('JobSSKeywordAssociations',
                                 db.Column('keyword_id', db.Integer, db.ForeignKey('job_keyword.id')),
                                 db.Column('search_id', db.Integer, db.ForeignKey('job_saved_search.id'))
                                     )

SkillUserAssociations = db.Table('SkillUserAssociations',
                                db.Column('skill_id', db.Integer, db.ForeignKey('skill.id')),
                                db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                                   )

InterestUserAssociations = db.Table('InterestUserAssociations',
                                db.Column('interest_id', db.Integer, db.ForeignKey('interest.id')),
                                db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                                    )

HobbyUserAssociations = db.Table('HobbyUserAssociations',
                                db.Column('hobby_id', db.Integer, db.ForeignKey('hobby.id')),
                                db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                                 )

BackgroundUserAssociations = db.Table('BackgroundUserAssociations',
                                db.Column('background_id', db.Integer, db.ForeignKey('background.id')),
                                db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                                 )

ValueUserAssociations = db.Table('ValueUserAssociations',
                                db.Column('value_id', db.Integer, db.ForeignKey('value.id')),
                                db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                                 )

InstitutionAssociations = db.Table('InstitutionAssociations',
                                db.Column('institution_id', db.Integer, db.ForeignKey('institution.id')),
                                db.Column('profile_id', db.Integer, db.ForeignKey('recruiting_profile.id'))
                                   )

ProfileIndustryAssociations = db.Table('ProfileIndustryAssociations',
                                db.Column('industry_id', db.Integer, db.ForeignKey('industry.id')),
                                db.Column('profile_id', db.Integer, db.ForeignKey('recruiting_profile.id'))
                                       )

ProfileCityAssociations = db.Table('ProfileCityAssociations',
                                db.Column('city_id', db.Integer, db.ForeignKey('city.id')),
                                db.Column('profile_id', db.Integer, db.ForeignKey('recruiting_profile.id'))
                                   )

PostLikes = db.Table('PostLikes',
                                db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                                db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                                   )

UpVotes = db.Table('UpVotes',
                                db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')),
                                db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                                   )

DownVotes = db.Table('DownVotes',
                                db.Column('comment_id', db.Integer, db.ForeignKey('comment.id')),
                                db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                                   )

EventIndustryAssociations = db.Table('EventIndustryAssociations',
                                db.Column('event_id', db.Integer, db.ForeignKey('event.id')),
                                db.Column('industry_id', db.Integer, db.ForeignKey('industry.id'))
                                     )

ResourceTypeAssociations = db.Table('ResourceTypeAssociations',
                                db.Column('resource_id', db.Integer, db.ForeignKey('resource.id')),
                                db.Column('resource_type_id', db.Integer, db.ForeignKey('resource_type.id'))
                                    )

BlogAuthorAssociations = db.Table('BlogAuthorAssociations',
                                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                                db.Column('blog_post_id', db.Integer, db.ForeignKey('blog_post.id'))
                                  )

SpeakerEventAssociations = db.Table('SpeakerEventAssociations',
                                db.Column('speaker_profile_id', db.Integer, db.ForeignKey('speaker_profile.id')),
                                db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
                                    )


AppointmentParticipantAssociations = db.Table('AppointmentParticipantAssociations',
                                              db.Column('appointment_id', db.Integer, db.ForeignKey('appointment.id')),
                                              db.Column('user_id', db.Integer, db.ForeignKey('user.id'))
                                              )
#
class User(UserMixin, db.Model):
    __searchable__ = ['name', 'username', 'email', 'company_name', 'position_title']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    password_length = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))  # 1 user has 1 country
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))  # 1 user has 1 state if applicable
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))  # 1 user has 1 city
    zip_code_id = db.Column(db.Integer, db.ForeignKey('zip_code.id'))  # 1 user has 1 zip if applicable
    industry_id = db.Column(db.Integer, db.ForeignKey('industry.id'))  # TODO: 1 user has 1 Industry (not true)
    company_name = db.Column(db.String(64), index=True) # rid
    position_title = db.Column(db.String(64), index=True) # rid
    experience_id = db.Column(db.Integer(), db.ForeignKey('experience.id')) # rid
    completed = db.Column(db.Integer())
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    forums = db.relationship('Forum', secondary=ForumAssociations, backref='xxx')
    liked_posts = db.relationship('Post', secondary=PostLikes, backref='user')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    directory = db.Column(db.String(150))
    resume = db.Column(db.Boolean, default=False)
    fired = db.Column(db.DateTime) # rid
    img = db.Column(db.Boolean, default=False)
    created = db.Column(db.DateTime)
    post_reports = db.relationship('PostReport', backref='user', lazy='dynamic')
    comment_reports = db.relationship('CommentReport', backref='user', lazy='dynamic')
    comment_votes = db.relationship('CommentVote', backref='user', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user',
                                    lazy='dynamic', order_by='desc(Notification.timestamp)')
    sent_messages = db.relationship('Message', backref='author', lazy='dynamic')
    message_boards = db.relationship('MessageBoard', secondary=MessageBoardAssociations, backref='xxx', order_by='desc(MessageBoard.last_active)')
    message_boards_activity = db.relationship('MessageBoardActivity', backref='ccc', lazy='dynamic')
    recruiter_visibility = db.Column(db.Integer, default=0)
    recruiting_bio = db.Column(db.String(500))
    is_recruiter = db.Column(db.Boolean, default=False)
    recruiter = db.relationship('Recruiter', backref='user', uselist=False)
    job_searches = db.relationship('JobSavedSearch', backref='user', lazy='dynamic')
    mail_activity = db.relationship('MailActivity', backref='user', lazy='dynamic')
    job_connections_activity = db.relationship('Candidate', backref='user', lazy='dynamic')
    resume_views = db.relationship('ResumeView', backref='user', lazy='dynamic')
    job_found_reports = db.relationship('JobFound', backref='user', lazy='dynamic')
    email_verified = db.Column(db.Boolean, default=False)
    password_reset_state = db.Column(db.Boolean, default=False)
    suggested_forums = db.relationship('SuggestedForum', backref='user', lazy='dynamic')
    recruiting_profile = db.relationship('RecruitingProfile', backref='user', uselist=False)
    upvotes_total = db.relationship('Comment', secondary=UpVotes)
    downvotes_total = db.relationship('Comment', secondary=DownVotes)
    applied_jobs = db.relationship('Applicant', backref='user', lazy='dynamic')
    skills = db.relationship('Skill', secondary=SkillUserAssociations, backref='user')
    backgrounds = db.relationship('Background', secondary=BackgroundUserAssociations, backref='user')
    values = db.relationship('Value', secondary=ValueUserAssociations, backref='user')
    hobbies = db.relationship('Hobby', secondary=HobbyUserAssociations, backref='user')
    interests = db.relationship('Interest', secondary=InterestUserAssociations, backref='user')
    unsubscribed = db.Column(db.Boolean, default=False)
    date_unsubscribed = db.Column(db.DateTime)  # rid
    blogs = db.relationship('BlogPost', secondary=BlogAuthorAssociations, backref='blog')
    blog_about = db.Column(db.String(500))
    partner_click_outs = db.relationship('PartnerClicks', backref='user', lazy='dynamic')
    admin = db.Column(db.Boolean)
    speaker_profile = db.relationship('SpeakerProfile', backref='user', uselist=False)
    event_rsvps = db.relationship('EventRsvp', backref='user', lazy='dynamic')
    event_rewatches = db.relationship('EventRewatch', backref='user', lazy='dynamic')
    admin_sent_emails = db.relationship('CustomEmail', backref='user', lazy='dynamic')
    mentor_profile = db.relationship('MentorProfile', backref='user', uselist=False)
    intended_mentor = db.Column(db.Boolean, default=False)
    mentor_ratings = db.relationship('MentorRating', backref='user', lazy='dynamic')
    appointments = db.relationship('Appointment', secondary=AppointmentParticipantAssociations, backref='user')
    appointment_notes = db.relationship('MenteeNote', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        if not self.img:
            digest = md5(self.email.lower().encode('utf-8')).hexdigest()
            return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
        else:
            return 'https://ilmjtcv-user-static-files.s3.us-east-2.amazonaws.com/' + str(self.directory) + '/user_img' + str(size) + '.jpg'

    def get_resume(self):
        if self.resume:
            return 'https://ilmjtcv-user-static-files.s3.us-east-2.amazonaws.com/' + str(self.directory) + '/resume.pdf'

    def get_linked_in(self):
        if self.recruiting_profile != None:
            return self.recruiting_profile.linked_in
        else:
            return None

    def is_mentor(self):
        if self.mentor_profile is not None and self.mentor_profile.status > 0:
            return True
        else:
            return False

    def set_location(self, codes):
        self.country_id = codes['country']
        self.state_id = codes['state']
        self.city_id = codes['city']
        self.zip_code_id = codes['zip']

    def suggest_forums(self, new_search=False):
        if new_search:
            for search in self.job_searches:
                for industry in search.industries:
                    f = Forum.query.filter_by(location_type=0, industry_id=industry.id).first_or_404()
                    f.recommend(self)
        else:
            f = Forum.query.filter_by(location_type=0, industry_id=self.industry_id).first_or_404()
            f.recommend(self)

    def add_forums(self):
        for i in Forum.query.filter_by(location_type=-1).all():
            i.join(self)
        for i in Forum.query.filter_by(location_type=-2).all():
            i.recommend(self)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def get_email_confirmation_token(self, expires_in=604800):
        return jwt.encode(
            {'email_confirmation': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def get_account_deletion_token(self, expires_in=600):
        return jwt.encode(
            {'account_deletion': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def verify_email_confirmation_token(token):
        try: id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['email_confirmation']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def verify_account_deletion_token(token):
        try: id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['account_deletion']
        except:
            return
        return User.query.get(id)

    # def get_resources(self):
    #     resources = []
    #     if self.zip_code_id is not None:
    #         zip = self.zip_code
    #         for i in zip.resources.all():
    #             resources.append(i)
    #     if self.city_id is not None:
    #         city = self.city
    #         for i in city.resources.filter_by(zip_code_id=None).all():
    #             resources.append(i)
    #         state = self.state
    #         for i in state.resources.filter_by(city_id=None, zip_code_id=None).all():
    #             resources.append(i)
    #         country = self.country
    #         for i in country.resources.filter_by(state_id=None, city_id=None, zip_code_id=None).all():
    #             resources.append(i)
    #     return resources

    def new_messages(self):
        count = 0
        for board in self.message_boards_activity:
            if board.last_seen < board.message_board.last_active:
                count += 1
        return count
        # return MessageBs.query.filter_by(recipient=self, read=None).count()

    # def get_jobs(self, viewed=False, applied=False):
    #     if not viewed and not applied:
    #         jobs = JobListing.query.filter_by(active=True, city_id=self.city_id, industry_id=self.industry_id)\
    #             .order_by(JobListing.date.desc()).all()
    #         # jobs = [x for x in jobs if x.activity.filter_by(user_id=self.id).count() == 0 or
    #         #         x.activity.filter_by(user_id=self.id).first().status == 0]
    #
    #     elif viewed and not applied:
    #         jobs = db.session.query(JobListing).join(JobListingActivity).filter(
    #             JobListingActivity.job_id == JobListing.id,
    #             JobListingActivity.user_id == self.id,
    #             JobListingActivity.status == 1
    #         ).all()
    #     elif not viewed and applied:
    #         jobs = db.session.query(JobListing).join(JobListingActivity).filter(
    #             JobListingActivity.job_id == JobListing.id,
    #             JobListingActivity.user_id == self.id,
    #             JobListingActivity.status == 2
    #         ).all()
    #     elif viewed and applied:
    #         jobs = db.session.query(JobListing).join(JobListingActivity).filter(
    #             JobListingActivity.job_id == JobListing.id,
    #             JobListingActivity.user_id == self.id,
    #             JobListingActivity.status == (1 or 2)
    #         ).all()
    #     return jobs

    def last_sent(self):
        return self.mail_activity.order_by(MailActivity.timestamp.desc()).first().timestamp

    def candidacies(self):
        return Candidate.query.join(SavedSearch).filter(
            SavedSearch.id == Candidate.search_id,
            SavedSearch.status == 1,
            Candidate.user_id == self.id,
            SavedSearch.agency_id != 45
        ).all()

    def applicancies(self):
        return Applicant.query.join(MessageBoard, (MessageBoard.applicant_id == Applicant.id)).filter(
            Applicant.user_id == self.id,
            Applicant.status != -1,
        ).all()

    def get_boards(self, type=0, start=None):
        if int(type) == 0:
            if start is not None:
                return db.session.query(MessageBoard).join(MessageBoardActivity,
                                                           (MessageBoardActivity.message_board_id == MessageBoard.id)
                                                           ).filter(
                    MessageBoardActivity.user_id == self.id
                ).order_by(MessageBoardActivity.last_seen >= MessageBoard.last_active
                           ).order_by(MessageBoard.last_active.desc()
                                      ).all()[int(start): int(start) + 10]
            else:
                return db.session.query(MessageBoard).join(MessageBoardActivity,
                                                           (MessageBoardActivity.message_board_id == MessageBoard.id)
                                                           ).filter(
                    MessageBoardActivity.user_id == self.id
                ).order_by(MessageBoardActivity.last_seen <= MessageBoard.last_active
                           ).order_by(MessageBoard.last_active.desc()
                                      ).all()


    def get_resume_views(self, daysback=None):
        if daysback is None:
            least = self.last_seen
        else:
            least = datetime.utcnow() - timedelta(days=int(daysback))
        c = self.resume_views.filter(ResumeView.timestamp >= least).count()
        return c

    def new_agencies(self, daysback=None):
        if daysback is None:
            return RecruitingAgency.query.filter(RecruitingAgency.date_joined > self.last_seen).count()
        else:
            return RecruitingAgency.query.filter(RecruitingAgency.date_joined > datetime.utcnow() - timedelta(days=int(daysback))).count()

    def new_recruiters(self, daysback=None):
        if daysback is None:
            return db.session.query(Recruiter).join(User).filter(
                Recruiter.user_id == User.id,
                User.created >= self.last_seen
            ).count()
        else:
            return db.session.query(Recruiter).join(User).filter(
                Recruiter.user_id == User.id,
                User.created >= datetime.utcnow() - timedelta(days=int(daysback)
            )).count()

    def new_users_area(self, daysback=None):
        if daysback is None:
            return User.query.filter(User.created > self.last_seen, User.city_id == self.city_id).count()
        else:
            return User.query.filter(User.created > datetime.utcnow() - timedelta(days=int(daysback)), User.city_id == self.city_id).count()

    def new_users_industry(self, daysback=None):
        if daysback is None:
            return User.query.filter(User.created > self.last_seen, User.industry_id == self.industry_id).count()
        else:
            return User.query.filter(User.created > datetime.utcnow() - timedelta(days=int(daysback)), User.industry_id == self.industry_id).count()

    def new_users_both(self, daysback=None):
        if daysback is None:
            return User.query.filter(User.created > self.last_seen, User.industry_id == self.industry_id, User.city_id == self.city_id).count()
        else:
            return User.query.filter(User.created > datetime.utcnow() - timedelta(days=int(daysback)), User.industry_id == self.industry_id, User.city_id == self.city_id).count()

    def new_industry_jobs(self, daysback=None):
        if daysback is None:
            return JobListing.query.filter(JobListing.date_found > self.last_seen, JobListing.industry_id == self.industry_id).count()
        else:
            return JobListing.query.filter(JobListing.date_found > datetime.utcnow() - timedelta(days=int(daysback)), JobListing.industry_id == self.industry_id).count()

    def add_first_job_ss(self):
        title = str(self.industry.title) + ' (' + str(self.city.name) + ') -- Trial Search'
        description = 'We have added this search for you automatically based on your initial location and primary industry inputs. Feel free to add other searches to your profile. Happy job hunting!'
        search = JobSavedSearch(title=title, snippet=description, user_id=self.id, l_specific=True,
                                city_id=self.city_id, proximity_id=2, status=1, start=datetime.utcnow(),
                                last_updated=datetime.utcnow(), last_checked=datetime.utcnow() - timedelta(minutes=5))
        search.industries.append(self.industry)
        db.session.add(search)
        db.session.commit()
        search.get_first_page_results()

    def new_notifications(self):
        return self.notifications.filter_by(read=False).count()

    def delete_user(self, reason=None):
        try:
            self.message_boards = []
            self.forums = []
            self.upvotes_total = []
            self.downvotes_total = []
            self.liked_posts = []
            for p in Post.query.filter_by(user_id=self.id).all():
                p.delete()
            for p in Comment.query.filter_by(user_id=self.id).all():
                p.delete()
            for s in SuggestedForum.query.filter_by(user_id=self.id).all():
                db.session.delete(s)
            if self.is_recruiter:
                self.recruiter.delete()
            for j in self.job_searches:
                j.status = 0
            for i in self.sent_messages:
                db.session.delete(i)
            for i in self.message_boards_activity:
                db.session.delete(i)
            if self.recruiting_profile is not None:
                self.recruiting_profile.delete()
            for j in self.job_connections_activity:
                j.delete()
            for k in self.applied_jobs:
                k.delete_applicant(full=True)
            db.session.commit()
        except:
            print('error')
        d = DeletedUser(user_id=self.id, username=self.username, email=self.email, reason=reason,
                        timestamp=datetime.utcnow())
        db.session.add(d)
        db.session.delete(self)
        db.session.commit()

    def get_followed_posts(self, type=0, start=None):
        if int(type) == 0:
            if start is not None:
                return Post.query.filter_by(deleted=0).join(ForumAssociations,
                                                            (ForumAssociations.c.forum_id == Post.forum_id)).filter(
                    ForumAssociations.c.user_id == self.id).order_by(
                    Post.timestamp.desc()).all()[int(start):int(start) + 10]
            else:
                return Post.query.filter_by(deleted=0).join(ForumAssociations, (ForumAssociations.c.forum_id == Post.forum_id)).filter(
                    ForumAssociations.c.user_id == self.id).order_by(
                            Post.timestamp.desc())
        elif int(type) == 1:
            # session = db.session.query(Post, (PostLikes.c.post_id).label('total')).join(PostLikes) \
            #               .group_by(Post).join(ForumAssociations, (ForumAssociations.c.forum_id == Post.forum_id)) \
            #               .filter(Post.deleted == 0, ForumAssociations.c.user_id == self.id) \
            #               .order_by('total') \
            #               .all()[::-1]
            posts = Post.query.filter_by(deleted=0).join(ForumAssociations,
                                                 (ForumAssociations.c.forum_id == Post.forum_id)).filter(
                ForumAssociations.c.user_id == self.id).all()
            session = sorted(posts, key= lambda r: r.get_likes(), reverse=True)
            if start is not None:
                return session[int(start):int(start) + 10]
            else:
                return session

    def unread_notifications(self):
        if self.notifications.filter_by(read=False).count() > 0:
            return True
        else:
            return False

    def unsubscribe(self):
        if not self.is_recruiter:
            self.unsubscribed = True
            self.date_unsubscribed = datetime.utcnow()
            db.session.commit()
            return True
        else:
            return False

    def resubscribe(self):
        if not self.is_recruiter:
            self.unsubscribed = False
            self.date_unsubscribed = None
            db.session.commit()
            return True
        else:
            return False

    def render_social_card(self, num=None):
        return render_template('main/social_profile_card.html', user=self, num=num)

    def similar_people(self, start=None, existing=[]):
        users = []
        for hobby in self.hobbies:
            for user in hobby.users[:50]:
                if user.id not in existing and user != self:
                    if user not in [j[0] for j in users]:
                        users.append([user, 1])
                    else:
                        users[[i[0] for i in users].index(user)][1] = 0
        for background in self.backgrounds:
            for user in background.users[:50]:
                if user.id not in existing and user != self:
                    if user not in [j[0] for j in users]:
                        users.append([user, 2])
                    else:
                        users[[i[0] for i in users].index(user)][1] = 0
        for skill in self.skills:
            for user in skill.users[:50]:
                if user.id not in existing and user != self:
                    if user not in [j[0] for j in users]:
                        users.append([user, 3])
                    else:
                        users[[i[0] for i in users].index(user)][1] = 0
        for value in self.values:
            for user in value.users[:50]:
                if user.id not in existing and user != self:
                    if user not in [j[0] for j in users]:
                        users.append([user, 4])
                    else:
                        users[[i[0] for i in users].index(user)][1] = 0
        for interest in self.interests:
            for user in interest.users[:50]:
                if user.id not in existing and user != self:
                    if user not in [j[0] for j in users]:
                        users.append([user, 5])
                    else:
                        users[[i[0] for i in users].index(user)][1] = 0
        if self.industry is not None:
            for user in self.industry.users[:50]:
                if user.id not in existing and user != self:
                    if user not in [j[0] for j in users]:
                        users.append([user, 6])
                    else:
                        users[[i[0] for i in users].index(user)][1] = 0
        for user in self.city.users[:50]:
            if user.id not in existing and user != self:
                if user not in [j[0] for j in users]:
                    users.append([user, 7])
                else:
                    users[[i[0] for i in users].index(user)][1] = 0

        if start is not None:
            return sorted(users[int(start):int(start) + 10], key= lambda r: r[1])
        else:
            return users

    def get_resources(self, type=0, start=None):
        if int(type) == 0:
            resources = Resource.query.filter_by(active=True).join(ResourceTypeAssociations, (Resource.id == ResourceTypeAssociations.c.resource_id)).filter(
                ResourceTypeAssociations.c.resource_type_id == 1
            ).order_by(Resource.added.desc()).all()
        elif int(type) == 1:
            resources = Resource.query.filter_by(active=True).join(ResourceTypeAssociations, (
                    Resource.id == ResourceTypeAssociations.c.resource_id)).filter(
                ResourceTypeAssociations.c.resource_type_id == 2,
            ).filter(
                or_(Resource.state_id == self.state_id, Resource.country_id == self.country_id)
            ).order_by(Resource.state_id.desc()).order_by(Resource.title.asc()).order_by(Resource.added.desc()).all()
        elif int(type) == 2:
            resources = Resource.query.filter_by(active=True).join(ResourceTypeAssociations, (
                    Resource.id == ResourceTypeAssociations.c.resource_id)).filter(
                ResourceTypeAssociations.c.resource_type_id == 3,
            ).order_by(Resource.title.asc()).order_by(Resource.added.desc()).all()
        elif int(type) == 3:
            resources = Resource.query.filter_by(active=True).join(ResourceTypeAssociations, (
                        Resource.id == ResourceTypeAssociations.c.resource_id)).filter(
                ResourceTypeAssociations.c.resource_type_id == 4
            ).order_by(Resource.added.desc()).all()
        else:
            resources = []
        if start is not None:
            return resources[int(start):int(start) + 10]
        else:
            return resources

    def get_events(self, type, start):
        if int(type) == 0:
            events = Event.query.filter(Event.time_end >= datetime.utcnow()).order_by(Event.time_start).all()
        elif int(type) == 1:
            events = Event.query.filter(Event.time_end <= datetime.utcnow()).order_by(Event.time_start).all()
        else:
            events = []
        if start is not None:
            return events[int(start): int(start) + 5]
        else:
            return events

    def get_completed_sessions(self):
        return db.session.query(Appointment).join(AppointmentParticipantAssociations, (AppointmentParticipantAssociations.c.appointment_id == Appointment.id)).filter(
            AppointmentParticipantAssociations.c.user_id == self.id,
            Appointment.end_time <= datetime.utcnow()
        ).count()

    def last_sent_mail(self, type, duration):
        mail = MailActivity.query.filter(MailActivity.type == type,
                                     MailActivity.user_id == self.id).order_by(MailActivity.timestamp.desc()).first()
        if mail is not None:
            if datetime.utcnow() - mail.timestamp > duration:
                return True
            else:
                return False
        else:
            return True


class Recruiter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agency_id = db.Column(db.Integer, db.ForeignKey('recruiting_agency.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    industry_interest_id = db.Column(db.Integer, db.ForeignKey('industry.id'))
    admin = db.Column(db.Integer)
    status = db.Column(db.Integer)
    searches = db.relationship('RecruiterSearchAssociation', backref='recruiter', lazy='dynamic')
    resume_views = db.relationship('ResumeView', backref='recruiter', lazy='dynamic')
    notes = db.relationship('SavedSearchNote', backref='recruiter', lazy='dynamic')
    c_notes = db.relationship('CandidateNote', backref='recruiter', lazy='dynamic', order_by='desc(CandidateNote.timestamp)')
    job_postings = db.relationship('RecruiterJobAssociation', backref='recruiter', lazy='dynamic')
    job_posting_notes = db.relationship('JobPostingNote', backref='recruiter', lazy='dynamic')
    a_notes = db.relationship('ApplicantNote', backref='recruiter', lazy='dynamic', order_by='desc(ApplicantNote.timestamp)')


    def get_initial_confirm_token(self, expires_in=2419200):
        if self.status < 1:
            return jwt.encode(
                {'recruiter_confirmation': self.id, 'exp': time() + expires_in},
                current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_confirmation_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['recruiter_confirmation']
        except:
            return
        recruiter = Recruiter.query.get(id)
        if recruiter.status < 1:
            return recruiter
        else:
            return

    def get_searches(self, type):
        if int(type) == 0:
            return db.session.query(SavedSearch).join(RecruiterSearchAssociation).filter(
                SavedSearch.id == RecruiterSearchAssociation.search_id,
                RecruiterSearchAssociation.recruiter_id == self.id,
                SavedSearch.status == 0
            ).all()
        elif int(type) == 1:
            return db.session.query(SavedSearch).join(RecruiterSearchAssociation).filter(
                SavedSearch.id == RecruiterSearchAssociation.search_id,
                RecruiterSearchAssociation.recruiter_id == self.id,
                SavedSearch.status == 1
            ).all()
    def add_first_search(self):
        search = SavedSearch(title='Demo Search', snippet="We've added this search for you based on your industry interest.",
                             industry_id=self.industry_interest_id, city_id=None,
                             status=1, last_updated=datetime.utcnow(), public=False,
                             agency_id=self.agency_id, l_specific=False)
        db.session.add(search)
        db.session.commit()
        search.add_initial_recruiters(self.user, initial=True)
        search.apply_results()

    def delete(self):
        for c in self.c_notes:
            db.session.delete(c)
        for c in self.notes:
            db.session.delete(c)
        for c in self.resume_views:
            db.session.delete(c)
        for s in self.searches:
            db.session.delete(s)
        for a in self.a_notes:
            db.session.delete(a)
        for j in self.job_posting_notes:
            db.session.delete(j)
        for x in self.job_postings:
            db.session.delete(x)
        db.session.delete(self)
        db.session.commit()

    def get_job_postings(self, type):
        if int(type) == 0:
            return db.session.query(JobListing).join(RecruiterJobAssociation).filter(
                JobListing.id == RecruiterJobAssociation.job_id,
                RecruiterJobAssociation.recruiter_id == self.id,
                JobListing.active == False
            ).all()
        elif int(type) == 1:
            return db.session.query(JobListing).join(RecruiterJobAssociation).filter(
                JobListing.id == RecruiterJobAssociation.job_id,
                RecruiterJobAssociation.recruiter_id == self.id,
                JobListing.active == True
            ).all()


class RecruitingAgency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    website = db.Column(db.String(100))
    directory = db.Column(db.String(100))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    date_requested = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Integer)
    request_name = db.Column(db.String(100))
    request_email = db.Column(db.String(120))
    additional_info = db.Column(db.String(150))
    recruiters = db.relationship('Recruiter', backref='agency', lazy='dynamic')
    searches = db.relationship('SavedSearch', backref='agency', lazy='dynamic')
    job_listing_profile = db.relationship('JobLister', backref='agency', uselist=False)

    def avatar(self, size):
        if self.directory is None:
            return 'https://ilmjtcv-recruiting-agencies.s3.us-east-2.amazonaws.com/sample' + '/accnt_img' + str(size) + '.jpg'
        else:
            return 'https://ilmjtcv-recruiting-agencies.s3.us-east-2.amazonaws.com/' + str(
                self.directory) + '/accnt_img' + str(size) + '.jpg'

    def get_initial_confirm_token(self, expires_in=604800):
        return jwt.encode(
            {'partnership_confirmation': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_confirmation_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['partnership_confirmation']
        except:
            return
        return RecruitingAgency.query.get(id)

    def activate_org(self):
        self.status = 2
        self.date_joined = datetime.utcnow()
        for recruiter in self.recruiters:
            recruiter.user.completed = 0
            recruiter.status = 0
        db.session.commit()

    def delete_agency(self):
        for recruiter in self.recruiters:
            recruiter.delete()
        self.job_listing_profile.delete()
        for search in self.searches:
            search.delete()
        db.session.delete(self)
        db.session.commit()

    def reject_agency(self):
        for recruiter in self.recruiters:
            db.session.delete(recruiter.user)
            db.session.delete(recruiter)
        self.job_listing_profile.delete()
        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    __searchable__ = ['title', 'body']
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100))
    body = db.Column(db.String(1800))
    forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    deleted = db.Column(db.Integer, default=0) # 0 or None (active), 1 deleted by user, 2 deleted by admin, 3 account deleted by user, 4 account deleted by admin
    date_deleted = db.Column(db.DateTime)
    reports = db.relationship('PostReport', backref='post', lazy='dynamic')
    liked_posts = db.relationship('User', secondary=PostLikes, backref='post')

    def get_comments(self, type=0, start=None):
        if int(type) == 0:
            if start is not None:
                return self.comments.filter_by(deleted=0).order_by(Comment.timestamp.desc()).all()[int(start): int(start) + 10]
            else:
                return self.comments.filter_by(deleted=0).order_by(Comment.timestamp.desc())
        elif int(type) == 1:
            raw = self.comments.filter_by(deleted=0).all()
            session = sorted(raw, key=lambda comment: comment.vote_total(), reverse=True)
            if start is not None:
                return session[int(start): int(start) + 10]
            else:
                return session

    def get_likes(self):
        return len(self.liked_posts)

    def like(self, user):
        if user not in self.liked_posts:
            self.liked_posts.append(user)
            db.session.commit()

    def unlike(self, user):
        if user in self.liked_posts:
            self.liked_posts.remove(user)
            db.session.commit()

    def is_liked(self, user):
        if user in self.liked_posts:
            return True
        else:
            return False

    def delete(self):
        self.deleted = 1
        self.date_deleted = datetime.utcnow()
        db.session.commit()

    def render_html(self, type=0):
        if int(type) == 0:
            return render_template('/main/posts/_post_preview_full.html', post=self)
        elif int(type) == 1:
            return render_template('/main/posts/_post_preview.html', post=self)
        elif int(type) == 2:
            return render_template('/main/posts/post_page.html', post=self)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    body = db.Column(db.String(1800))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    upvotes = db.relationship('User', secondary=UpVotes)
    downvotes = db.relationship('User', secondary=DownVotes)
    votes = db.relationship('CommentVote', backref='comment', lazy='dynamic')
    deleted = db.Column(db.Integer, default=0)  # 0 or None (active), 1 deleted by user, 2 deleted by admin, 3 account deleted by user, 4 account deleted by admin
    date_deleted = db.Column(db.DateTime)
    reports = db.relationship('CommentReport', backref='comment', lazy='dynamic')

    def render_html(self):
        return render_template('/main/posts/_comment.html', comment=self)

    def delete(self):
        self.deleted = 1
        self.date_deleted = datetime.utcnow()
        db.session.commit()

    def upvote(self, user):
        if user not in self.upvotes:
            self.upvotes.append(user)
            if user in self.downvotes:
                self.downvotes.remove(user)
        else:
            self.upvotes.remove(user)
        db.session.commit()

    def downvote(self, user):
        if user not in self.downvotes:
            self.downvotes.append(user)
            if user in self.upvotes:
                self.upvotes.remove(user)
        else:
            self.downvotes.remove(user)
        db.session.commit()

    def vote_total(self):
        return int(len(self.upvotes) - len(self.downvotes))

    def vote_status(self, user):
        if user in self.upvotes:
            return 1
        elif user in self.downvotes:
            return -1
        else:
            return 0


class Forum(db.Model):
    __searchable__ = ['title']
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    location_type = db.Column(db.Integer)  # 1=zip, 2=city, 3=state, 4=country
    location_id = db.Column(db.Integer)
    industry_id = db.Column(db.Integer, db.ForeignKey('industry.id'))
    snippet = db.Column(db.String(100))
    posts = db.relationship('Post', backref='forum', lazy='dynamic')
    users = db.relationship('User', secondary=ForumAssociations, backref='xxx')
    suggested = db.relationship('SuggestedForum', backref='forum', lazy='dynamic')
    icon = db.Column(db.String(100))


    def get_posts(self, type=0, start=None):
        if int(type) == 0:
            if start is not None:
                return self.posts.filter_by(deleted=0).order_by(Post.timestamp.desc()).all()[int(start): int(start) + 10]
            else:
                return self.posts.filter_by(deleted=0).order_by(Post.timestamp.desc())
        elif int(type) == 1:
            # session = db.session.query(Post, func.count(PostLikes.c.post_id).label('total')).group_by(Post).\
            #     filter(Post.forum_id == self.id, Post.deleted==0).order_by('total').all()[::-1]
            posts = self.posts.filter_by(deleted=0).all()
            session = sorted(posts, key= lambda r: r.get_likes(), reverse=True)
            if start is not None:
                return session[int(start): int(start) + 10]
            else:
                return session

    def recommend(self, user):
        if user not in self.users:
            s = SuggestedForum.query.filter_by(user_id=user.id, forum_id=self.id)
            if s.count() == 0:
                s = SuggestedForum(user_id=user.id, forum_id=self.id, reason=0, status=0,
                                   timestamp_found=datetime.utcnow())
                db.session.add(s)
                db.session.commit()

    def join(self, user):
        if user not in self.users:
            s = SuggestedForum.query.filter_by(user_id=user.id, forum_id=self.id)
            if s.count() > 0:
                s.first().status = 1
            else:
                s = SuggestedForum(user_id=user.id, forum_id=self.id, reason=0, status=1,
                                   timestamp_found=datetime.utcnow())
                db.session.add(s)
            self.users.append(user)
            db.session.commit()

    def leave(self, user, special=None):
            s = SuggestedForum.query.filter_by(user_id=user.id, forum_id=self.id)
            if s.count() > 0:
                if special is None:
                    s.first().status = 0
                else:
                    db.session.delete(s.first())
            else:
                if special is None:
                    s = SuggestedForum(user_id=user.id, forum_id=self.id, reason=0, status=0,
                                       timestamp_found=datetime.utcnow())
                    db.session.add(s)
            if user in self.users:
                self.users.remove(user)
            db.session.commit()

    def get_icon(self):
        if self.industry_id is None or self.industry_id == 0:
            return self.icon
        else:
            return self.industry.icon

    def followed(self, user):
        if user in self.users:
            return True
        else:
            return False

class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    code = db.Column(db.String(2))
    users = db.relationship('User', backref='country', lazy='dynamic')  # 1 country has many users
    states = db.relationship('State', backref='country', lazy='dynamic')  # 1 country has many states
    cities = db.relationship('City', backref='country', lazy='dynamic')  # 1 country has many cities
    zips = db.relationship('ZipCode', backref='country', lazy='dynamic')  # 1 country has many zip-codes
    resources = db.relationship('Resource', backref='country', lazy='dynamic')


class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    code = db.Column(db.String(2))
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))   # 1 state has 1 country
    users = db.relationship('User', backref='state', lazy='dynamic')  # 1 state has many users
    cities = db.relationship('City', backref='state', lazy='dynamic')  # 1 state has many cities
    zips = db.relationship('ZipCode', backref='state', lazy='dynamic')  # 1 state has many zip-codes
    resources = db.relationship('Resource', backref='state', lazy='dynamic')
    img = db.Column(db.String(150))

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))  # 1 city has 1 country
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))  # 1 city has 1 state
    users = db.relationship('User', backref='city', lazy='dynamic')  # 1 city has many users
    zips = db.relationship('ZipCode', backref='city', lazy='dynamic')   # 1 city has many zip codes
    lat = db.Column(db.Float())
    long = db.Column(db.Float())
    resources = db.relationship('Resource', backref='city', lazy='dynamic')
    jobs = db.relationship('JobListing', backref='city', lazy='dynamic')
    searches = db.relationship('SavedSearch', backref='city', lazy='dynamic')
    job_searches = db.relationship('JobSavedSearch', backref='city', lazy='dynamic')
    institutions = db.relationship('Institution', backref='city', lazy='dynamic')
    profiles = db.relationship('RecruitingProfile', secondary=ProfileCityAssociations, backref='city')

class ZipCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10))
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))  # 1 zip has 1 country
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))  # 1 zip has 1 state
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))  # 1 zip has 1 city
    users = db.relationship('User', backref='zip_code', lazy='dynamic')  # 1 zip has many users
    lat = db.Column(db.Float())
    long = db.Column(db.Float())


class Industry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    forum_title = db.Column(db.String(100))
    icon = db.Column(db.String(100))
    users = db.relationship('User', backref='industry', lazy='dynamic')  # 1 inudstry has many users
    forums = db.relationship('Forum', backref='industry', lazy='dynamic')
    recruiters = db.relationship('Recruiter', backref='industry_interest', lazy='dynamic')
    searches = db.relationship('SavedSearch', backref='industry', lazy='dynamic')
    job_search_associations = db.relationship('JobSavedSearch', secondary=JobSearchIndustryAssociations, backref='industry')
    jobs = db.relationship('JobListing', secondary=JobIndustryAssociations, backref='industry')
    profiles = db.relationship('RecruitingProfile', secondary=ProfileIndustryAssociations, backref='industry')
    events = db.relationship('Event', secondary=EventIndustryAssociations, backref='industry')


    def get_info(self):
        return {'users_first': self.users.count(), 'recruiters_interest': self.recruiters.count(),
                'recruiter_searches': self.searches.count(), 'job_searches': len(self.job_search_associations),
                'jobs': len(self.jobs), 'profiles': len(self.profiles)}

class Proximity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    searches = db.relationship('JobSavedSearch', backref='proximity', lazy='dynamic')


class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(15))
    users = db.relationship('User', backref='experience', lazy='dynamic')  # 1 inudstry has many users
    searches = db.relationship('SavedSearch', backref='experience', lazy='dynamic')
    profiles = db.relationship('RecruitingProfile', backref='experience', lazy='dynamic')


class ResourceType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(400))
    resources = db.relationship('Resource', secondary=ResourceTypeAssociations, backref='type')
    """
        1 = Virtual networking events and job fairs
        2 = Unemployment assistance (location)
        3 = Food and shelter (location)
        4 = Personal education
    """


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    types = db.relationship('ResourceType', secondary=ResourceTypeAssociations, backref='resource')
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'))
    state_id = db.Column(db.Integer, db.ForeignKey('state.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    virtual = db.Column(db.Boolean)
    link = db.Column(db.String(400))
    title = db.Column(db.String(400))
    description = db.Column(db.String(5000))
    img = db.Column(db.String(800))
    added = db.Column(db.DateTime)
    active = db.Column(db.Boolean)

    def avatar(self):
        if self.img is not None:
            return self.img
        else:
            return self.state.img

    def render_html(self):
        return render_template('main/mentorship/resources/_resource.html', resource=self)

    def get_location(self):
        if self.virtual:
            return 'NONE'
        else:
            if self.country_id is not None:
                return self.country.name
            elif self.state_id is not None:
                return self.state.name
            elif self.city_id is not None:
                return self.city.name
            else:
                return 'NONE'


class PostReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    body = db.Column(db.String(400))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Integer)


class CommentReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    body = db.Column(db.String(400))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Integer)


class CommentVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    direction = db.Column(db.Integer) #1 up, 0 down
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class MessageBoard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(140))
    members = db.relationship('User', secondary=MessageBoardAssociations, backref='yyy')
    messages = db.relationship('Message', backref='message', lazy='dynamic')
    last_active = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    recruiting = db.Column(db.Boolean)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'))
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'))
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    activity = db.relationship('MessageBoardActivity', backref='message_board', lazy='dynamic')

    def unread_messages(self, user):
        if self.activity.filter_by(user_id=user.id).first().last_seen < self.last_active:
            return True
        else:
            return False

    def send_message(self, user, message):
        m = Message(message_board_id=self.id, sender_id=user.id, body=message, timestamp=datetime.utcnow())
        db.session.add(m)
        self.last_active = datetime.utcnow()
        a = MessageBoardActivity.query.filter_by(user_id=user.id, message_board_id=self.id).first()
        a.last_seen = datetime.utcnow() + timedelta(seconds=5)
        for m in self.members:
            if m != user:
                if m.is_recruiter:
                    if self.recruiting:
                        if self.candidate_id != None:
                            if self.candidate.status == 1:
                                link = '/p/saved_search/' + str(self.candidate.search_id)
                                t = 5
                                i = int(self.candidate.search_id)
                                n = Notification(user_id=m.id, title='You have received a message!',
                                                 sub_title=str(user.username) + ': ' + message[:100], link=link,
                                                 type=t, specific_id=i)
                                db.session.add(n)
                        else:
                            if self.applicant.status == 1:
                                link = '/p/job_posting/' + str(self.applicant.application.job_id)
                                t = 4
                                i = int(self.applicant.application.job_id)
                                n = Notification(user_id=m.id, title='You have received a message!', sub_title=str(user.username) + ': ' + message[:100], link=link,
                                                 type=t, specific_id=i)
                                db.session.add(n)
                else:
                    if user.is_recruiter:
                        title = 'You have received a message from a recruiter!'
                    else:
                        title = 'You have received a message!'
                    n = Notification(user_id=m.id, title=title, sub_title=str(user.username) + ': ' + message[:100], link='/message/' + str(self.id),
                                     type=0, specific_id=a.id)
                    db.session.add(n)
        db.session.commit()

    def delete_board(self):
        self.members = []
        for message in self.messages:
            message.delete_message()
        for i in self.activity:
            i.delete_activity()
        db.session.delete(self)
        db.session.commit()

    def add_member(self, user):
        if user not in self.members:
            self.members.append(user)

        if MessageBoardActivity.query.filter_by(user_id=user.id, message_board_id=self.id).count() == 0:
            a = MessageBoardActivity(user_id=user.id, message_board_id=self.id,
                                     last_seen=datetime.utcnow() + timedelta(seconds=10))
            db.session.add(a)
        db.session.commit()

    def render_html(self, current=False):
        return render_template('/main/messages/_message_preview_sidebar.html', board=self, current=current)

    def clear_notifications(self, user):
        if user.is_recruiter:
            if self.candidate_id is not None:
                id = 4
            elif self.applicant_id is not None:
                id = 3
        else:
            id = 0
        n = Notification.query.filter_by(type=id, specific_id=self.id, user_id=user.id, read=False).all()
        for i in n:
            i.read = True
        db.session.commit()

    def get_latest_post(self):
        return Message.query.filter_by(message_board_id=self.id).order_by(Message.timestamp.desc()).first()

    def get_messages(self, type=0, start=None):
        if int(type) == 0:
            if start is not None:
                return db.session.query(Message).join(MessageBoard, (MessageBoard.id == Message.message_board_id)).filter(
                    MessageBoard.id == self.id
                ).order_by(Message.timestamp.desc()).all()[int(start):int(start) + 10]
            else:
                return db.session.query(Message).join(MessageBoard,
                                                      (MessageBoard.id == Message.message_board_id)).filter(
                    MessageBoard.id == self.id
                ).order_by(Message.timestamp.desc()).all()

    def recent_messages(self):
        if self.messages.filter(Message.timestamp >= datetime.utcnow() - timedelta(hours=3)).count() > 0:
            return True
        else:
            return False


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_board_id = db.Column(db.Integer, db.ForeignKey('message_board.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    deleted = db.Column(db.Integer,
                        default=0)  # 0 or None (active), 1 deleted by user, 2 deleted by admin, 3 account deleted by user, 4 account deleted by admin
    date_deleted = db.Column(db.DateTime)

    def __repr__(self):
        return '<Message {}>'.format(self.body)

    def edit_message(self, message):
        self.body = message
        db.session.commit()

    def hide_message(self):
        self.deleted = 1
        self.date_deleted = datetime.utcnow()
        db.session.commit()

    def delete_message(self):
        db.session.delete(self)
        db.session.commit()

    def render_html(self):
        return render_template('/main/messages/_message.html', message=self)

class MessageBoardActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message_board_id = db.Column(db.Integer, db.ForeignKey('message_board.id'))
    last_seen = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def delete_activity(self):
        db.session.delete(self)
        db.session.commit()


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), index=True)
    sub_title = db.Column(db.String(128), index=True)
    link = db.Column(db.String(312), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    type = db.Column(db.Integer)
    """
    USER
        0 = New Message (Message Board), -- 
        1 = New Jobs (Job Search), -- 
        2 = Profile Match with Recruiter (Recruiting), --
        360 = User Survey
        
    RECRUITERS
        3 = New Message Applicant (Job Posting), -- 
        4 = New Message Candidate (Saved Search), -- 
        5 = New Candidates Found (Saved Search), 
        6 = New Applicant (Job Posting)
        7 = Edit Applicant (Job Posting), 
        8 = Edit Candidate (Saved Search),
        9 = Added to Search (Saved Search),
        10 = Added to Job Posting (Job Search)
        361 = Recruiter Survey
    """
    specific_id = db.Column(db.Integer)
    read = db.Column(db.Boolean, default=False)

    def mark_read(self):
        self.read = True
        db.session.commit()


class JobLister(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String(140))
    listings = db.relationship('JobListing', backref='lister', lazy='dynamic')
    agency_id = db.Column(db.Integer, db.ForeignKey('recruiting_agency.id'), unique=True)

    def delete(self):
        for job in self.listings:
            job.delete_posting()


class JobListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.Integer, db.ForeignKey('job_lister.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    lat = db.Column(db.Float())
    lon = db.Column(db.Float())
    industries = db.relationship('Industry', secondary=JobIndustryAssociations, backref='xpx')
    searches = db.relationship('JobSavedSearch', secondary=JobListingSSAssociagtions, backref='xlx')
    active = db.Column(db.Boolean, default=True)
    date_found = db.Column(db.DateTime, default=datetime.utcnow)
    date = db.Column(db.DateTime)
    location = db.Column(db.String(100))
    date_no_longer_active = db.Column(db.DateTime)
    job_key = db.Column(db.String(100))
    company = db.Column(db.String(200))
    job_title = db.Column(db.String(200))
    snippet = db.Column(db.String(1000))  # raw HTML
    indeed_url = db.Column(db.String(400))
    apply_url = db.Column(db.String(400))
    activity = db.relationship('JobListingActivity', backref='job', lazy='dynamic')
    notes = db.relationship('JobListingNote', backref='job', lazy='dynamic', order_by='desc(JobListingNote.timestamp)')
    keywords = db.relationship('JobKeyword', secondary=JobKeywordAssociations, backref='job')
    quick_apply = db.relationship('QuickApplyProfile', backref='job', uselist=False)
    recruiters = db.relationship('RecruiterJobAssociation', backref='job', lazy='dynamic')
    recruiter_notes = db.relationship('JobPostingNote', backref='job', lazy='dynamic', order_by='desc(JobPostingNote.timestamp)')


    def add_recruiter(self, recruiter, level):
        if not self.has_recruiter(recruiter):
            a = RecruiterJobAssociation(job_id=self.id, recruiter_id=recruiter.id, last_active=datetime.utcnow(),
                                        level=int(level))
            if self.quick_apply is not None:
                for j in self.quick_apply.applicants:
                    if j.message_board.first() is not None:
                        j.message_board.first().add_member(a.user)
            n = Notification(type=10, specific_id=self.id, link='/p/job_posting/' + str(self.id), user_id=recruiter.user_id,
                             title='You have been added to a Job Posting', sub_title='... ' + str(self.job_title) + ' @ ' +
                             str(self.company), timestamp=datetime.utcnow())
            db.session.add(a)
            db.session.add(n)
            db.session.commit()
            return a
        else:
            return None


    def has_recruiter(self, recruiter):
        if self.recruiters.filter_by(recruiter_id =recruiter.id).count() == 0:
            return False
        else:
            return True

    def get_icons(self):
        return [x.icon for x in self.industries]

    def send_recruiter_messages(self, title, sub, link, type, s_id):
        for i in self.recruiters:
            n = Notification(title=str(title), sub_title=str(sub), link=str(link), user_id=i.recruiter.user_id,
                             type=type, specific_id=s_id)
            db.session.add(n)
        db.session.commit()

    def get_recruiters(self):
        c = self.recruiters.all()
        return [x.recruiter for x in c if x.recruiter.status == 1]

    def get_number_connections(self):
        num = 0
        for i in self.industries:
            num += JobSavedSearch.query.join(JobSearchIndustryAssociations).filter(
                JobSearchIndustryAssociations.c.industry_id == i.id,
                JobSavedSearch.id == JobSearchIndustryAssociations.c.search_id,
            ).count()
        return num

    def get_number_viewed(self):
        return self.activity.filter_by(status=1).count()

    def get_number_applied(self):
        return self.activity.filter_by(status=2).count()

    def delete_posting(self):
        self.industries = []
        self.searches = []
        self.keywords = []
        for i in self.notes:
            db.session.delete(i)
        for j in self.recruiter_notes:
            db.session.delete(j)
        for k in self.activity:
            db.session.delete(k)
        for n in self.recruiters:
            db.session.delete(n)
        db.session.commit()
        if self.quick_apply is not None:
            self.quick_apply.delete_profile()
        db.session.commit()

    def deactivate(self):
        self.active = False
        self.date_no_longer_active = datetime.utcnow()
        db.session.commit()

    def activate(self):
        self.active = True
        self.date_no_longer_active = None
        db.session.commit()

    def get_recruiter_association(self, recruiter):
        return self.recruiters.filter_by(recruiter_id=recruiter.id).first_or_404()

    def clear_notifications(self, user):
        n = Notification.query.filter_by(type=7, specific_id=self.id, user_id=user.id, read=False).all()
        for i in n:
            i.read = True
        db.session.commit()

    def update_recruiter_association(self, recruiter):
        s = RecruiterJobAssociation.query.filter_by(recruiter_id=recruiter.id, job_id=self.id).first()
        s.last_active = datetime.utcnow()
        db.session.commit()

    def get_available_recruiters(self):
        return [x for x in Recruiter.query.filter_by(agency_id=self.lister.agency_id, status=1) if not self.has_recruiter(x)]

    def recently_shared(self, user):
        a = self.get_recruiter_association(user.recruiter)
        if a.level == 3:
            n = Notification.query.filter_by(type=10, user_id=user.id, specific_id=self.id).first()
            if n is None:
                return False
            if n.timestamp >= a.last_active - timedelta(days=1):
                return True
            else:
                return False
        else:
            return False

    def get_creator(self):
        return RecruiterJobAssociation.query.filter_by(job_id=self.id, level=0).first().recruiter


class JobPostingNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    job_id = db.Column(db.Integer, db.ForeignKey('job_listing.id'))
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter.id'))
    timestamp = db.Column(db.DateTime)

    def render_html(self):
        return render_template('/partnership/_posting_note.html', note=self)

    def is_author(self, user):
        if self.recruiter.user == user:
            return True
        else:
            return False

    def edit(self, content):
        self.body = content
        db.session.commit()

    def delete_note(self):
        db.session.delete(self)
        db.session.commit()


class QuickApplyProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_listing.id'), unique=True)
    employment_type_id = db.Column(db.Integer, db.ForeignKey('employment_type.id'))
    compensation_type_id = db.Column(db.Integer, db.ForeignKey('compensation_type.id'))
    compensation_high = db.Column(db.Float)
    compensation_low = db.Column(db.Float)
    pitch = db.Column(db.String(500))  # raw HTML
    applicants = db.relationship('Applicant', backref='application', lazy='dynamic')

    def has_applied(self, user):
        if Applicant.query.filter_by(user_id=user.id, application_id=self.id).count() > 0:
            return True
        else:
            return False

    def apply(self, user, message):
        if not self.has_applied(user):
            a = Applicant.query.filter_by(application_id=self.id).order_by(Applicant.order.desc()).first()
            if a is not None:
                if a.order is not None:
                    num = a.order + 1
                else:
                    num = 1
            else:
                num = 1
            if len(message) == 0:
                m = None
            else:
                m = message
            app = Applicant(user_id=user.id, application_id=self.id, order=num, applied=datetime.utcnow(), specific_message=m, status=1)
            db.session.add(app)
            db.session.commit()
            self.job.send_recruiter_messages(title='Somebody has applied to your job listing...',
                                         sub='...' + str(self.job.job_title) + 'Check it out!',
                                         link='/p/job_posting/' + str(self.job_id),
                                             type=6, s_id=app.id)
            return True
        else:
            return False

    def applicant(self, user):
        return Applicant.query.filter_by(user_id=user.id, application_id=self.id).first()

    def unapply(self, user):
        if self.has_applied(user):
            a = self.applicant(user)
            a.delete_applicant()

    def delete_profile(self):
        for applicant in self.applicants:
            applicant.delete_applicant()
        db.session.delete(self)
        db.session.commit()

    def reorders(self, orders):
        for i in range(len(orders)):
            applicant = Applicant.query.filter_by(application_id=self.id, id=int(orders[i])).first_or_404()
            applicant.order = int(i) + 1
        db.session.commit()

    def get_applicants(self, type=0, start=None, user=None):
        if int(type) == 0:
            if start is not None:
                return self.applicants.filter_by(status=1).order_by(Applicant.order.asc()).all()[int(start): int(start) + 5]
            else:
                return self.applicants.filter_by(status=1).order_by(Applicant.order.asc()).all()
        elif int(type) == 1:
            results = Applicant.query.filter_by(status=1, application_id=self.id).join(
                MessageBoard, (MessageBoard.applicant_id == Applicant.id)
            ).join(
                MessageBoardActivity, (MessageBoardActivity.message_board_id == MessageBoard.id)
            ).filter(
                MessageBoardActivity.user_id == user.id,
                MessageBoard.last_active >= MessageBoardActivity.last_seen
            ).all()
            if start is not None:
                return results[int(start): int(start) + 5]
            else:
                return results
        elif int(type) == 2:
            if start is not None:
                return Applicant.query.filter_by(status=1, application_id=self.id).filter(Applicant.applied >= datetime.utcnow() - timedelta(weeks=1)).order_by(Applicant.applied.desc()).all()[int(start): int(start) + 5]
            else:
                return Applicant.query.filter_by(status=1, application_id=self.id).filter(Applicant.applied >= datetime.utcnow() - timedelta(weeks=1)).order_by(Applicant.applied.desc()).all()

    def reinitiate_applicant(self, applicant_id):
        a = Applicant.query.filter_by(id=applicant_id, application_id=self.id).first_or_404()
        if Applicant.query.filter_by(application_id=self.id, status=1).count() > 0:
            last_order = Applicant.query.filter_by(application_id=self.id, status=1).order_by(
                Applicant.order.desc()).first().order
        else:
            last_order = 0
        a.status = 1
        a.order = int(last_order) + 1
        db.session.commit()

    def remove_applicant(self, applicant_id):
        a = Applicant.query.filter_by(id=applicant_id, application_id=self.id).first_or_404()
        for i in Applicant.query.filter_by(application_id=self.id, status=1).all():
            if i != a:
                if i.order > a.order:
                    i.order -= 1
                    db.session.commit()
        a.status = -1
        db.session.commit()

    def get_removed_applicants(self):
        return self.applicants.filter_by(status=-1).all()

    def get_removed_applicants_html(self):
        html = ''
        if len(self.get_removed_applicants()) > 0:
            for i in self.get_removed_applicants():
                html += render_template('/partnership/_removed_applicant.html', applicant=i)
        else:
            html += '<div class="row" id="no-more-comments"><div class="col-sm-12 no-more-indicator" style="margin-top: 15px; cursor: default">Nothing to show</div></div>'
        return html


class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('quick_apply_profile.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    order = db.Column(db.Integer)
    notes = db.relationship('ApplicantNote', backref='applicant', lazy='dynamic')
    resume_views = db.relationship('ResumeView', backref='applicant', lazy='dynamic')
    applied = db.Column(db.DateTime, default=datetime.utcnow)
    specific_message = db.Column(db.String(500))
    status = db.Column(db.Integer, default=1)
    message_board = db.relationship('MessageBoard', backref='applicant', lazy='dynamic')

    def delete_applicant(self, full=False):
        for note in self.notes:
            db.session.delete(note)
        for a in self.application.applicants:
            if a.order < self.order:
                a.order += 1
        if not full:
            self.application.job.send_recruiter_messages(title=str(self.user.name) + ' has removed their application... ',
                                             sub='... from ' + str(self.application.job.job_title),
                                             link='/p/job_posting/' + str(self.application.job_id),
                                                         type=7, s_id=self.application.job_id)
        db.session.delete(self)
        db.session.commit()

    def render_html(self):
        return render_template('/partnership/_applicant.html', applicant=self)

    def render_html_card(self):
        return render_template('/partnership/_applicant_card.html', applicant=self)

    def clear_notifications(self, user):
        n = Notification.query.filter_by(user_id=user.id, read=False, type=6, specific_id=self.id).all()
        for i in n:
            i.read = True
        db.session.commit()

    def has_notes(self):
        if self.notes.count() > 0:
            return True
        else:
            return False

    def has_messages(self):
        if self.message_board.first() is not None:
            return True
        else:
            return False

    def new_messages(self, user):
        if self.message_board.first() is not None:
            if self.message_board.first().unread_messages(user):
                return True
            else:
                return False
        else:
            return False


class ApplicantNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'))
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter.id'))
    timestamp = db.Column(db.DateTime)

    def render_html(self):
        return render_template('/partnership/_applicant_note.html', note=self)

    def is_author(self, user):
        if self.recruiter.user == user:
            return True
        else:
            return False

    def edit(self, content):
        self.body = content
        db.session.commit()

    def delete_note(self):
        db.session.delete(self)
        db.session.commit()


class EmploymentType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))  # raw HTML
    profiles = db.relationship('QuickApplyProfile', backref='employment', lazy='dynamic')


class CompensationType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))  # raw HTML
    profiles = db.relationship('QuickApplyProfile', backref='compensation', lazy='dynamic')


class JobListingActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('job_saved_search.id'))
    job_id = db.Column(db.Integer, db.ForeignKey('job_listing.id'))
    status = db.Column(db.Integer)
    order = db.Column(db.Integer)

    def render_html(self):
        return render_template('/main/jobs/_job_listing_card.html', job=self)

    def delete_activity(self):
        if self.search_id is not None and self.job_id is not None:
            db.session.delete(self)
            db.session.commit()


class MailActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.Integer)
    """
    99 = account deleted request
    100 = account deleted successful
    0 = confirm email
    1 = registration confirmed
    2 = password reset
    3 = confirm password reset
    4 = confirm new email
    5 = profile update
    6 = 
    7 = report post
    8 = enroll
    9 = unenroll
    10 = partnership approved
    11 = apply for job
    12 = withdraw application
    13 = rsvp event
    14 = unrsvp event
    150 = Mentor Profile Update
    160 = appointment confirmation
    170 = appointment filled
    180 = appointment cancelled -- user
    190 = appointment cacnelled -- mentor
    200 = mentor approved
    210 = mentorship application received
    220 = mentorship application rejected
    215 = mentorship appointment startng (mentor)
    216 = mentorship appointment starting (mentee)
    217 = mentorship appointment followup (mentee)
    218 = event reminder (5 min before)
    501 = User roundup
    502 = Mentor No appointments
    503 = mentor not completed

    
    15 = new applicant
    16 = talent search reactivated
    17 = job reactivated
    18 = talent deactivated
    19 = job deactivated
    20 = talent deleted
    21 = job deleted
    22 = external job added
    23 = quick apply job added
    24 = recruiter created
    25 = approval reminder
    26 = never enrolled recruiting
    27 = candidates found
    28 = partnership rejected
    29 = applicant removed
    30 = shared on search
    31 = shared on job
    50 = custom message
    500 = inactivity reminder
    
    """
    # 0 = confirm email, 1 = registration confirmed, 2 = password reset, 3 = confirm password reset,
    # 4 = confirm new email, 5 = profile update, 6 = new jobs, 7 = report post, 8 = enroll, 9 = un-enroll,
    # 10 = partnership confirm, 11 = partnership confirmed
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('saved_search.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.Integer)
    order = db.Column(db.Integer)
    added = db.Column(db.DateTime)
    notes = db.relationship('CandidateNote', backref='candidate', lazy='dynamic')
    message_board = db.relationship('MessageBoard', backref='candidate', lazy='dynamic')

    def delete(self):
        for note in self.notes:
            db.session.delete(note)
        for message_board in self.message_board:
            db.session.delete(message_board)
        for r in self.search.get_recruiters():
            n = Notification(user_id=r.user_id, link='/p/saved_search/' + str(self.search_id), timestamp=datetime.utcnow(),
                             title=str(self.user.name) + ' has deleted their account', sub_title='They will no longer appear as a candidate in your search.',
                             type=8, specific_id=self.search_id)
            db.session.add(n)
            db.session.commit()
        db.session.delete(self)
        db.session.commit()

    def render_html_card(self):
        return render_template('/partnership/_candidate_card.html', candidate=self)

    def render_html(self):
        return render_template('/partnership/_new_candidate.html', candidate=self)

    def clear_notifications(self, user):
        n = Notification.query.filter_by(user_id=user.id, read=False, type=5, specific_id=self.id).all()
        for i in n:
            i.read = True
        db.session.commit()

    def has_notes(self):
        if self.notes.count() > 0:
            return True
        else:
            return False

    def has_messages(self):
        if self.message_board.first() is not None:
            return True
        else:
            return False

    def new_messages(self, user):
        if self.message_board.first() is not None:
            if self.message_board.first().unread_messages(user):
                return True
            else:
                return False
        else:
            return False


class SavedSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    snippet = db.Column(db.String(500))
    l_specific = db.Column(db.Boolean)
    recruiters = db.relationship('RecruiterSearchAssociation', backref='search', lazy='dynamic')
    industry_id = db.Column(db.Integer, db.ForeignKey('industry.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    experience_id = db.Column(db.Integer, db.ForeignKey('experience.id'))
    status = db.Column(db.Integer)
    candidates = db.relationship('Candidate', backref='search', lazy='dynamic')
    public = db.Column(db.Boolean)
    start = db.Column(db.DateTime, default=datetime.utcnow)
    ended = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)
    resume_views = db.relationship('ResumeView', backref='search', lazy='dynamic')
    notes = db.relationship('SavedSearchNote', backref='search', lazy='dynamic', order_by='desc(SavedSearchNote.timestamp)')
    agency_id = db.Column(db.Integer, db.ForeignKey('recruiting_agency.id'))

    def add_initial_recruiters(self, user, initial=False):
        c = RecruiterSearchAssociation(recruiter_id=user.recruiter.id, search_id=self.id, level=0)
        db.session.add(c)
        if not initial:
            for j in Recruiter.query.filter_by(agency_id=user.recruiter.agency_id, admin=(1 or 2)).all():
                if RecruiterSearchAssociation.query.filter_by(recruiter_id=j.id, search_id=self.id).count() == 0:
                    c = RecruiterSearchAssociation(recruiter_id=j.id, search_id=self.id, level=1)
                    db.session.add(c)
        db.session.commit()

    def apply_results(self):
        added = 0
        def add_candidate(search, c):
            if Candidate.query.filter_by(search_id=search.id, status=1).count() > 0:
                last_order = Candidate.query.filter_by(search_id=search.id, status=1).order_by(
                    Candidate.order.desc()).first().order
            else:
                last_order = 0
            can = Candidate(search_id=search.id, user_id=c.user_id, status=1, order=last_order + 1,
                          added=datetime.utcnow())
            n = Notification(title='Your profile matched with a recruiter search!', sub_title= 'The recruiter search is titled ' + str(search.title),
                             user_id=can.user_id, link='/recruiting', type=2)
            db.session.add(n)
            db.session.add(can)
            db.session.commit()
            for recruiter in search.recruiters:
                n = Notification(user_id=recruiter.recruiter.user_id,
                                 title='Candidates have been found for your search', sub_title=str(search.title),
                                 link='/p/saved_search/' + str(search.id), type=5, specific_id=can.id)
                db.session.add(n)
            db.session.commit()
        if self.l_specific:
            candidates = self.industry.profiles
            for c in candidates:
                if c.user.recruiter_visibility == 3:
                    if Candidate.query.filter_by(user_id=c.user_id, search_id=self.id).count() == 0:
                        if not c.remote:
                            if self.city_id in [x.id for x in c.cities]:
                                add_candidate(self, c)
                                added += 1
                        else:
                            add_candidate(self, c)
                            added += 1
        else:
            candidates = self.industry.profiles
            for c in candidates:
                if c.user.recruiter_visibility == 3:
                    if Candidate.query.filter_by(user_id=c.user_id, search_id=self.id).count() == 0:
                        add_candidate(self, c)
                        added += 1
        return added

    def terminate(self):
        self.status = 0
        self.ended = datetime.utcnow()
        db.session.commit()

    def activate(self):
        self.status = 1
        self.last_updated = datetime.utcnow()
        self.apply_results()

    def reactivate(self):
        self.status = 1
        self.last_updated = datetime.utcnow()
        db.session.commit()

    def agency(self):
        c = self.recruiters.filter_by(level=0).first_or_404()
        return c.recruiter.agency

    def get_recruiters(self):
        c = self.recruiters.all()
        return [x.recruiter for x in c if x.recruiter.status == 1]

    def unseen_notes(self, r_id):
        if self.notes.filter(
                SavedSearchNote.timestamp > RecruiterSearchAssociation.query.filter_by(
                    recruiter_id=r_id).first().last_active).count() > 0:
            return True
        else:
            return False

    def unseen_messages(self, u_id):
        for c in self.candidates:
            if c.message_board.first() is not None:
                if c.message_board.first().last_active > c.message_board.first().activity.filter_by(
                        user_id=u_id).first().last_seen:
                    return True
        return False

    def get_icons(self):
        return self.industry.icon

    def has_recruiter(self, recruiter):
        if self.recruiters.filter_by(recruiter_id =recruiter.id).count() == 0:
            return False
        else:
            return True

    def delete(self):
        for recruiters in self.recruiters:
            db.session.delete(recruiters)
        for candidate in self.candidates:
            candidate.delete()
        for s in self.resume_views:
            db.session.delete(s)
        for x in self.notes:
            db.session.delete(x)
        db.session.commit()

    def get_recruiter_association(self, recruiter):
        return self.recruiters.filter_by(recruiter_id=recruiter.id).first_or_404()

    def reorders(self, orders):
        for i in range(len(orders)):
            candidate = Candidate.query.filter_by(search_id=self.id, id=int(orders[i])).first_or_404()
            candidate.order = int(i) + 1
        db.session.commit()

    def get_candidates(self, type=0, start=None, user=None):
        if int(type) == 0:
            if start is not None:
                return self.candidates.filter_by(status=1).order_by(Candidate.order.asc()).all()[int(start): int(start) + 5]
            else:
                return self.candidates.filter_by(status=1).order_by(Candidate.order.asc()).all()
        elif int(type) == 1:
            results = Candidate.query.filter_by(status=1, search_id=self.id).join(
                    MessageBoard, (MessageBoard.candidate_id == Candidate.id)
                ).join(
                    MessageBoardActivity, (MessageBoardActivity.message_board_id == MessageBoard.id)
                ).filter(
                    MessageBoardActivity.user_id == user.id,
                    MessageBoard.last_active >= MessageBoardActivity.last_seen
                ).all()
            if start is not None:
                return results[int(start): int(start) + 5]
            else:
                return results
        elif int(type) == 2:
            if start is not None:
                return Candidate.query.filter_by(status=1, search_id=self.id).filter(Candidate.added >= datetime.utcnow() - timedelta(weeks=1)).order_by(Candidate.added.desc()).all()[int(start): int(start) + 5]
            else:
                return Candidate.query.filter_by(status=1, search_id=self.id).filter(Candidate.added >= datetime.utcnow() - timedelta(weeks=1)).order_by(Candidate.added.desc()).all()

    def remove_candidate(self, candidate_id):
        c = Candidate.query.filter_by(id=candidate_id, search_id=self.id).first_or_404()
        for i in Candidate.query.filter_by(search_id=self.id, status=1).all():
            if i != c:
                if i.order > c.order:
                    i.order -= 1
                    db.session.commit()
        c.status = -1
        db.session.commit()

    def reinitiate_candidate(self, candidate_id):
        c = Candidate.query.filter_by(id=candidate_id, search_id=self.id).first_or_404()
        if Candidate.query.filter_by(search_id=self.id, status=1).count() > 0:
            last_order = Candidate.query.filter_by(search_id=self.id, status=1).order_by(
                Candidate.order.desc()).first().order
        else:
            last_order = 0
        c.status = 1
        c.order = int(last_order) + 1
        db.session.commit()

    def get_removed_candidates(self):
        return Candidate.query.filter_by(search_id=self.id, status=-1).all()

    def get_removed_candidates_html(self):
        html = ''
        if len(self.get_removed_candidates()) > 0:
            for i in self.get_removed_candidates():
                html += render_template('/partnership/_removed.html', candidate=i)
        else:
            html += '<div class="row" id="no-more-comments"><div class="col-sm-12 no-more-indicator" style="margin-top: 15px; cursor: default">Nothing to show</div></div>'
        return html

    def clear_notifications(self, user):
        n = Notification.query.filter_by(type=8, specific_id=self.id, user_id=user.id, read=False).all()
        for i in n:
            i.read = True
        db.session.commit()

    def update_recruiter_association(self, recruiter):
        s = RecruiterSearchAssociation.query.filter_by(recruiter_id=recruiter.id, search_id=self.id).first()
        s.last_active = datetime.utcnow()
        db.session.commit()

    def get_available_recruiters(self):
        return [x for x in Recruiter.query.filter_by(agency_id=self.agency_id, status=1).all() if not self.has_recruiter(x)]

    def add_recruiter(self, r):
        if not self.has_recruiter(r):
            c = RecruiterSearchAssociation(recruiter_id=r.id, search_id=self.id, level=3)
            for a in self.candidates:
                if a.message_board.first() is not None:
                    a.message_board.first().add_member(r.user)
            n = Notification(type=9, specific_id=self.id, link='/p/saved_search/' + str(self.id),
                             user_id=r.user_id,
                             title='You have been added to a Talent Search',
                             sub_title='... ' + str(self.title), timestamp=datetime.utcnow())
            db.session.add(c)
            db.session.add(n)
            db.session.commit()
            return c
        else:
            return None

    def recently_shared(self, user):
        a = self.get_recruiter_association(user.recruiter)
        if a.level == 3:
            n = Notification.query.filter_by(type=9, user_id=user.id, specific_id=self.id).first()
            if n is None:
                return False
            if n.timestamp >= a.last_active - timedelta(days=1):
                return True
            else:
                return False
        else:
            return False

    def get_creator(self):
        return RecruiterSearchAssociation.query.filter_by(search_id=self.id, level=0).first().recruiter

class ResumeView(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter.id'))
    search_id = db.Column(db.Integer, db.ForeignKey('saved_search.id'))
    applicant_id = db.Column(db.Integer, db.ForeignKey('applicant.id'))
    timestamp = db.Column(db.DateTime)


class SavedSearchNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter.id'))
    search_id = db.Column(db.Integer, db.ForeignKey('saved_search.id'))
    timestamp = db.Column(db.DateTime)

    def render_html(self):
        return render_template('/partnership/_ss_note.html', note=self)

    def is_author(self, user):
        if self.recruiter.user == user:
            return True
        else:
            return False

    def edit(self, content):
        self.body = content
        db.session.commit()

    def delete_note(self):
        db.session.delete(self)
        db.session.commit()


class CandidateNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'))
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter.id'))
    timestamp = db.Column(db.DateTime)

    def render_html(self):
        return render_template('/partnership/_candidate_note.html', note=self)

    def is_author(self, user):
        if self.recruiter.user == user:
            return True
        else:
            return False

    def edit(self, content):
        self.body = content
        db.session.commit()

    def delete_note(self):
        db.session.delete(self)
        db.session.commit()


class RecruiterSearchAssociation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.Integer, db.ForeignKey('saved_search.id'))
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter.id'))
    last_active = db.Column(db.DateTime, default=datetime.utcnow())
    level = db.Column(db.Integer) # 0 -- created, #1 company admins

    def render_html(self):
        return render_template('/partnership/recruiter_preview.html', user=self.recruiter, search=self.search)


class RecruiterJobAssociation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_listing.id'))
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter.id'))
    last_active = db.Column(db.DateTime)
    level = db.Column(db.Integer) # 0 -- created, #1 company admins

    def render_html(self):
        return render_template('/partnership/recruiter_preview.html', user=self.recruiter, search=self.job)



class JobFound(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    testimonial = db.Column(db.Boolean)
    message = db.Column(db.String(150))
    timestamp = db.Column(db.DateTime)


class SuggestedForum(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    forum_id = db.Column(db.Integer, db.ForeignKey('forum.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reason = db.Column(db.Integer)  # 0 = location, 1 = industry, 2 = like you
    status = db.Column(db.Integer, default=0)  # 0 = unmoved, 1 = ignored, 2 = Joined
    timestamp_found = db.Column(db.DateTime, default=datetime.utcnow)

    def render_html(self):
        return render_template('/main/posts/_suggested_forum.html', forum=self)


class JobSSNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    search_id = db.Column(db.Integer, db.ForeignKey('job_saved_search.id'))
    timestamp = db.Column(db.DateTime)

    def render_html(self):
        return render_template('/main/jobs/_note.html', note=self)

    def is_author(self, user):
        if self.search.user == user:
            return True
        else:
            return False

    def edit(self, content):
        self.body = content
        db.session.commit()

    def delete_note(self):
        db.session.delete(self)
        db.session.commit()


class JobListingNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(500))
    job_id = db.Column(db.Integer, db.ForeignKey('job_listing.id'))
    search_id = db.Column(db.Integer, db.ForeignKey('job_saved_search.id'))
    timestamp = db.Column(db.DateTime)

    def render_html(self):
        return render_template('/main/jobs/_job_listing_note.html', note=self)

    def is_author(self, user):
        if self.search.user == user:
            return True
        else:
            return False

    def edit(self, content):
        self.body = content
        db.session.commit()

    def delete_note(self):
        db.session.delete(self)
        db.session.commit()


class JobSavedSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    snippet = db.Column(db.String(140))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    industries = db.relationship('Industry', secondary=JobSearchIndustryAssociations, backref='xvx')
    l_specific = db.Column(db.Boolean)
    proximity_id = db.Column(db.Integer, db.ForeignKey('proximity.id'))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    activities = db.relationship('JobListingActivity', backref='search', lazy='dynamic')
    status = db.Column(db.Integer, default=1)
    jobs = db.relationship('JobListing', secondary=JobListingSSAssociagtions, backref='xvx')
    start = db.Column(db.DateTime, default=datetime.utcnow)
    ended = db.Column(db.DateTime)
    last_updated = db.Column(db.DateTime)
    last_checked = db.Column(db.DateTime)
    notes = db.relationship('JobSSNote', backref='search', lazy='dynamic', order_by='desc(JobSSNote.timestamp)')
    job_notes = db.relationship('JobListingNote', backref='search', lazy='dynamic', order_by='desc(JobListingNote.timestamp)')
    keywords = db.relationship('JobKeyword', secondary=JobSSKeywordAssociations, backref='search')

    def get_first_page_results(self):
        self.update_job_listings_local(num=30)
        q = self.industries
        l = self.city_id
        r = self.proximity
        client = IndeedClient('current_app.config.get('INDEED_API')')
        if l is not None:
            location = self.city.name + ', ' + self.city.state.name
            country = self.city.country.code
            for industry in q:
                initial_params = {
                    'q': industry.title,
                    'l': location,
                    'userip': "1.2.3.4",
                    'useragent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)",
                    'radius': str(r.title.split(' miles')[0]),
                    'limit': '10',
                    'co': country,
                    'filter': '1',
                    'latlong': '1'
                }
                results = client.search(**initial_params)
                for result in results['results']:
                    if JobListing.query.filter_by(job_key=str(result['jobkey']),
                                                  city_id=int(self.city_id)).count() < 1:
                        if not result['expired']:
                            date = datetime.strptime(result['date'].split(' GMT')[0], '%a, %d %b %Y %H:%M:%S')
                            listing = JobListing(city_id=int(self.city_id), snippet=result['snippet'],
                                                 indeed_url=result['url'],
                                                 date=date, location=result['formattedLocationFull'], source=1,
                                                 job_key=result['jobkey'], company=result['company'],
                                                 job_title=result['jobtitle'])
                            if 'latitude' in result.keys() and 'longitude' in result.keys():
                                listing.lat = result['latitude']
                                listing.lon = result['longitude']
                            listing.industries.append(industry)
                            if not result['indeedApply']:
                                job_response = client.jobs(jobkeys=(str(listing.job_key), ''))
                                if len(job_response['results']) > 0:
                                    listing.apply_url = job_response['results'][0]['url']
                            db.session.add(listing)
                            if listing not in self.jobs:
                                self.jobs.append(listing)
                    else:
                        listing = JobListing.query.filter_by(job_key=str(result['jobkey'])).first()
                        if industry not in listing.industries:
                            listing.industries.append(industry)
                        if 'latitude' in result.keys() and 'longitude' in result.keys():
                            listing.lat = result['latitude']
                            listing.lon = result['longitude']
                        if result['expired']:
                            listing.active = False
                            listing.date_no_longer_active = datetime.utcnow()
                        db.session.add(listing)
                        if listing not in self.jobs:
                            self.jobs.append(listing)
                db.session.commit()
        else:
            for industry in q:
                initial_params = {
                    'q': industry.title,
                    'userip': "1.2.3.4",
                    'useragent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2)",
                    'limit': '10',
                    'filter': '1',
                    'latlong': '1'
                }
                results = client.search(**initial_params)
                # print(results, results['results'])
                for result in results['results']:
                    if JobListing.query.filter_by(job_key=str(result['jobkey'])).count() < 1:
                        if not result['expired']:
                            date = datetime.strptime(result['date'].split(' GMT')[0], '%a, %d %b %Y %H:%M:%S')
                            listing = JobListing(snippet=result['snippet'], indeed_url=result['url'],
                                                 date=date, location=result['formattedLocationFull'], source=1,
                                                 job_key=result['jobkey'], company=result['company'],
                                                 job_title=result['jobtitle'])
                            if 'latitude' in result.keys() and 'longitude' in result.keys():
                                listing.lat = result['latitude']
                                listing.lon = result['longitude']
                            listing.industries.append(industry)
                            if not result['indeedApply']:
                                job_response = client.jobs(jobkeys=(str(listing.job_key), ''))
                                if len(job_response['results']) > 0:
                                    listing.apply_url = job_response['results'][0]['url']
                            db.session.add(listing)
                            if listing not in self.jobs:
                                self.jobs.append(listing)
                    else:
                        listing = JobListing.query.filter_by(job_key=str(result['jobkey'])).first()
                        if industry not in listing.industries:
                            listing.industries.append(industry)
                        if 'latitude' in result.keys() and 'longitude' in result.keys():
                            listing.lat = result['latitude']
                            listing.lon = result['longitude']
                        if result['expired']:
                            listing.active = False
                            listing.date_no_longer_active = datetime.utcnow()
                        db.session.add(listing)
                        if listing not in self.jobs:
                            self.jobs.append(listing)

                db.session.commit()

        for job in self.jobs:
            if JobListingActivity.query.filter_by(search_id=self.id, job_id=job.id).count() == 0:
                a = JobListingActivity(job_id=job.id, search_id=self.id, status=0)
                db.session.add(a)
        db.session.commit()

    def update_job_listings_local(self, all=False, num=50):
        added = 0
        q = self.industries
        l = self.city_id
        if self.city_id is not None:
            for industry in q:
                jobs = JobListing.query.join(JobIndustryAssociations).filter(
                    JobIndustryAssociations.c.job_id == JobListing.id,
                    JobIndustryAssociations.c.industry_id == industry.id,
                    JobListing.active == True,
                    JobListing.city_id == l
                ).order_by(JobListing.source.desc()).order_by(JobListing.date.desc()).limit(500).all()
                if not all:
                    jobs = jobs[:num]
                for job in jobs:
                    if job not in self.jobs:
                        added += 1
                        self.jobs.append(job)
        else:
            for industry in q:
                jobs = JobListing.query.join(JobIndustryAssociations).filter(
                    JobIndustryAssociations.c.job_id == JobListing.id,
                    JobIndustryAssociations.c.industry_id == industry.id,
                    JobListing.active == True
                ).order_by(JobListing.source.desc()).order_by(JobListing.date.desc()).limit(500).all()
                if not all:
                    jobs = jobs[:50]
                for job in jobs:
                    if job not in self.jobs:
                        added += 1
                        self.jobs.append(job)
        db.session.commit()
        return added

    def get_icon(self):
        return [i.icon for i in self.industries]

    def get_jobs(self, type=0, start=None):
        if int(type) == 0:
            if start is not None:
                return db.session.query(JobListingActivity).join(JobListing).filter(
                            JobListing.id == JobListingActivity.job_id,
                            JobListingActivity.status >= 0,
                            JobListingActivity.search_id == self.id
                        ).order_by(JobListingActivity.status.desc()).order_by(JobListing.source.desc()).order_by(JobListing.date_found.desc()).all()[int(start):int(start) + 10]
            else:
                return db.session.query(JobListing).join(JobListingActivity).filter(
                    JobListing.id == JobListingActivity.job_id,
                    JobListingActivity.status >= 0,
                    JobListingActivity.search_id == self.id
                ).order_by(JobListingActivity.status.desc())
        else:
            if start is not None:
                return db.session.query(JobListingActivity).join(JobListing).filter(
                            JobListing.id == JobListingActivity.job_id,
                            JobListingActivity.status == int(type),
                            JobListingActivity.search_id == self.id
                        ).order_by(JobListingActivity.status.asc()).order_by(JobListing.date_found.desc()).all()[int(start):int(start) + 10]
            else:
                return db.session.query(JobListing).join(JobListingActivity).filter(
                    JobListing.id == JobListingActivity.job_id,
                    JobListingActivity.status == int(type),
                    JobListingActivity.search_id == self.id
                ).order_by(JobListingActivity.status.asc()).order_by(JobListing.date_found.desc())

    def clear_notifications(self, user):
        n = Notification.query.filter_by(type=1, specific_id=self.id, user_id=user.id, read=False).all()
        for i in n:
            i.read = True
        db.session.commit()

    def get_industry_list(self):
        return [x.id for x in self.industries]

    def terminate(self):
        self.status = 0
        self.ended = datetime.utcnow()
        self.clear_notifications(self.user)
        db.session.commit()

    def delete_search(self):
        if self.status == 0:
            self.industries = []
            self.jobs = []
            self.keywords = []
            for i in self.activities:
                i.delete_activity()
            for i in self.job_notes:
                i.delete_note()
            for i in self.notes:
                i.delete_note()
        db.session.delete(self)
        db.session.commit()

    def render_deactivated_html(self):
        if self.status == 0:
            return render_template('/main/jobs/deactivated_search.html', search=self)
        else:
            return ''

    def reactivate(self):
        if self.status == 0:
            self.status = 1
            self.ended = None
            self.get_first_page_results()
            db.session.commit()

class JobKeyword(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(140))
    jobs = db.relationship('JobListing', secondary=JobKeywordAssociations, backref='keyword')
    searches = db.relationship('JobSavedSearch', secondary=JobSSKeywordAssociations, backref='keyword')


class Employer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(240))
    employees = db.relationship('EmployerAssociations', backref='employer', lazy='dynamic')


class EmployerAssociations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('recruiting_profile.id'))
    employer_id = db.Column(db.Integer, db.ForeignKey('employer.id'))
    job_description = db.Column(db.String(2400))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    is_current = db.Column(db.Boolean)

    def update(self, values):
        self.job_description = values['description']
        self.start = values['start']
        if values['is_current'] == 'false':
            self.end = values['end']
            self.is_current = False
        else:
            self.is_current = True


class Institution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    name = db.Column(db.String(240))
    users = db.relationship('RecruitingProfile', secondary=InstitutionAssociations, backref='institution')


class RecruitingProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    industries = db.relationship('Industry', secondary=ProfileIndustryAssociations, backref='profile')
    remote = db.Column(db.Boolean)
    date_laid_off = db.Column(db.DateTime)
    additional_bio = db.Column(db.String(340))
    linked_in = db.Column(db.String(340))
    cities = db.relationship('City', secondary=ProfileCityAssociations, backref='profile')
    experience_id = db.Column(db.Integer(), db.ForeignKey('experience.id'))
    employers = db.relationship('EmployerAssociations', backref='profile', lazy='dynamic')
    institutions = db.relationship('Institution', secondary=InstitutionAssociations, backref='profile')

    def delete(self):
        self.institutions = []
        self.cities = []
        self.industries = []
        for e in self.employers:
            db.session.delete(e)
        db.session.delete(self)
        db.session.commit()


class DeletedUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(64))
    email = db.Column(db.String(120))
    reason = db.Column(db.String(340))
    timestamp = db.Column(db.DateTime)


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    users = db.relationship('User', secondary=SkillUserAssociations, backref='skill')

    def render_html(self):
        return render_template('main/user_profile_option.html', option=self)


class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    users = db.relationship('User', secondary=InterestUserAssociations, backref='interest')

    def render_html(self):
        return render_template('main/user_profile_option.html', option=self)


class Hobby(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    users = db.relationship('User', secondary=HobbyUserAssociations, backref='hobby')

    def render_html(self):
        return render_template('main/user_profile_option.html', option=self)


class Background(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    users = db.relationship('User', secondary=BackgroundUserAssociations, backref='background')

    def render_html(self):
        return render_template('main/user_profile_option.html', option=self)


class Value(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    users = db.relationship('User', secondary=ValueUserAssociations, backref='value')

    def render_html(self):
        return render_template('main/user_profile_option.html', option=self)


class SpeakerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    title = db.Column(db.String(200))
    linkedin = db.Column(db.String(1000))
    bio = db.Column(db.String(2500))
    img = db.Column(db.String(600))
    events = db.relationship('Event', secondary=SpeakerEventAssociations, backref='speaker')

    def avatar(self):
        return 'https://ilmjtcv-other.s3.us-east-2.amazonaws.com/events/speakers/' + str(self.img) + '.jpg'

    def render_edit_modal(self):
        return render_template('admin/_edit_speaker.html', speaker=self)


class EventRsvp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    checked_in = db.Column(db.DateTime, default=datetime.utcnow)

    def delete_rsvp(self):
        db.session.delete(self)
        db.session.commit()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.String(200))
    title = db.Column(db.String(1000))
    description = db.Column(db.String(5000))
    external_link = db.Column(db.String(200))
    time_start = db.Column(db.DateTime)
    time_end = db.Column(db.DateTime)
    industries = db.relationship('Industry', secondary=EventIndustryAssociations, backref='event')
    speakers = db.relationship('SpeakerProfile', secondary=SpeakerEventAssociations, backref='event')
    rsvps = db.relationship('EventRsvp', backref='event', lazy='dynamic')
    recorded = db.Column(db.Boolean)
    recorded_link = db.Column(db.String(200))
    rewatches = db.relationship('EventRewatch', backref='event', lazy='dynamic')
    invite_sent = db.Column(db.Boolean, default=False)

    def render_preview(self):
        return render_template('main/mentorship/events/_event_card.html', event=self)

    def render_html(self):
        return render_template('main/mentorship/events/_event_modal.html', event=self)

    def get_attachment(self):
        CRLF = "\r\n"
        organizer = "ORGANIZER;CN=ILMJTCV Exclusive Events:mailto:support" + CRLF + " @ilmjtcv.com"

        ddtstart = self.time_start
        dur = self.time_end - self.time_start
        dtend = ddtstart + dur
        dtstamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        dtstart = ddtstart.strftime("%Y%m%dT%H%M%SZ")
        dtend = dtend.strftime("%Y%m%dT%H%M%SZ")

        description = "DESCRIPTION:" + self.description + ". Please add this invitation to your calendar and be ready to join the zoom meeting 5 minutes prior to the session's start time. " + CRLF
        attendee = ""
        ical = "BEGIN:VCALENDAR" + CRLF + "PRODID:" + str(
            self.id) + CRLF + "VERSION:2.0" + CRLF + "CALSCALE:GREGORIAN" + CRLF
        ical += "METHOD:REQUEST" + CRLF + "BEGIN:VEVENT" + CRLF + "DTSTART:" + dtstart + CRLF + "DTEND:" + dtend + CRLF + "DTSTAMP:" + dtstamp + CRLF + organizer + CRLF
        ical += "UID:FIXMEUID" + dtstamp + CRLF
        ical += attendee + "CREATED:" + dtstamp + CRLF + description + "LAST-MODIFIED:" + dtstamp + CRLF + "LOCATION:" + CRLF + "SEQUENCE:0" + CRLF + "STATUS:CONFIRMED" + CRLF + 'URL:' + 'https://ilmjtcv.com/events?event=' + str(
            self.id) + CRLF
        ical += "SUMMARY:ILMJTCV Exclusive Event: " + self.title + ' with ' + self.speakers[0].name + CRLF + "TRANSP:OPAQUE" + CRLF + "END:VEVENT" + CRLF + "END:VCALENDAR" + CRLF
        title = 'invite_' + str(self.id)
        path = 'app/static/uploads/ical/' + title + '.ics'
        os.makedirs('app/static/uploads/ical', exist_ok=True)
        file1 = open(path, "wb+")
        file1.write(ical.encode('utf-8'))
        file1.close()
        return path

    def avatar(self):
        return 'https://ilmjtcv-other.s3.us-east-2.amazonaws.com/events/' + self.img + '.jpg'

    def get_end(self):
        return self.time_end.strftime('%Y-%m-%dT%H:%M')

    def get_start(self):
        return self.time_start.strftime('%Y-%m-%dT%H:%M')

    def get_speakers(self):
        return [i.id for i in self.speakers]

    def get_industries(self):
        if len(self.industries) > 0:
            return [i.id for i in self.industries]
        else:
            return [0]

    def has_passed(self):
        if self.time_end <= datetime.utcnow():
            return True
        else:
            return False

    def get_similar(self):
        return Event.query.filter(Event.id != self.id).order_by(Event.time_start.desc()).first()

    def responded(self, user):
        if self.rsvps.filter_by(user_id=user.id).count() > 0:
            return True
        else:
            return False

    def unrsvp(self, user):
        e = EventRsvp.query.filter_by(user_id=user.id, event_id=self.id).first()
        if e is not None:
            db.session.delete(e)
            db.session.commit()

    def rsvp(self, user):
        if self.responded(user):
            self.unrsvp(user)
            return False
        else:
            e = EventRsvp(user_id=user.id, event_id=self.id, timestamp=datetime.utcnow(), checked_in=False)
            db.session.add(e)
            db.session.commit()
            return True

    def check_in(self, user):
        if not self.responded(user):
            self.rsvp(user)
        a = self.rsvps.filter_by(user_id=user.id).first()
        a.checked_in = datetime.utcnow()
        db.session.commit()

    def add_watch(self, user):
        s = EventRewatch(user_id=user.id, event_id=self.id, timestamp=datetime.utcnow())
        db.session.add(s)
        db.session.commit()

    def delete_event(self):
        self.industries = []
        self.speakers = []
        for rewatch in self.rewatches.all():
            rewatch.delete_rewatch()
        for rsvp in self.rsvps.all():
            rsvp.delete_rsvp()
        db.session.delete(self)
        db.session.commit()

    def ongoing(self):
        if self.time_start - timedelta(minutes=5) >= datetime.utcnow():
            print('pre')
        if self.time_end + timedelta(minutes=5) >= datetime.utcnow():
            print('post')
        if self.time_start - timedelta(minutes=5) <= datetime.utcnow() and self.time_end + timedelta(minutes=5) >= datetime.utcnow():
            return True
        else:
            return False


class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    authors = db.relationship('User', secondary=BlogAuthorAssociations, backref='blog')
    title = db.Column(db.String(200))
    snippet = db.Column(db.String(200))
    html_path = db.Column(db.String(100))
    posted = db.Column(db.DateTime, default=datetime.utcnow)
    img = db.Column(db.String(600))
    meta_img = db.Column(db.String(600))

    def avatar(self):
        return url_for('static', filename='images/articles/' + self.img)

    def avatar_meta(self):
        return url_for('static', filename='images/articles/' + self.meta_img)

    def render_preview(self):
        return render_template('main/mentorship/blog/_preview_card.html', blog=self)

    def render_html(self):
        return render_template(self.html_path)

    def get_authors(self):
        if(len(self.authors)) == 1:
            return self.authors[0].name
        else:
            names = ''
            for a in range(len(self.authors)):
                names += self.authors[a].name.split(' ')[0]
                if a + 1 < len(self.authors):
                    names += ', '
            return names


class ExclusivePartner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    description = db.Column(db.String(1000))
    img = db.Column(db.String(1000))
    cover_img = db.Column(db.String(1000))
    html_path = db.Column(db.String(100))
    posted = db.Column(db.DateTime, default=datetime.utcnow)
    link = db.Column(db.String(100))
    clicks = db.relationship('PartnerClicks', backref='partner', lazy='dynamic')

    def render_preview(self):
        return render_template('main/mentorship/partners/_partner_card.html', partner=self)

    def avatar(self):
        return url_for('static', filename='images/partners/' + self.img)

    def avatar_cover(self):
        return url_for('static', filename='images/partners/' + self.cover_img)

    def render_html(self):
        return render_template('main/mentorship/partners/partnerships/' + self.html_path + '.html', partner=self)


class PartnerClicks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('exclusive_partner.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class EventRewatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def delete_rewatch(self):
        db.session.delete(self)
        db.session.commit()


class CustomEmail (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(10000))
    button_text = db.Column(db.String(100))
    button_link = db.Column(db.String(1000))
    header_text = db.Column(db.String(100))
    prefix = db.Column(db.String(50))
    subject = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Integer)
    audience = db.Column(db.Integer)  #0  == All Recruiters,  #1 == All Users

    def get_audience(self):
        if self.audience == 0:
            return User.query.filter_by(is_recruiter=True, unsubscribed=False).all()
        elif self.audience == 1:
            return User.query.filter_by(is_recruiter=False, unsubscribed=False).all()
        elif self.audience == 2:
            return User.query.filter_by(admin=True).all()
        elif self.audience == 3:
            return db.session.query(User).join(MentorProfile, (MentorProfile.user_id == User.id)).filter(
                MentorProfile.status == 1,
                User.unsubscribed == False
            ).all()


    def get_sending_confirmation_token(self, expires_in=604800):
        return jwt.encode(
            {'email_confirmation': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


    @staticmethod
    def verify_sending_confirmation_token(token):
        try: id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['email_confirmation']
        except:
            return
        return CustomEmail.query.get(id)

    def render_edit_html(self):
        return render_template('admin/_edit_email.html', email=self)

    def delete_email(self):
        db.session.delete(self)
        db.session.commit()


class MentorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    appointments = db.relationship('Appointment', backref='mentor', lazy='dynamic')
    bio = db.Column(db.String(1000))
    ratings = db.relationship('MentorRating', backref='mentor', lazy='dynamic')
    notes = db.relationship('MentorNote', backref='mentor', lazy='dynamic')
    zoom_link = db.Column(db.String(1000))
    zoom_password = db.Column(db.String(1000))
    linked_in = db.Column(db.String(1000))
    status = db.Column(db.Integer, default=0)
    why = db.Column(db.String(1000))

    def get_rating(self):
        total = 0
        for i in self.ratings.all():
            total += i.rating
        if self.ratings.count() > 0:
            return total / int(self.ratings.count())
        else:
            return 5
    def get_completed_appointments(self):
        return db.session.query(Appointment).join(AppointmentParticipantAssociations, (AppointmentParticipantAssociations.c.appointment_id == Appointment.id)).filter(
            Appointment.mentor_id == self.id,
            Appointment.end_time <= datetime.utcnow()
        ).count()
    def delete_mentor_profile(self):
        for appointment in self.appointments:
            appointment.delete_appointment()
        for rating in self.ratings:
            rating.delete_rating()
        for note in self.notes:
            note.delete_note()
        db.session.delete(self)
        db.session.commit()


class MentorRating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor_profile.id'))
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    rating = db.Column(db.Float)
    timestamp = db.Column(db.DateTime)

    def delete_rating(self):
        db.session.delete(self)
        db.session.commit()


class MenteeNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    note = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime)

    def render_html(self):
        return render_template('main/mentorship/sessions/participant/_note.html', note=self)

    def delete_note(self):
        db.session.delete(self)
        db.session.commit()


class MentorNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor_profile.id'))
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    note = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime)

    def render_html(self):
        return render_template('main/mentorship/sessions/mentor/_note.html', note=self)

    def delete_note(self):
        db.session.delete(self)
        db.session.commit()


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mentor_id = db.Column(db.Integer, db.ForeignKey('mentor_profile.id'))
    participants = db.relationship('User', secondary=AppointmentParticipantAssociations, backref='appointment')
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.Integer, default=0)
    ratings = db.relationship('MentorRating', backref='appointment', lazy='dynamic')
    mentee_notes = db.relationship('MenteeNote', backref='appointment', lazy='dynamic', order_by='desc(MenteeNote.timestamp)')
    notes = db.relationship('MentorNote', backref='appointment', lazy='dynamic', order_by='desc(MentorNote.timestamp)')
    message_board = db.relationship('MessageBoard', backref='appointment', uselist=False)
    follow_up_sent = db.Column(db.Boolean, default=False)
    check_in_sent = db.Column(db.Boolean, default=False)

    def is_mentor(self, user):
        if user == self.mentor.user:
            return True
        else:
            return False

    def join_time(self):
        if datetime.utcnow() < self.end_time:
            if datetime.utcnow() + timedelta(minutes=5) >= self.start_time:
                return True
        else:
            return False

    def get_zoom_link(self):
        return self.mentor.zoom_link

    def get_zoom_password(self):
        if self.mentor.zoom_password is None:
            return None
        else:
            return self.mentor.zoom_password

    def get_rating_modal(self):
        return render_template('main/mentorship/sessions/participant/session_rating.html', appointment=self)

    def render_html_modal(self):
        if not self.enough_time_start(0):
            return render_template('main/mentorship/sessions/mentor/_post_edit_session_modal.html', appointment=self)
        else:
            return render_template('main/mentorship/sessions/mentor/_edit_session_modal.html', appointment=self)

    def get_rating(self, user):
        return MentorRating.query.filter_by(appointment_id=self.id, user_id=user.id).first()

    def render_html_modal_mentee(self):
        return render_template('main/mentorship/sessions/participant/session_modal.html', appointment=self)

    def get_notes(self, start):
        return MentorNote.query.filter_by(appointment_id=self.id).order_by(
            MentorNote.timestamp.desc()).all()[start: start + 10][::-1]

    def get_mentee_notes(self, start):
        return MenteeNote.query.filter_by(appointment_id=self.id).order_by(
            MenteeNote.timestamp.desc()).all()[start: start + 10][::-1]

    def add_note(self, q, user):
        if user == self.mentor.user:
            n = MentorNote(mentor_id=user.mentor_profile.id, appointment_id=self.id, note=q, timestamp=datetime.utcnow())
        else:
            n = MenteeNote(user_id=user.id, appointment_id=self.id, note=q, timestamp=datetime.utcnow())
        db.session.add(n)
        db.session.commit()

    def has_participant(self):
        if len(self.participants) > 0:
            return True
        else:
            return False

    def unregister(self, user):
        if user in self.participants:
            self.participants.remove(user)
            self.message_board.delete_board()
            db.session.commit()
            return True
        else:
            return False

    def sign_up(self, user):
        if not self.has_participant():
            self.participants.append(user)
            self.status = 1
            m = MessageBoard(subject='Mentorship Session: ' + user.name, last_active=datetime.utcnow(),
                             appointment_id=self.id)
            db.session.add(m)
            m.add_member(user)
            m.add_member(self.mentor.user)
            db.session.commit()
            m.send_message(self.mentor.user, 'Hi, my name is ' + self.mentor.user.name + ' and I am excited to meet you during our mentorship session!')
            return True
        else:
            return False

    def delete_appointment(self):
        self.participants = []
        for note in self.notes.all():
            note.delete_note()
        if self.message_board is not None:
            self.message_board.delete_board()
        for rating in self.ratings.all():
            rating.delete_rating()
        db.session.delete(self)
        db.session.commit()

    def enough_time_start(self, min):
        if self.start_time - timedelta(minutes=int(min)) >= datetime.utcnow():
            return True
        else:
            return False

    def enough_time_end(self):
        if self.end_time <= datetime.utcnow():
            return True
        else:
            return False

    def render_upcoming_preview(self):
        return render_template('main/mentorship/sessions/mentor/_upcoming.html', appointment=self)

    def render_upcoming_preview_mentee(self):
        return render_template('main/mentorship/sessions/participant/_upcoming.html', appointment=self)

    def render_past_preview(self):
        return render_template('main/mentorship/sessions/mentor/_upcoming.html', appointment=self)

    def render_past_preview_mentee(self):
        return render_template('main/mentorship/sessions/participant/_past.html', appointment=self)

    def render_messages_board(self):
        return render_template('main/mentorship/sessions/mentor/participant_conversation.html', appointment=self)

    def render_notes_board(self):
        return render_template('main/mentorship/sessions/mentor/participant_notes.html', appointment=self)

    def render_notes_board_mentee(self):
        return render_template('main/mentorship/sessions/participant/participant_notes.html', appointment=self)

    def get_attachment(self):
        CRLF = "\r\n"
        attendees = [user.email for user in self.participants]
        attendees.append(self.mentor.user.email)
        organizer = "ORGANIZER;CN=ILMJTCV Mentorship:mailto:support" + CRLF + " @ilmjtcv.com"

        ddtstart = self.start_time
        dur = timedelta(minutes=30)
        dtend = ddtstart + dur
        dtstamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        dtstart = ddtstart.strftime("%Y%m%dT%H%M%SZ")
        dtend = dtend.strftime("%Y%m%dT%H%M%SZ")

        description = "DESCRIPTION:This is a mentorship appointment for " + self.participants[0].name + ' with ' + self.mentor.user.name + ". Please add this invitation to your calendar and be ready to join the zoom meeting 5 minutes prior to the session's start time. "+ CRLF
        attendee = ""
        for att in attendees:
            attendee += "ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-    PARTICIPANT;PARTSTAT=ACCEPTED;RSVP=TRUE" + CRLF + " ;CN=" + att + ";X-NUM-GUESTS=0:" + CRLF + " mailto:" + att + CRLF
        ical = "BEGIN:VCALENDAR" + CRLF + "PRODID:" + str(self.id) + CRLF + "VERSION:2.0" + CRLF + "CALSCALE:GREGORIAN" + CRLF
        ical += "METHOD:REQUEST" + CRLF + "BEGIN:VEVENT" + CRLF + "DTSTART:" + dtstart + CRLF + "DTEND:" + dtend + CRLF + "DTSTAMP:" + dtstamp + CRLF + organizer + CRLF
        ical += "UID:FIXMEUID" + dtstamp + CRLF
        ical += attendee + "CREATED:" + dtstamp + CRLF + description + "LAST-MODIFIED:" + dtstamp + CRLF + "LOCATION:" + CRLF + "SEQUENCE:0" + CRLF + "STATUS:CONFIRMED" + CRLF + 'URL:' + 'https://ilmjtcv.com/appointment_check_in/' + str(self.id) + CRLF
        ical += "SUMMARY:ILMJTCV Mentorship Appointment" + CRLF + "TRANSP:OPAQUE" + CRLF + "END:VEVENT" + CRLF + "END:VCALENDAR" + CRLF
        title = 'invite_' + str(self.id)
        path = 'app/static/uploads/ical/' + title + '.ics'
        os.makedirs('app/static/uploads/ical', exist_ok=True)
        file1 = open(path, "w")
        file1.write(ical)
        file1.close()
        return path

    def get_cancelled_attachment(self):
        CRLF = "\r\n"
        attendees = [user.email for user in self.participants]
        attendees.append(self.mentor.user.email)
        organizer = "ORGANIZER;CN=ILMJTCV Mentorship:mailto:support" + CRLF + " @ilmjtcv.com"

        ddtstart = self.start_time
        dur = timedelta(minutes=30)
        dtend = ddtstart + dur
        dtstamp = datetime.now().strftime("%Y%m%dT%H%M%SZ")
        dtstart = ddtstart.strftime("%Y%m%dT%H%M%SZ")
        dtend = dtend.strftime("%Y%m%dT%H%M%SZ")

        description = "DESCRIPTION: Unfortunately the mentorship appointment that you had for this time slot was cancelled."+ CRLF
        attendee = ""
        for att in attendees:
            attendee += "ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-    PARTICIPANT;PARTSTAT=REJECTED;RSVP=FALSE" + CRLF + " ;CN=" + att + ";X-NUM-GUESTS=0:" + CRLF + " mailto:" + att + CRLF
        ical = "BEGIN:VCALENDAR" + CRLF + "PRODID:" + str(self.id) + CRLF + "VERSION:2.0" + CRLF + "CALSCALE:GREGORIAN" + CRLF
        ical += "METHOD:REQUEST" + CRLF + "BEGIN:VEVENT" + CRLF + "DTSTART:" + dtstart + CRLF + "DTEND:" + dtend + CRLF + "DTSTAMP:" + dtstamp + CRLF + organizer + CRLF
        ical += "UID:FIXMEUID" + dtstamp + CRLF
        ical += attendee + "CREATED:" + dtstamp + CRLF + description + "LAST-MODIFIED:" + dtstamp + CRLF + "LOCATION:" + CRLF + "SEQUENCE:0" + CRLF + "STATUS:CONFIRMED" + CRLF
        ical += "SUMMARY:CANCELLED: ILMJTCV Mentorship Appointment" + CRLF + "TRANSP:OPAQUE" + CRLF + "END:VEVENT" + CRLF + "END:VCALENDAR" + CRLF
        title = 'invite_' + str(self.id)
        path = 'app/static/uploads/ical/' + title + '.ics'
        os.makedirs('app/static/uploads/ical', exist_ok=True)
        file1 = open(path, "w")
        file1.write(ical)
        file1.close()
        return path

    def get_join_modal(self):
        return render_template('main/mentorship/sessions/participant/join_session.html', appointment=self)

    def add_rating(self, score, user):
        r = MentorRating(appointment_id=self.id, user_id=user.id, mentor_id=self.mentor.id, rating=score, timestamp=datetime.utcnow())
        self.status = 3
        db.session.add(r)
        db.session.commit()

class NewsArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.String(200))
    link = db.Column(db.String(1000))
    img = db.Column(db.String(200))
    added = db.Column(db.DateTime, default=datetime.utcnow)

    def avatar(self):
        return 'https://ilmjtcv-other.s3.us-east-2.amazonaws.com/news/' + self.img

    def render_html(self):
        return render_template('_news_article.html', news=self)

    def render_edit_modal(self):
        return render_template('admin/_edit_news.html', news=self)

    def delete_news(self):
        db.session.delete(self)
        db.session.commit()


