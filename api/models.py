# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import datetime
from email.policy import default

import json

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Users(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    password = db.Column(db.Text())
    jwt_auth_active = db.Column(db.Boolean())
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"User {self.username}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def update_email(self, new_email):
        self.email = new_email

    def update_username(self, new_username):
        self.username = new_username

    def check_jwt_auth_active(self):
        return self.jwt_auth_active

    def set_jwt_auth_active(self, set_status):
        self.jwt_auth_active = set_status
    
    def delete_user(self):
        self.deleted = True

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def toDICT(self):

        cls_dict = {}
        cls_dict['_id'] = self.id
        cls_dict['username'] = self.username
        cls_dict['email'] = self.email

        return cls_dict

    def toJSON(self):
        return self.toDICT()


class JWTTokenBlocklist(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    jwt_token = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)

    def __repr__(self):
        return f"Expired Token: {self.jwt_token}"

    def save(self):
        db.session.add(self)
        db.session.commit()

class Project(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    project_name = db.Column(db.String(32), nullable=False)
    number_of_issues = db.Column(db.Integer(), default=0, nullable=False)
    created_by = db.Column(db.Integer(), db.ForeignKey(Users.id), nullable=False)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False, nullable=False)


    def __repr__(self):
        return f"Project {self.project_name}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_project_name(self, project_name):
        self.project_name = project_name

    def increment_issue_count(self):
        self.number_of_issues += 1
    
    def decrement_issue_count(self):
        if self.number_of_issues > 0:
            self.number_of_issues -= 1
        
    def update_username(self, new_username):
        self.username = new_username

    def delete_project(self):
        self.deleted = True
        related_issues = db.session.query(Issue.id).filter.by(project=self.id)
        for issue_id in related_issues:
            Issue.get_by_id(issue_id).delete_issue()
            
    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def toDICT(self):

        cls_dict = {}
        cls_dict['_id'] = self.id
        cls_dict['project_name'] = self.project_name
        cls_dict['number_of_issues'] = self.number_of_issues

        return cls_dict

    def toJSON(self):
        return self.toDICT()

class Issue(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    issue_title = db.Column(db.String(32), nullable=False)
    issue_type = db.Column(db.String(16), nullable=False)
    issue_status = db.Column(db.String(16), nullable=False)
    parent_project = db.Column(db.Integer(), db.ForeignKey(Project.id), nullable=False)
    created_by = db.Column(db.Integer(), db.ForeignKey(Users.id), nullable=False)
    date_created = db.Column(db.DateTime(), default=datetime.utcnow)
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"Project {self.project_name}"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_issue_title(self, issue_title):
        self.issue_title = issue_title
    
    def set_issue_type(self, issue_type):
        self.issue_type = issue_type
    
    def set_issue_status(self, issue_status):
        self.issue_status = issue_status

    def update_parent_project(self, project_id):
        self.parent_project = project_id
    
    def delete_issue(self):
        self.deleted = True
        Project.get_by_id(self.parent_project).decrement_issue_count()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)

    def toDICT(self):

        cls_dict = {}
        cls_dict['_id'] = self.id
        cls_dict['issue_title'] = self.issue_title
        cls_dict['issue_type'] = self.issue_type
        cls_dict['issue_status'] = self.issue_status
        cls_dict['parent_project'] = self.parent_project

        return cls_dict

    def toJSON(self):

        return self.toDICT()