# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from datetime import datetime, timezone, timedelta

from functools import wraps

from flask import request
from flask_restx import Api, Resource, fields

import jwt

from .models import db, Users, JWTTokenBlocklist, Project, Issue
from .config import BaseConfig

rest_api = Api(version='1.0', title='Gira API')
users_api = rest_api.namespace('Users Endpoints', path='/api/users', description='Api endpoints for user related operations')
project_api = rest_api.namespace('Project Endpoints', path='/api/project', description='Api endpoints for project related operations')
issue_api = rest_api.namespace('Issue Endpoints', path='/api/issue', description='Api endpoints for issue related operations')


'''
    Flask-Restx Users models for api request and response data
'''

signup_model = users_api.model('SignUpModel', {"username": fields.String(required=True, min_length=2, max_length=32),
                                              "email": fields.String(required=True, min_length=4, max_length=64),
                                              "password": fields.String(required=True, min_length=4, max_length=16)
                                              })

login_model = users_api.model('LoginModel', {"email": fields.String(required=True, min_length=4, max_length=64),
                                            "password": fields.String(required=True, min_length=4, max_length=16)
                                            })

user_edit_model = users_api.model('UserEditModel', {"userID": fields.String(required=True, min_length=1, max_length=32),
                                                   "username": fields.String(required=False, min_length=2, max_length=32),
                                                   "email": fields.String(required=False, min_length=4, max_length=64),
                                                   "password": fields.String(required=False, min_length=4, max_length=16)
                                                   })

'''
    Flask-Restx Project models for api request and response data
'''

project_create_model = project_api.model('ProjectCreateModel', {"project_name": fields.String(required=True, min_length=1, max_length=32)})

project_view_model = project_api.model('ProjectViewModel', {"projectID": fields.String(required=True, min_length=1, max_length=32)})

project_edit_model = project_api.model('ProjectEditModel', {"projectID": fields.String(required=True, min_length=1, max_length=32),
                                                         "project_name": fields.String(required=True, min_length=1, max_length=32)
                                                         })

project_delete_model = project_api.model('ProjectDeleteModel', {"projectID": fields.String(required=True, min_length=1, max_length=32)})

'''
    Flask-Restx Issue models for api request and response data
'''

issue_create_model = issue_api.model('IssueCreateModel', {"issue_title": fields.String(required=True, min_length=1, max_length=32),
                                                          "issue_type": fields.String(required=True, enum=('Bug', 'Improvement', 'Feature')),
                                                          "parent_project": fields.String(required=True, min_length=1, max_length=32)
                                                         })

issue_view_model = issue_api.model('IssueViewModel', {"issueID": fields.String(required=True, min_length=1, max_length=32)})

issue_edit_model = issue_api.model('IssueEditModel', {"issueID": fields.String(required=True, min_length=1, max_length=32),
                                                      "issue_title": fields.String(required=False, min_length=1, max_length=32),
                                                      "issue_type": fields.String(required=False, enum=('Bug', 'Improvement', 'Feature')),
                                                      "issue_status": fields.String(required=False, enum=('To Do', 'In Progress', 'Done')),
                                                      "parent_project": fields.String(required=False, min_length=1, max_length=32)
                                                      })

issue_delete_model = issue_api.model('IssueDeleteModel', {"issueID": fields.String(required=True, min_length=1, max_length=32)})

'''
   Helper function for JWT token required
'''

def token_required(f):

    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'authorization' in request.headers:
            token = request.headers["authorization"]

        if not token:
            return {"success": False, "msg": "Valid JWT token is missing"}, 400

        try:
            data = jwt.decode(token, BaseConfig.SECRET_KEY, algorithms=["HS256"])
            current_user = Users.get_by_email(data["email"])

            if not current_user:
                return {"success": False,
                        "msg": "Sorry. Wrong auth token. This user does not exist."}, 400

            token_expired = db.session.query(JWTTokenBlocklist.id).filter_by(jwt_token=token).scalar()

            if token_expired is not None:
                return {"success": False, "msg": "Token revoked."}, 400

            if not current_user.check_jwt_auth_active():
                return {"success": False, "msg": "Token expired."}, 400

        except:
            return {"success": False, "msg": "Token is invalid"}, 400

        return f(current_user, *args, **kwargs)

    return decorator


