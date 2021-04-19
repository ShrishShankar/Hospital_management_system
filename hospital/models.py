from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import timezone
from django import forms


departments = [('Cardiologist', 'Cardiologist'),
               ('Dermatologists', 'Dermatologists'),
               ('Emergency Medicine Specialists',
                'Emergency Medicine Specialists'),
               ('Allergists/Immunologists', 'Allergists/Immunologists'),
               ('Anesthesiologists', 'Anesthesiologists'),
               ('Colon and Rectal Surgeons', 'Colon and Rectal Surgeons')
               ]


# class Department(models.Model):
#     department_id=models.PositiveSmallIntegerField(primary_key=True)
#     department_name=models.CharField(max_length=40)


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # profile_pic = models.ImageField(upload_to='profile_pic/DoctorProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    department = models.CharField(max_length=50, choices=departments, default='Cardiologist')
    fee = models.PositiveIntegerField(null=False, default=100)
    appointment_duration = models.PositiveSmallIntegerField(null=False, default=30)
    start_time = models.TimeField(null=False, default=datetime.time(9, 00))
    end_time = models.TimeField(null=False, default=datetime.time(17, 00))
    status = models.BooleanField(default=False)

    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return "{} ({})".format(self.user.first_name, self.department)


class Patient(models.Model):
    GENDER_CHOICES=[('Male','Male'),('Female','Female'),]
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    symptoms = models.CharField(max_length=100,null=False)
    assignedDoctorId = models.PositiveIntegerField(null=True)
    admitDate=models.DateField(auto_now=True)
    status=models.BooleanField(default=True)
    #additional changes
    email=models.EmailField(max_length=256,null=False)
    bloodgroup=models.CharField(max_length=4,null=False)
    age=models.IntegerField(null=False)
    sex=models.CharField(max_length=10,null=False, choices=GENDER_CHOICES)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name

    @property
    def get_id(self):
        return self.user.id

    def __str__(self):
        return self.user.first_name+" ("+self.symptoms+")"


class Appointment(models.Model):
    patientId = models.PositiveIntegerField(null=True)
    doctorId = models.PositiveIntegerField(null=True)
    # patientId = models.ForeignKey(Patient, on_delete=models.CASCADE)
    # doctorId = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patientName = models.CharField(max_length=40, null=True)
    doctorName = models.CharField(max_length=40, null=True)
    appointmentDate = models.DateField(auto_now=True)
    appointmentTime = models.TimeField(
        null=False, auto_now=True)  # remove auto_now
    description = models.TextField(max_length=500)  # might remove
    status = models.BooleanField(default=False)

    # class Meta:
    #     unique_together = (("patientID", "doctorId"),)


class Facilities(models.Model):
    FACILITIES=[('Bloodtest','Bloodtest'),('X-ray','X-ray')]
    patientId = models.PositiveIntegerField(null=True)
    doctorId = models.PositiveIntegerField(null=True)
    patientName = models.CharField(max_length=40, null=True)
    doctorName = models.CharField(max_length=40, null=True)

    appointmentDate = models.DateField(auto_now=True)
    appointmentTime = models.TimeField(
        null=False, auto_now=True)
    
    service=models.CharField(max_length=20,null=False, choices=FACILITIES)
    status = models.BooleanField(default=False)


class PatientDischargeDetails(models.Model):
    patientId = models.PositiveIntegerField(null=True)
    patientName = models.CharField(max_length=40)

    assignedDoctorName = models.CharField(max_length=40)  # might remove
    doctorId = models.PositiveIntegerField(null=True)
    doctorName = models.CharField(max_length=40, null=True)

    address = models.CharField(max_length=40)  # might remove
    mobile = models.CharField(max_length=20, null=True)  # might remove
    symptoms = models.CharField(max_length=100, null=True)  # might remove

    admitDate = models.DateField(null=False)  # need to remove
    releaseDate = models.DateField(null=False)  # need to remove
    daySpent = models.PositiveIntegerField(null=False)  # might remove

    roomCharge = models.PositiveIntegerField(null=False)  # might remove
    medicineCost = models.PositiveIntegerField(null=False)  # might remove
    doctorFee = models.PositiveIntegerField(null=False)  # might remove
    OtherCharge = models.PositiveIntegerField(null=False)  # need to remove
    total = models.PositiveIntegerField(null=False)


class Medicine(models.Model):
    MEDICINES = [('PARACETAMOL','PARACETAMOL'),('TYLENOL','TYLENOL')]
    # medId = models.PositiveSmallIntegerField(primary_key=True)
    # medName = models.CharField(max_length=100)
    patientId = models.PositiveIntegerField(null=True)
    costForOne = models.PositiveIntegerField(null=False, default=50)
    quantity = models.PositiveIntegerField(null=False)
    drug=models.CharField(max_length=20,null=False, choices=MEDICINES)


# class Takes_meds(models.Model):
#     purchaseDate = models.DateTimeField(auto_now=True)
#     patientId = models.ForeignKey(Patient, on_delete=models.CASCADE)
#     medId = models.ForeignKey(Medicine, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(null=False)

#     class Meta:
#         unique_together = (("patientID", "medId"),)

