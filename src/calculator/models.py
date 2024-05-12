from src import db
from datetime import datetime
from sqlalchemy.orm import relationship
 
class Patient(db.Model):

    __tablename__ = "patients"
    
    pat_uuid = db.Column(db.String, nullable=False, primary_key=True)
    survey_date = db.Column(db.DateTime, nullable=False, primary_key=True)
    fullname = db.Column(db.String, nullable=False, primary_key=True)
    birthdate = db.Column(db.DateTime, nullable=False, primary_key=True)
    gender = db.Column(db.String, nullable=False, primary_key=True)
    height = db.Column(db.Float, nullable=False)
    X6_birth_weight = db.Column(db.Float, nullable=False, primary_key=True)
    weight = db.Column(db.Float, nullable=False)
    diagnosis_date = db.Column(db.DateTime, nullable=False, primary_key=True)
    surgery_type = db.Column(db.String, nullable=False, primary_key=True)
    surgery_date = db.Column(db.DateTime, nullable=False)
    max_weight_before_surgery = db.Column(db.Float, nullable=False)
    weight_before_surgery = db.Column(db.Float, nullable=False)
    min_weight_after_surgery = db.Column(db.Float, nullable=False)
    therapy_before_surgery = db.Column(db.String, nullable=False)
    X9_HbA1c_before_surgery = db.Column(db.Float, nullable=False)
    arterial_hypertension_degree = db.Column(db.String, nullable=False)
    dyslipidemia = db.Column(db.String, nullable=False)
    heredity = db.Column(db.String, nullable=False)
    complications_history = db.Column(db.String, nullable=False)
    gestational_diabetes = db.Column(db.String, nullable=False)
    X1_age_at_surgery = db.Column(db.Float, nullable=False)
    X2_period_after_surgery = db.Column(db.Float, nullable=False)
    X3_max_BMI_before_surgery = db.Column(db.Float, nullable=False)
    X4_BMI_before_surgery = db.Column(db.Float, nullable=False)
    X5_BMI_at_survey = db.Column(db.Float, nullable=False)
    X7_min_BMI_after_surgery = db.Column(db.Float, nullable=False)
    X8_illness_duration = db.Column(db.Float, nullable=False)
    Target_HbA1c_now = db.Column(db.Float, default=0, nullable=False)
    HbA1c_predicted = db.Column(db.Float, default=0, nullable=False)

    def __init__(
        self,
        pat_uuid,
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
        arterial_hypertension_degree,
        dyslipidemia,
        heredity,
        complications_history,
        gestational_diabetes,
        X1_age_at_surgery,
        X2_period_after_surgery,
        X3_max_BMI_before_surgery,
        X4_BMI_before_surgery,
        X5_BMI_at_survey,
        X7_min_BMI_after_surgery,
        X8_illness_duration,
        Target_HbA1c_now
    ):
        self.pat_uuid = pat_uuid
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
        self.arterial_hypertension_degree = arterial_hypertension_degree
        self.dyslipidemia = dyslipidemia
        self.heredity = heredity
        self.complications_history = complications_history
        self.gestational_diabetes = gestational_diabetes
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


# class Survey(db.Model):

#     __tablename__ = "surveys"

#     UUID = db.Column(db.String, ForeignKey(Patient.pat_uuid), nullable=False, primary_key=True)
#     survey_date = db.Column(db.DateTime, nullable=False, primary_key=True)
#     weight = db.Column(db.Float, nullable=False)
#     min_weight_after_surgery = db.Column(db.Float, nullable=False)
#     X2_period_after_surgery = db.Column(db.Float, nullable=False)
#     X5_BMI_at_survey = db.Column(db.Float, nullable=False)
#     X7_min_BMI_after_surgery = db.Column(db.Float, nullable=False)
#     Target_HbA1c_now = db.Column(db.Float, default=0, nullable=False)
#     HbA1c_predicted = db.Column(db.Float, nullable=False)

#     patient = relationship("Patient")
    

#     def __init__(
#         self,
#         UUID,
#         survey_date,
#         weight,
#         min_weight_after_surgery,
#         X2_period_after_surgery,
#         X5_BMI_at_survey,
#         X7_min_BMI_after_surgery,
#         Target_HbA1c_now
#     ):
#         self.UUID = UUID
#         self.survey_date = survey_date
#         self.weight = weight
#         self.min_weight_after_surgery = min_weight_after_surgery
#         self.X2_period_after_surgery = X2_period_after_surgery
#         self.X5_BMI_at_survey = X5_BMI_at_survey
#         self.X7_min_BMI_after_surgery = X7_min_BMI_after_surgery
#         self.Target_HbA1c_now = Target_HbA1c_now

#     # TODO: Проанализировать что нужно возвращать
#     def __repr__(self):
#         return f"<user {self.username}>"