'''
    Flask-Restx Users API routes
'''

@users_api.route('/register')
class Register(Resource):
    '''
       Creates a new user by taking 'signup_model' input
    '''

    @users_api.expect(signup_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _username = req_data.get('username')
        _email = req_data.get('email')
        _password = req_data.get('password')

        email_exists = Users.get_by_email(_email)
        username_exists = Users.get_by_username(_username)
        if email_exists:
            return {"success": False,
                    "msg": "Email already taken"}, 400
        elif username_exists:
            return {"success": False,
                    "msg": "Username already taken"}, 400
        else:
            new_user = Users(username=_username, email=_email)

            new_user.set_password(_password)
            new_user.save()
            rest_api.logger.info('Registered User Successfully ')
            return {"success": True,
                    "userID": new_user.id,
                    "msg": "The user was successfully registered"}, 200

@users_api.route('/login')
class Login(Resource):
    '''
       Login user by taking 'login_model' input and return JWT token
    '''

    @users_api.expect(login_model, validate=True)
    def post(self):

        req_data = request.get_json()

        _email = req_data.get('email')
        _password = req_data.get('password')

        user = Users.get_by_email(_email)

        if not user:
            return {"success": False,
                    "msg": "This email does not exist."}, 400

        if not user.check_password(_password):
            return {"success": False,
                    "msg": "Wrong credentials."}, 400

        # create access token uwing JWT
        token = jwt.encode({"email": _email, "exp": datetime.utcnow() + timedelta(minutes=30)}, BaseConfig.SECRET_KEY)

        user.set_jwt_auth_active(True)
        user.save()

        return {"success": True,
                "token": token,
                "user": user.toJSON()}, 200

@users_api.route('/edit')
class EditUser(Resource):
    '''
       Edits User's username or password or both using 'user_edit_model' input
    '''

    @users_api.expect(user_edit_model)
    @token_required
    def post(self, current_user):

        req_data = request.get_json()

        _new_username = req_data.get('username')
        _new_email = req_data.get('email')
        _new_password = req_data.get('password')

        if _new_username or _new_email or _new_password:
            success_msg = 'Successfully updated '       
            if _new_username:
                new_username_exists = Users.get_by_username(_new_username)
                if new_username_exists:
                    return {"success": False,
                            "msg": "Username already taken"}, 400
                else:
                    self.update_username(_new_username)
                    success_msg = success_msg + 'username '

            if _new_email:
                new_email_exists = Users.get_by_email(_new_email)
                if new_email_exists:
                        return {"success": False,
                        "msg": "Email already taken"}, 400
                else:
                    self.update_email(_new_email)
                    success_msg = success_msg + 'email '

            if _new_password:
                self.set_password(_new_password)
                success_msg = success_msg + 'password '

            self.save()
        else:
            success_msg = 'Nothing to update' 

        return {"success": True,
                "user": self.toJSON(),
                "msg": success_msg}, 200

@users_api.route('/logout')
class LogoutUser(Resource):
    '''
        Logs out the currently logged in User 
    '''
    
    @token_required
    def post(self, current_user):

        _jwt_token = request.headers["authorization"]

        jwt_block = JWTTokenBlocklist(jwt_token=_jwt_token, created_at=datetime.now(timezone.utc))
        jwt_block.save()

        self.set_jwt_auth_active(False)
        self.save()

        return {"success": True,
                "msg": "Successfully logged out the user"}, 200

'''
    Flask-Restx Project API routes
'''

@project_api.route('/create')
class CreateProject(Resource):
    '''
        Creates a new project using 'ProjectCreateModel' input
    '''

    @project_api.expect(project_create_model, validate=True)
    @token_required
    def post(self, current_user):

        req_data = request.get_json()

        _project_name = req_data.get('project_name')

        project_exists = Project.get_by_name(_project_name, self.id)

        if project_exists:
            return {"success": False,
                    "msg": "A project with the same name already exists"}, 400
        new_project = Project(project_name = _project_name, created_by=self.id)
        new_project.save()

        return {"success": True,
                "projectID": new_project.id,
                "project_name": new_project.project_name,
                "created_by": new_project.created_by,
                "msg": "Project successfully created"}, 200
        
@project_api.route('/listall')
class ListAllProjects(Resource):
    '''
        Lists all projects that a user created
    '''

    @token_required
    def get(self, current_user):
        project_list = Project.get_by_cerator(self.id)
        projects_to_return = []
        for proj in project_list:
            projects_to_return.append(proj.toJSON())
        if len(projects_to_return) == 0:
            return {"success": True,
                "projects": [],
                "msg": "There are no projects to return"}, 200
        return {"success": True,
                "projects": projects_to_return,
                "msg": "Projects of the current user successfully listed"}, 200

@project_api.route('/view')
class ViewProject(Resource):
    '''
        View information of a project that a user has access to
    '''
    
    @project_api.expect(project_view_model, validate=True)
    @token_required
    def get(self, current_user):

        req_data = request.get_json()

        _project_id = req_data.get('projectID')

        requested_project = Project.get_by_id(_project_id, self.id)

        if requested_project:
            return {"success": True,
             "project": requested_project.toJSON(),
             "msg": "Project content returned successfully"}, 200
        else:
            return {"success": False,
                    "msg": "No such project found in the scope of this user"}, 404

@project_api.route('/edit')
class UpdateProject(Resource):
    '''
        Updates an existing project using 'ProjectEditModel' input
    '''

    @project_api.expect(project_edit_model, validate=True)
    @token_required
    def post(self, current_user):

        req_data = request.get_json()

        _project_id = req_data.get('projectID')
        _new_project_name = req_data.get('project_name')

        project_name_exists = Project.get_by_name(_new_project_name, self.id)
        project = Project.get_by_id(_project_id, self.id)
        
        if project:
            if project_name_exists:
                return {"success": False,
                        "msg": "A project with the same name already exists"}, 400
            else:
                project.set_project_name(_new_project_name)
                project.save()
                return {"success": True,
                        "project_name": project.project_name,
                        "msg": "Project successfully edited"}, 200
        else:
            return {"success": False,
                        "msg": "No such project exists in the scope of the user"}, 404

@project_api.route('/delete')
class DeleteProject(Resource):
    '''
        Deletes(Soft Delete) an existing project using 'ProjectDeleteModel' input
    '''

    @project_api.expect(project_delete_model, validate=True)
    @token_required
    def delete(self, current_user):

        req_data = request.get_json()

        _project_id = req_data.get('projectID')

        project = Project.get_by_id(_project_id, self.id)
        
        if project:
            project.delete_project()
            related_issues = Issue.get_issues_by_project_id(self.id)
            for issue in related_issues:
                issue.delete_issue()
                issue.save()
                project.decrement_issue_count()
            project.save()
            return {"success": True,
                    "msg": "Project and related issues deleted successfully"}, 200
        else:
            return {"success": False,
                        "msg": "No such project exists in the scope of the user"}, 404

'''
    Flask-Restx Issue API routes
'''

@issue_api.route('/create')
class CreateIssue(Resource):
    '''
        Creates a new issue using 'IssueCreateModel' input
    '''

    @project_api.expect(issue_create_model, validate=True)
    @token_required
    def post(self, current_user):

        req_data = request.get_json()

        _issue_title = req_data.get('issue_title')
        _issue_type = req_data.get('issue_type')
        _parent_project = req_data.get('parent_project')

        existing_project = Project.get_by_id(_parent_project, self.id)
        if not existing_project:
            return {"success": False,
                    "msg": "No such project exists in the scope of the user, cannot create the issue"}, 400
        else:         
            new_issue = Issue(issue_title = _issue_title, issue_type = _issue_type,
                            parent_project = _parent_project, created_by = self.id)
            new_issue.save()
            existing_project.increment_issue_count()
            existing_project.save()

            return {"success": True,
                    "issueID": new_issue.id,
                    "issue_title": new_issue.issue_title,
                    "issue_type": new_issue.issue_type,
                    "issue_status": new_issue.issue_status,
                    "parent_project": new_issue.parent_project,
                    "created_by": new_issue.created_by,
                    "msg": "Issue successfully created"}, 200

@issue_api.route('/view')
class ViewIssue(Resource):
    '''
        View information of a issue that a user has access to
    '''
    
    @issue_api.expect(issue_view_model, validate=True)
    @token_required
    def get(self, current_user):

        req_data = request.get_json()

        _issue_id = req_data.get('issueID')

        requested_issue = Issue.get_by_id(_issue_id)

        if requested_issue:
            _parent_project_id = requested_issue.parent_project
            parent_project = Project.get_by_id(_parent_project_id, self.id)
            if parent_project:
                return {"success": True,
                        "issue": requested_issue.toJSON(),
                        "msg": "Issue content returned successfully"}, 200
            else:
                return {"success": False,
                        "msg": "Cannot reach issue since user has no access to parent project"}, 404
        else:
            return {"success": False,
                    "msg": "No such issue found in this project"}, 404

@issue_api.route('/edit')
class UpdateIssue(Resource):
    '''
        Updates an existing issue using 'IssueEditModel' input
    '''

    @issue_api.expect(issue_edit_model, validate=True)
    @token_required
    def post(self, current_user):

        req_data = request.get_json()

        _issue_id = req_data.get('issueID')
        _new_issue_title = req_data.get('issue_title')
        _new_issue_type = req_data.get('issue_type')
        _new_issue_status= req_data.get('issue_status')
        _new_issue_parent= req_data.get('parent_project')

        issue_to_edit = Issue.get_by_id(_issue_id)

        if issue_to_edit:
            _parent_project_id = issue_to_edit.parent_project
            parent_project = Project.get_by_id(_parent_project_id, self.id)
            if parent_project:
                if _new_issue_title or _new_issue_type or _new_issue_status or _new_issue_parent:
                    success_msg_content = "Successfully updated"
                    if _new_issue_title:
                        issue_to_edit.set_issue_title(_new_issue_title)
                        success_msg_content = success_msg_content + " issue title"
                    if _new_issue_type:
                        issue_to_edit.set_issue_type(_new_issue_type)
                        success_msg_content = success_msg_content + " issue type"                    
                    if _new_issue_status:
                        issue_to_edit.set_issue_status(_new_issue_status)
                        success_msg_content = success_msg_content + " issue status"
                    if _new_issue_parent:
                        new_parent_project = Project.get_by_id(_new_issue_parent, self.id)
                        if new_parent_project:
                            issue_to_edit.update_parent_project(_new_issue_parent)
                            parent_project.decrement_issue_count()
                            parent_project.save()
                            new_parent_project.increment_issue_count()
                            new_parent_project.save()
                            success_msg_content = success_msg_content + " parent project"
                        else:
                            return {"success": False,
                                    "msg": "Cannot change to new parent project since it is not accessible by user"}, 404
                    issue_to_edit.save()
                else:
                    success_msg_content = "Nothing to update"                    
                return {"success": True,
                        "updated issue": issue_to_edit.toJSON(),
                        "msg": success_msg_content}, 200
            else:
                return {"success": False,
                        "msg": "Cannot reach issue since user has no access to parent project"}, 404
        else:
            return {"success": False,
                    "msg": "No such issue found in this project"}, 404

@issue_api.route('/delete')
class DeleteIssue(Resource):
    '''
        Deletes(Soft Delete) an existing issue using 'IssueDeleteModel' input
    '''

    @issue_api.expect(issue_delete_model, validate=True)
    @token_required
    def delete(self, current_user):

        req_data = request.get_json()

        _issue_id = req_data.get('issueID')

        issue_to_delete = Issue.get_by_id(_issue_id)
        
        if issue_to_delete:
            _parent_project_id = issue_to_delete.parent_project
            parent_project = Project.get_by_id(_parent_project_id, self.id)
            if parent_project:
                issue_to_delete.delete_issue()
                issue_to_delete.save()
                parent_project.decrement_issue_count()
                parent_project.save()
                return {"success": True,
                        "msg": "Issue deleted successfully"}, 200
            else:
                return {"success": False,
                        "msg": "Cannot reach issue since user has no access to parent project"}, 404
        else:
            return {"success": False,
                    "msg": "No such issue found in this project"}, 404