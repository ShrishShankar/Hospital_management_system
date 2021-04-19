from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa
import io
from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import timedelta, date
import datetime
from django.conf import settings
from django.db import connection
from django.contrib.auth.hashers import make_password

# Create your views here.

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'hospital/index.html')


# for showing signup/login button for admin
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'hospital/adminclick.html')


# for showing signup/login button for doctor
def doctorclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'hospital/doctorclick.html')


# for showing signup/login button for patient
def patientclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'hospital/patientclick.html')


def fetchNextId(table_name):
    cursor = connection.cursor()
    cursor.execute("SELECT id FROM {} ORDER BY id DESC LIMIT 1;".format(table_name))
    user_last_id = cursor.fetchall()
    if user_last_id is ():
        user_last_id=0
    else:
        ((user_last_id,),)=user_last_id
    
    return user_last_id+1


def authUserReg(form, user_type):
    auth_user_attributes = ['id', 'password', 'last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active' , 'date_joined']
    form_data = form.cleaned_data

    user_next_id = fetchNextId('auth_user')
    form_data['id'] = user_next_id
    form_data['password'] = make_password(form_data['password'])
    form_data['last_login'] = 'NULL'
    form_data['is_superuser'] = 0
    form_data['email'] = ''
    form_data['is_staff'] = 0
    form_data['is_active'] = 1
    form_data['date_joined'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    
    sql=''
    for key in auth_user_attributes:
        if isinstance(form_data[key], str) and form_data[key] is not 'NULL':
            form_data[key]="'{}'".format(form_data[key])
        if key is not 'date_joined':
            sql += str(form_data[key]) + ", "
        else:
            sql += str(form_data[key])

    cursor = connection.cursor()
    sql = "INSERT INTO auth_user VALUES (" + sql + ");"
    cursor.execute(sql)

    cursor.execute("SELECT count(*) FROM auth_group WHERE name='{}';".format(user_type))
    group_exist=cursor.fetchone()
    (group_exist,)=group_exist
    if group_exist==0:
        auth_group_next_id = fetchNextId('auth_group')
    else:
        cursor.execute("SELECT id FROM auth_group WHERE name='{}';".format(user_type))
        (auth_group_next_id,)=cursor.fetchone()
    
    cursor.execute("INSERT INTO auth_group VALUES ({}, '{}') ON DUPLICATE KEY UPDATE id=id;".format(auth_group_next_id, user_type))
    
    auth_user_groups_next_id=fetchNextId('auth_user_groups')
    cursor.execute("INSERT INTO auth_user_groups VALUES ({}, {}, {});".format(auth_user_groups_next_id, user_next_id, auth_group_next_id))


def admin_signup_view(request):
    form = forms.AdminSigupForm()
    if request.method == 'POST':
        form = forms.AdminSigupForm(request.POST)
        if form.is_valid():
            # user = form.save()
            # user.set_password(user.password)
            # user.save()
            # my_admin_group = Group.objects.get_or_create(name='ADMIN')
            # my_admin_group[0].user_set.add(user)
            authUserReg(form, 'ADMIN')
            
            return HttpResponseRedirect('adminlogin')
    return render(request, 'hospital/adminsignup.html', {'form': form})


def doctor_signup_view(request):
    userForm = forms.DoctorUserForm()
    doctorForm = forms.DoctorForm()
    mydict = {'userForm': userForm, 'doctorForm': doctorForm}
    if request.method == 'POST':
        userForm = forms.DoctorUserForm(request.POST)
        doctorForm = forms.DoctorForm(request.POST, request.FILES)
        if userForm.is_valid() and doctorForm.is_valid():
            # user = userForm.save()
            # user.set_password(user.password)
            # user.save()
            # my_doctor_group = Group.objects.get_or_create(name='DOCTOR')
            # my_doctor_group[0].user_set.add(user)

            authUserReg(userForm, 'DOCTOR')
            doc_attributes = ['id', 'address', 'mobile', 'department', 'fee', 'appointment_duration', 'start_time', 'end_time', 'status', 'user_id']
            doc_data=doctorForm.cleaned_data
            doc_data['id'] = fetchNextId('hospital_doctor')
            doc_data['appointment_duration'] = 30
            doc_data['start_time'] = '09:00:00'
            doc_data['end_time'] = '17:00:00'
            doc_data['user_id'] = fetchNextId('auth_user') - 1
            doc_data['fee'] = 100
            doc_data['status'] = 0
            
            sql=''
            for key in doc_attributes:
                if isinstance(doc_data[key], str):
                    doc_data[key]="'{}'".format(doc_data[key])
                if key is not 'user_id':
                    sql += str(doc_data[key]) + ", "
                else:
                    sql += str(doc_data[key])
            print(sql)
            cursor = connection.cursor()
            sql = "INSERT INTO hospital_doctor VALUES (" + sql + ");"
            cursor.execute(sql)
            
            # doctor = doctorForm.save(commit=False)
            # doctor.user = user
            # doctor = doctor.save()
        return HttpResponseRedirect('doctorlogin')
    return render(request, 'hospital/doctorsignup.html', context=mydict)


def patient_signup_view(request):
    userForm = forms.PatientUserForm()
    patientForm = forms.PatientForm()
    mydict = {'userForm': userForm, 'patientForm': patientForm}
    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST)
        patientForm = forms.PatientForm(request.POST, request.FILES)
        if userForm.is_valid() and patientForm.is_valid():
            # user = userForm.save()
            # user.set_password(user.password)
            # user.save()
            # my_patient_group = Group.objects.get_or_create(name='PATIENT')
            # my_patient_group[0].user_set.add(user)

            authUserReg(userForm, 'PATIENT')
            pat_attributes = ['id', 'address', 'mobile', 'symptoms', 'assignedDoctorId', 'admitDate', 'status', 'email', 'bloodgroup', 'age', 'sex', 'user_id']
            pat_data=patientForm.cleaned_data
            pat_data['id'] = fetchNextId('hospital_patient')
            pat_data['admitDate'] = datetime.datetime.now().strftime("%Y-%m-%d")
            pat_data['status'] = 1
            pat_data['user_id'] = fetchNextId('auth_user') - 1
            pat_data['assignedDoctorId'] = getattr(pat_data['assignedDoctorId'], 'user_id') # might change if form is changed
            
            sql=''
            for key in pat_attributes:
                if isinstance(pat_data[key], str):
                    pat_data[key]="'{}'".format(pat_data[key])
                if key is not 'user_id':
                    sql += str(pat_data[key]) + ", "
                else:
                    sql += str(pat_data[key])
            cursor = connection.cursor()
            sql = "INSERT INTO hospital_patient VALUES (" + sql + ");"
            cursor.execute(sql)

            # patient=patientForm.save(commit=False)
            # patient.user=user
            # patient.assignedDoctorId=request.POST.get('assignedDoctorId')
            # patient.status=True
            # patient = patient.save()
        return HttpResponseRedirect('patientlogin')
    return render(request, 'hospital/patientsignup.html', context=mydict)


