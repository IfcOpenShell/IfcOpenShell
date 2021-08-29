from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from .models import User


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError(
                "Username already exists! Please try a different username"
            )

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(
            email_address=email_address_to_check.data
        ).first()
        if email_address:
            raise ValidationError("Email Address already exists!")

    username = StringField(
        label="User Name:", validators=[Length(min=2, max=30), DataRequired()]
    )
    email_address = StringField(
        label="Email Address:", validators=[Email(), DataRequired()]
    )
    password1 = PasswordField(
        label="Password:", validators=[Length(min=6), DataRequired()]
    )
    password2 = PasswordField(
        label="Confirm Password:", validators=[EqualTo("password1"), DataRequired()]
    )
    submit = SubmitField(label="Create Account")


class LoginForm(FlaskForm):
    username = StringField(label="User Name:", validators=[DataRequired()])
    password = PasswordField(label="Password:", validators=[DataRequired()])
    submit = SubmitField(label="Sign in")


class OauthForm(FlaskForm):
    client_name = StringField(label="Client Name:", validators=[DataRequired()])
    # client_uri = StringField(label="Client URI:", validators=[DataRequired()])
    grant_types = StringField(label="Grant Types:", validators=[DataRequired()])
    # redirect_uris = StringField(label="Redirect URIs:", validators=[DataRequired()])
    response_types = StringField(label="Response Types:", validators=[DataRequired()])
    scope = StringField(label="Scope:", validators=[DataRequired()])
    # token_endpoint_auth_method = StringField(
    #     label="Token Endpoint Auth Method:", validators=[DataRequired()]
    # )
    submit = SubmitField(label="Create OAuth")
