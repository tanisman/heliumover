from wtforms import form, fields, validators
from werkzeug.security import check_password_hash
from util import db
from model.admin_user import admin_user

# Define login and registration forms (for flask-login)
class login_form(form.Form):
    login = fields.StringField(validators=[validators.DataRequired()])
    password = fields.PasswordField(validators=[validators.DataRequired()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid username/password')

        # we're comparing the plaintext pw with the the hash from the db
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError('Invalid username/password')

    def get_user(self):
        return db.session.query(admin_user).filter_by(login=self.login.data).first()