# -----------for checking user is doctor , patient or admin
def is_admin(user):
    return user.groups.filter(name='ADMIN').exists()


def is_doctor(user):
    return user.groups.filter(name='DOCTOR').exists()


def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


# ---------AFTER ENTERING CREDENTIALS WE CHECK WHETHER USERNAME AND PASSWORD IS OF ADMIN,DOCTOR OR PATIENT
def afterlogin_view(request):
    if is_admin(request.user):
        return redirect('admin-dashboard')
    elif is_doctor(request.user):
        accountapproval = models.Doctor.objects.all().filter(
            user_id=request.user.id, status=True)
        if accountapproval:
            return redirect('doctor-dashboard')
        else:
            return render(request, 'hospital/doctor_wait_for_approval.html')
    elif is_patient(request.user):
            return redirect('patient-dashboard')


# ---------------------------------------------------------------------------------
# ------------------------ ADMIN RELATED VIEWS START ------------------------------
# ---------------------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    cursor =connection.cursor()
   
    cursor.execute("SELECT count(*) as count from hospital_Doctor")
    res=dictfetchall(cursor)
    doctorcount=res[0]['count']
   
    cursor.execute("SELECT count(*) as count from hospital_Patient")
    res=dictfetchall(cursor)
    pendingdoctorcount=res[0]['count']
   
    cursor.execute("SELECT count(*) as count from hospital_Patient")
    res=dictfetchall(cursor)
    patientcount=res[0]['count']
    
    cursor.execute("SELECT count(*) as count from hospital_Appointment WHERE status=True")
    res=dictfetchall(cursor)
    appointmentcount=res[0]['count']
    cursor.execute("SELECT count(*) as count from hospital_Facilities WHERE status=True")
    res=dictfetchall(cursor)
    appointmentcount=res[0]['count']+appointmentcount
    


    cursor.execute("SELECT count(*) as count from hospital_Appointment WHERE status=False")
    res=dictfetchall(cursor)
    pendingappointmentcount=res[0]['count']
    cursor.execute("SELECT count(*) as count from hospital_Facilities WHERE status=False")
    res=dictfetchall(cursor)
    pendingappointmentcount=res[0]['count']+pendingappointmentcount
    mydict = {
        
        'doctorcount': doctorcount,
        'pendingdoctorcount': pendingdoctorcount,
        'patientcount': patientcount,
        'appointmentcount': appointmentcount,
        'pendingappointmentcount': pendingappointmentcount,
    }
    return render(request, 'hospital/admin_dashboard.html', context=mydict)


