from django.db import models
from django.contrib.auth.models import User


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
    profile_pic = models.ImageField(
        upload_to='profile_pic/DoctorProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=True)
    department = models.CharField(
        max_length=50, choices=departments, default='Cardiologist')
    fee = models.PositiveIntegerField(null=False, default=100)
    appointment_duration = models.PositiveSmallIntegerField(
        null=False, default=30)
    start_time = models.TimeField(null=False)
    end_time = models.TimeField(null=False)
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(
        upload_to='profile_pic/PatientProfilePic/', null=True, blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=False)
    symptoms = models.CharField(max_length=100, null=False)  # might remove
    # patient blood group
    bloodgroup = models.CharField(max_length=4, null=False)
    sex = models.CharField(max_lenght=1)
    assignedDoctorId = models.PositiveIntegerField(null=True)  # might remove
    status = models.BooleanField(default=True)

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
    patientName = models.CharField(max_length=40, null=True)
    doctorName = models.CharField(max_length=40, null=True)
    appointmentDate = models.DateField(auto_now=True)
    appointmentTime = models.TimeField(null=False)
    description = models.TextField(max_length=500)  # might remove
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
    med_id = models.PositiveSmallIntegerField(primary_key=True)
    med_name = models.CharField(max_length=100)
    cost_for_one = models.PositiveIntegerField(null=False)
    quantity-models.PositiveIntegerField(null=False)


# class Takes_meds(models.Model):


# class Tests(models.Model):
#     test_id = models.PositiveSmallIntegerField(primary=True)
#     test_name = models.CharField(max_length=50)
#     cost = models.PositiveIntegerField(null=False)
#     start_time = models.TimeField(null=False)
#     end_time = models.TimeField(null=False)
#     test_duration = models.PositiveSmallIntegerField(
#         null=False, default=30)

# class Had_test(models.Model):
