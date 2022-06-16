from wtforms import form, fields, validators
from util import db
from model.admin_user import admin_user

class RegistrationForm(form.Form):
    login = fields.StringField(validators=[validators.required()])
    email = fields.StringField()
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        if db.session.query(admin_user).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')