# this view for sidebar click on admin page
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_doctor_view(request):
    return render(request, 'hospital/admin_doctor.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_view(request):
    doctors = models.Doctor.objects.all().filter(status=True)
    return render(request, 'hospital/admin_view_doctor.html', {'doctors': doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_doctor_from_hospital_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-view-doctor')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_doctor_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)

    userForm = forms.DoctorUserForm(instance=user)
    doctorForm = forms.DoctorForm(request.FILES, instance=doctor)
    mydict = {'userForm': userForm, 'doctorForm': doctorForm}
    if request.method == 'POST':
        userForm = forms.DoctorUserForm(request.POST, instance=user)
        doctorForm = forms.DoctorForm(
            request.POST, request.FILES, instance=doctor)
        if userForm.is_valid() and doctorForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            doctor = doctorForm.save(commit=False)
            doctor.status = True
            doctor.save()
            return redirect('admin-view-doctor')
    return render(request, 'hospital/admin_update_doctor.html', context=mydict)



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_doctor_view(request):
    # those whose approval are needed
    doctors = models.Doctor.objects.all().filter(status=False)
    return render(request, 'hospital/admin_approve_doctor.html', {'doctors': doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_doctor_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    doctor.status = True
    doctor.save()
    return redirect(reverse('admin-approve-doctor'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_doctor_view(request, pk):
    doctor = models.Doctor.objects.get(id=pk)
    user = models.User.objects.get(id=doctor.user_id)
    user.delete()
    doctor.delete()
    return redirect('admin-approve-doctor')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_doctor_specialisation_view(request):
    doctors = models.Doctor.objects.all().filter(status=True)
    return render(request, 'hospital/admin_view_doctor_specialisation.html', {'doctors': doctors})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_patient_view(request):
    return render(request, 'hospital/admin_patient.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_patient_view(request):
    patients = models.Patient.objects.all().filter(status=True)
    return render(request, 'hospital/admin_view_patient.html', {'patients': patients})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def delete_patient_from_hospital_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    user = models.User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    return redirect('admin-view-patient')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def update_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    user = models.User.objects.get(id=patient.user_id)

    userForm = forms.PatientUserForm(instance=user)
    patientForm = forms.PatientForm(request.FILES, instance=patient)
    mydict = {'userForm': userForm, 'patientForm': patientForm}
    if request.method == 'POST':
        userForm = forms.PatientUserForm(request.POST, instance=user)
        patientForm = forms.PatientForm(
            request.POST, request.FILES, instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            patient = patientForm.save(commit=False)
            patient.status = True
            patient.assignedDoctorId = request.POST.get('assignedDoctorId')
            patient.save()
            return redirect('admin-view-patient')
    return render(request, 'hospital/admin_update_patient.html', context=mydict)







# --------------------- FOR DISCHARGING PATIENT BY ADMIN START-------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_discharge_patient_view(request):
    patients = models.Patient.objects.all().filter(status=True)
    return render(request, 'hospital/admin_discharge_patient.html', {'patients': patients})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def discharge_patient_view(request, pk):
    patient = models.Patient.objects.get(id=pk)
    days = (date.today()-patient.admitDate)  # 2 days, 0:00:00
    assignedDoctor = models.User.objects.all().filter(id=patient.assignedDoctorId)
    d = days.days  # only how many day that is 2
    patientDict = {
        'patientId': pk,
        'name': patient.get_name,
        'mobile': patient.mobile,
        'address': patient.address,
        'symptoms': patient.symptoms,
        'admitDate': patient.admitDate,
        'todayDate': date.today(),
        'day': d,
        'assignedDoctorName': assignedDoctor[0].first_name,
    }
    if request.method == 'POST':
        feeDict = {
            'roomCharge': int(request.POST['roomCharge'])*int(d),
            'doctorFee': request.POST['doctorFee'],
            'medicineCost': request.POST['medicineCost'],
            'OtherCharge': request.POST['OtherCharge'],
            'total': (int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        }
        patientDict.update(feeDict)
        # for updating to database patientDischargeDetails (pDD)
        pDD = models.PatientDischargeDetails()
        pDD.patientId = pk
        pDD.patientName = patient.get_name
        pDD.assignedDoctorName = assignedDoctor[0].first_name
        pDD.address = patient.address
        pDD.mobile = patient.mobile
        pDD.symptoms = patient.symptoms
        pDD.admitDate = patient.admitDate
        pDD.releaseDate = date.today()
        pDD.daySpent = int(d)
        pDD.medicineCost = int(request.POST['medicineCost'])
        pDD.roomCharge = int(request.POST['roomCharge'])*int(d)
        pDD.doctorFee = int(request.POST['doctorFee'])
        pDD.OtherCharge = int(request.POST['OtherCharge'])
        pDD.total = (int(request.POST['roomCharge'])*int(d))+int(request.POST['doctorFee'])+int(
            request.POST['medicineCost'])+int(request.POST['OtherCharge'])
        pDD.save()
        return render(request, 'hospital/patient_final_bill.html', context=patientDict)
    return render(request, 'hospital/patient_generate_bill.html', context=patientDict)


# --------------for discharge patient bill (pdf) download and printing


def render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return


def download_pdf_view(request, pk):
    dischargeDetails = models.PatientDischargeDetails.objects.all().filter(
        patientId=pk).order_by('-id')[:1]
    dict = {
        'patientName': dischargeDetails[0].patientName,
        'assignedDoctorName': dischargeDetails[0].assignedDoctorName,
        'address': dischargeDetails[0].address,
        'mobile': dischargeDetails[0].mobile,
        'symptoms': dischargeDetails[0].symptoms,
        'admitDate': dischargeDetails[0].admitDate,
        'releaseDate': dischargeDetails[0].releaseDate,
        'daySpent': dischargeDetails[0].daySpent,
        'medicineCost': dischargeDetails[0].medicineCost,
        'roomCharge': dischargeDetails[0].roomCharge,
        'doctorFee': dischargeDetails[0].doctorFee,
        'OtherCharge': dischargeDetails[0].OtherCharge,
        'total': dischargeDetails[0].total,
    }
    return render_to_pdf('hospital/download_bill.html', dict)


# -----------------APPOINTMENT START--------------------------------------------------------------------
@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_appointment_view(request):
    return render(request, 'hospital/admin_appointment.html')


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_appointment_view(request):
    appointments = models.Appointment.objects.all().filter(status=True)
    return render(request, 'hospital/admin_view_appointment.html', {'appointments': appointments})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_view_facilities_view(request):
    facilities=models.Facilities.objects.all().filter(status=True)
    return render(request, 'hospital/admin_view_facilities.html', {'facilities': facilities})



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_appointment_view(request):
    # those whose approval are needed
    appointments = models.Appointment.objects.all().filter(status=False)
    return render(request, 'hospital/admin_approve_appointment.html', {'appointments': appointments})

@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def admin_approve_facilities_view(request):
    facilities=models.Facilities.objects.all().filter(status=False)
    return render(request, 'hospital/admin_approve_facilities.html', {'facilities': facilities})


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_appointment_view(request, pk):
    appointment = models.Appointment.objects.get(id=pk)
    appointment.status = True
    appointment.save()
    return redirect(reverse('admin-approve-appointment'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_appointment_view(request, pk):
    appointment = models.Appointment.objects.get(id=pk)
    appointment.delete()
    return redirect('admin-approve-appointment')



@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def approve_facilities_view(request, pk):
    facilities = models.Facilities.objects.get(id=pk)
    facilities.status = True
    facilities.save()
    return redirect(reverse('admin-approve-facilities'))


@login_required(login_url='adminlogin')
@user_passes_test(is_admin)
def reject_facilities_view(request, pk):
    facilities = models.Facilities.objects.get(id=pk)
    facilities.delete()
    return redirect('admin-approve-facilities')
# ---------------------------------------------------------------------------------
# ------------------------ ADMIN RELATED VIEWS END ------------------------------
# ---------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------
# ------------------------ DOCTOR RELATED VIEWS START ------------------------------
# ---------------------------------------------------------------------------------
@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    # for three cards
    patientcount = models.Patient.objects.all().filter(
        status=True, assignedDoctorId=request.user.id).count()

    appointmentcount = models.Appointment.objects.all().filter(
        status=True, doctorId=request.user.id).count()
    patientdischarged = models.PatientDischargeDetails.objects.all(
    ).distinct().filter(assignedDoctorName=request.user.first_name).count()

    # for  table in doctor dashboard
    appointments = models.Appointment.objects.all().filter(
        status=True, doctorId=request.user.id).order_by('-id')
    patientid = []
    for a in appointments:
        patientid.append(a.patientId)
    patients = models.Patient.objects.all().filter(
        status=True, user_id__in=patientid).order_by('-id')
    appointments = zip(appointments, patients)
    mydict = {
        'patientcount': patientcount,
        'appointmentcount': appointmentcount,
        'patientdischarged': patientdischarged,
        'appointments': appointments,
        # for profile picture of doctor in sidebar
        'doctor': models.Doctor.objects.get(user_id=request.user.id),
    }
    return render(request, 'hospital/doctor_dashboard.html', context=mydict)


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_patient_view(request):
    mydict = {
        # for profile picture of doctor in sidebar
        'doctor': models.Doctor.objects.get(user_id=request.user.id),
    }
    return render(request, 'hospital/doctor_patient.html', context=mydict)


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    patients = models.Patient.objects.all().filter(
        status=True, assignedDoctorId=request.user.id)
    # for profile picture of doctor in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    return render(request, 'hospital/doctor_view_patient.html', {'patients': patients, 'doctor': doctor})




@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    # for profile picture of doctor in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    return render(request, 'hospital/doctor_appointment.html', {'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    # for profile picture of doctor in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.all().filter(
        status=True, doctorId=request.user.id)
    patientid = []
    for a in appointments:
        patientid.append(a.patientId)
    patients = models.Patient.objects.all().filter(
        status=True, user_id__in=patientid)
    appointments = zip(appointments, patients)
    return render(request, 'hospital/doctor_view_appointment.html', {'appointments': appointments, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def doctor_delete_appointment_view(request):
    # for profile picture of doctor in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.all().filter(
        status=True, doctorId=request.user.id)
    patientid = []
    for a in appointments:
        patientid.append(a.patientId)
    patients = models.Patient.objects.all().filter(
        status=True, user_id__in=patientid)
    appointments = zip(appointments, patients)
    return render(request, 'hospital/doctor_delete_appointment.html', {'appointments': appointments, 'doctor': doctor})


@login_required(login_url='doctorlogin')
@user_passes_test(is_doctor)
def delete_appointment_view(request, pk):
    appointment = models.Appointment.objects.get(id=pk)
    appointment.delete()
    # for profile picture of doctor in sidebar
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.all().filter(
        status=True, doctorId=request.user.id)
    patientid = []
    for a in appointments:
        patientid.append(a.patientId)
    patients = models.Patient.objects.all().filter(
        status=True, user_id__in=patientid)
    appointments = zip(appointments, patients)
    return render(request, 'hospital/doctor_delete_appointment.html', {'appointments': appointments, 'doctor': doctor})


# ---------------------------------------------------------------------------------
# ------------------------ DOCTOR RELATED VIEWS END ------------------------------
# ---------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------
# ------------------------ PATIENT RELATED VIEWS START ------------------------------
# ---------------------------------------------------------------------------------
@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    doctor = models.Doctor.objects.get(user_id=patient.assignedDoctorId)
    mydict = {
        'patient': patient,
        'doctorName': doctor.get_name,
        'doctorMobile': doctor.mobile,
        'doctorAddress': doctor.address,
        'symptoms': patient.symptoms,
        'doctorDepartment': doctor.department,
        'admitDate': patient.admitDate,
        'bloodgroup': patient.bloodgroup,
        'email': patient.email,
        'age': patient.age,
        'sex': patient.sex,
    }
    return render(request, 'hospital/patient_dashboard.html', context=mydict)


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_appointment_view(request):
    # for profile picture of patient in sidebar
    patient = models.Patient.objects.get(user_id=request.user.id)
    return render(request, 'hospital/patient_appointment.html', {'patient': patient})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_appointment_view(request):
    appointmentForm = forms.PatientAppointmentForm()
    # for profile picture of patient in sidebar
    patient = models.Patient.objects.get(user_id=request.user.id)
    message = None
    mydict = {'appointmentForm': appointmentForm,
              'patient': patient, 'message': message}
    if request.method == 'POST':
        appointmentForm = forms.PatientAppointmentForm(request.POST)
        if appointmentForm.is_valid():
            print(request.POST.get('doctorId'))
            #desc = request.POST.get('description')

            doctor = models.Doctor.objects.get( user_id=request.POST.get('doctorId'))

            #doctor=models.Doctor.objects.get(user_id=request.POST.get('doctorId'))

            appointment=appointmentForm.save(commit=False)
            appointment.doctorId=request.POST.get('doctorId')
            appointment.patientId=request.user.id #----user can choose any patient but only their info will be stored
            appointment.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            appointment.patientName=request.user.first_name #----user can choose any patient but only their info will be stored
            appointment.status=False
            appointment.description=request.POST.get('description')

            appointment.save()
        return HttpResponseRedirect('patient-view-appointment')
    return render(request, 'hospital/patient_book_appointment.html', context=mydict)


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_book_facilities_view(request):
    facilitiesForm=forms.PatientFacilitiesForm()
    patient = models.Patient.objects.get(user_id=request.user.id)
    message = None
    mydict = {'facilitiesForm': facilitiesForm,
              'patient': patient, 'message': message}
    if request.method == 'POST':
        facilitiesForm=forms.PatientFacilitiesForm(request.POST)
        if facilitiesForm.is_valid():
            doctor = models.Doctor.objects.get(user_id=request.POST.get('doctorId'))
            facilities=facilitiesForm.save(commit=False)
            facilities.doctorId=request.POST.get('doctorId')
            facilities.patientId=request.user.id #----user can choose any patient but only their info will be stored
            facilities.doctorName=models.User.objects.get(id=request.POST.get('doctorId')).first_name
            facilities.patientName=request.user.first_name #----user can choose any patient but only their info will be stored
            facilities.status=False
            facilities.service=request.POST.get('service')

            facilities.save()
        return HttpResponseRedirect('patient-view-facilities')
    return render(request, 'hospital/patient_book_facilities.html', context=mydict)


# @login_required(login_url='patientlogin')
# @user_passes_test(is_patient)
# def patient_buy_medicine(request):
#     medicineForm=forms.MedicineForm()
#     patient = models.Patient.objects.get(user_id=request.user.id)
#     message = None
#     mydict = {'medicineForm': medicineForm,
#               'patient': patient, 'message': message}
#     if request.method == 'POST':
#         medicineForm=forms.MedicineForm(request.POST)
#         print(medicineForm.is_valid())
#         if medicineForm.is_valid():
#             medicine=medicineForm.save(commit=False)
#             medicine.patientId=request.user.id
#             medicine.quantity=request.POST.get('quantity')
#             medicine.drug=request.POST.get('drug')

#             medicine.save()
#         return HttpResponseRedirect('patient-medicine-bill')
#     return render(request, 'hospital/patient_buy_medicine.html', context=mydict)


# @login_required(login_url='patientlogin')
# @user_passes_test(is_patient)
# def patient_medicine_bill(request):
#     patient = models.Patient.objects.get(user_id=request.user.id)
#     assignedDoctor = models.User.objects.all().filter(id=patient.assignedDoctorId)

#     cursor = connection.cursor()
#     cursor.execute("SELECT medId FROM hospital_medicine ORDER BY medId DESC LIMIT 1;")
#     user_last_id = cursor.fetchall()
#     if user_last_id is ():
#         user_last_id=0
#     else:
#         ((user_last_id,),)=user_last_id
    
#     med_id = user_last_id
    
#     med = models.Medicine.objects.get(medId = med_id)
#     print("error at medicine")
#     patientDict = {
#         'patientId': patient.id,
#         'name': patient.get_name,
#         'mobile': patient.mobile,
#         'address': patient.address,
#         'symptoms': patient.symptoms,
#         'todayDate': date.today(),
#         'assignedDoctorName': assignedDoctor[0].first_name,
#     }
#     feeDict = {
#         'medId': med.medId,
#         'medicineName': med.medName,
#         'quantity': med.quantity,
#         'costPerMedicine': med.costForOne,
#         'Tax': 0.05,
#         'total': (med.costForOne*med.quantity*1.05)
#         }
#     patientDict.update(feeDict)
#     return render(request, 'hospital/patient_medicine_bill.html', context=patientDict)


# def download_med_pdf_view(request, medId):
#     med = models.Medicine.objects.get(medId = med_id)
#     patient = models.Patient.objects.get(user_id=request.user.id)
#     dict = {
#         'patientName': dischargeDetails[0].patientName,
#         'assignedDoctorName': dischargeDetails[0].assignedDoctorName,
#         'address': dischargeDetails[0].address,
#         'mobile': dischargeDetails[0].mobile,
#         'symptoms': dischargeDetails[0].symptoms,
#         'admitDate': dischargeDetails[0].admitDate,
#         'releaseDate': dischargeDetails[0].releaseDate,
#         'daySpent': dischargeDetails[0].daySpent,
#         'medicineCost': dischargeDetails[0].medicineCost,
#         'roomCharge': dischargeDetails[0].roomCharge,
#         'doctorFee': dischargeDetails[0].doctorFee,
#         'OtherCharge': dischargeDetails[0].OtherCharge,
#         'total': dischargeDetails[0].total,
#     }
#     return render_to_pdf('hospital/download_med_pdf.html', dict)


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_appointment_view(request):
    # for profile picture of patient in sidebar
    patient = models.Patient.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.all().filter(patientId=request.user.id)
    return render(request, 'hospital/patient_view_appointment.html', {'appointments': appointments, 'patient': patient})


@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_view_facilities_view(request):
    patient = models.Patient.objects.get(user_id=request.user.id)
    facilities=models.Facilities.objects.all().filter(patientId=request.user.id)
    return render(request, 'hospital/patient_view_facilities.html', {'facilities': facilities, 'patient': patient})

@login_required(login_url='patientlogin')
@user_passes_test(is_patient)
def patient_discharge_view(request):
    # for profile picture of patient in sidebar
    patient = models.Patient.objects.get(user_id=request.user.id)
    dischargeDetails = models.PatientDischargeDetails.objects.all().filter(
        patientId=patient.id).order_by('-id')[:1]
    patientDict = None
    if dischargeDetails:
        patientDict = {
            'is_discharged': True,
            'patient': patient,
            'patientId': patient.id,
            'patientName': patient.get_name,
            'assignedDoctorName': dischargeDetails[0].assignedDoctorName,
            'address': patient.address,
            'mobile': patient.mobile,
            'symptoms': patient.symptoms,
            'admitDate': patient.admitDate,
            'releaseDate': dischargeDetails[0].releaseDate,
            'daySpent': dischargeDetails[0].daySpent,
            'medicineCost': dischargeDetails[0].medicineCost,
            'roomCharge': dischargeDetails[0].roomCharge,
            'doctorFee': dischargeDetails[0].doctorFee,
            'OtherCharge': dischargeDetails[0].OtherCharge,
            'total': dischargeDetails[0].total,
        }
        print(patientDict)
    else:
        patientDict = {
            'is_discharged': False,
            'patient': patient,
            'patientId': request.user.id,
        }
    return render(request, 'hospital/patient_discharge.html', context=patientDict)


# ------------------------ PATIENT RELATED VIEWS END ------------------------------
# ---------------------------------------------------------------------------------

