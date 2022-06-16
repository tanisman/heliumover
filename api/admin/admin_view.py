import flask_login as login
from flask_admin.contrib.sqla import ModelView

class admin_view(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated