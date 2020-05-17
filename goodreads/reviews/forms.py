from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, IntegerField, ValidationError


def validate_rating(form, rating):
    if rating.data is None:
        raise ValidationError("Dont forget to rate it!")


class ReviewForm(FlaskForm):
    rating = IntegerField('Rating', validators=[validate_rating])
    review = TextAreaField('What did you think?')
    submit = SubmitField('Post')
