from src import db
from datetime import datetime


class Patient(db.Model):

    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    date_id = db.Column(db.Integer, default= datetime.now(), primary_key=True)
    survey_date = db.Column(db.DateTime, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    birthdate = db.Column(db.DateTime, nullable=False)
    gender = db.Column(db.String, nullable=False)
    height = db.Column(db.Float, nullable=False)
    X6_birth_weight = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    diagnosis_date = db.Column(db.DateTime, nullable=False)
    surgery_type = db.Column(db.String, nullable=False)
    surgery_date = db.Column(db.DateTime, nullable=False)
    max_weight_before_surgery = db.Column(db.Float, nullable=False)
    weight_before_surgery = db.Column(db.Float, nullable=False)
    min_weight_after_surgery = db.Column(db.Float, nullable=False)
    therapy_before_surgery = db.Column(db.String, nullable=False)
    X9_HbA1c_before_surgery = db.Column(db.Float, nullable=False)
    X1_age_at_surgery = db.Column(db.Float, nullable=False)
    X2_period_after_surgery = db.Column(db.Float, nullable=False)
    X3_max_BMI_before_surgery = db.Column(db.Float, nullable=False)
    X4_BMI_before_surgery = db.Column(db.Float, nullable=False)
    X5_BMI_at_survey = db.Column(db.Float, nullable=False)
    X7_min_BMI_after_surgery = db.Column(db.Float, nullable=False)
    X8_illness_duration = db.Column(db.Float, nullable=False)
    Target_HbA1c_now = db.Column(db.Float, default=0, nullable=False)

    def __init__(
        self,
        survey_date,
        fullname,
        birthdate,
        gender,
        height,
        X6_birth_weight,
        weight,
        diagnosis_date,
        surgery_type,
        surgery_date,
        max_weight_before_surgery,
        weight_before_surgery,
        min_weight_after_surgery,
        therapy_before_surgery,
        X9_HbA1c_before_surgery,
        X1_age_at_surgery,
        X2_period_after_surgery,
        X3_max_BMI_before_surgery,
        X4_BMI_before_surgery,
        X5_BMI_at_survey,
        X7_min_BMI_after_surgery,
        X8_illness_duration,
        Target_HbA1c_now
    ):
        self.survey_date = survey_date
        self.fullname = fullname
        self.birthdate = birthdate
        self.gender = gender
        self.height = height
        self.X6_birth_weight = X6_birth_weight
        self.weight = weight
        self.diagnosis_date = diagnosis_date
        self.surgery_type = surgery_type
        self.surgery_date = surgery_date
        self.max_weight_before_surgery = max_weight_before_surgery
        self.weight_before_surgery = weight_before_surgery
        self.min_weight_after_surgery = min_weight_after_surgery
        self.therapy_before_surgery = therapy_before_surgery
        self.X9_HbA1c_before_surgery = X9_HbA1c_before_surgery
        self.X1_age_at_surgery = X1_age_at_surgery
        self.X2_period_after_surgery = X2_period_after_surgery
        self.X3_max_BMI_before_surgery = X3_max_BMI_before_surgery
        self.X4_BMI_before_surgery = X4_BMI_before_surgery
        self.X5_BMI_at_survey = X5_BMI_at_survey
        self.X7_min_BMI_after_surgery = X7_min_BMI_after_surgery
        self.X8_illness_duration = X8_illness_duration
        self.Target_HbA1c_now = Target_HbA1c_now

    # TODO: Проанализировать что нужно возвращать
    def __repr__(self):
        return f"<user {self.username}>"
