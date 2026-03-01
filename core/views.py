from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import admin_required, login_required_custom
from .forms import (
    AddStudentForm,
    GroupForm,
    LoginForm,
    PasswordChangeForm,
    RatingForm,
    SurveyForm,
)
from .models import Group, Rating, Student, Survey
from .utils import export_detail_excel, export_summary_excel, import_students_from_excel


# ─── Authentication ────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('survey')

    form = LoginForm(request.POST or None)
    error = None

    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password'],
        )
        if user is not None:
            login(request, user)
            return redirect('survey')
        else:
            error = 'Kullanıcı adı veya şifre hatalı.'

    return render(request, 'login.html', {'form': form, 'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


# ─── Student Views ─────────────────────────────────────────────────────────────

@login_required_custom
def survey_view(request):
    active_survey = Survey.objects.filter(is_active=True).first()

    if not active_survey:
        return render(request, 'survey.html', {'no_survey': True})

    student = request.user

    # Get group peers (excluding self)
    if not student.group:
        return render(request, 'survey.html', {'no_group': True, 'survey': active_survey})

    peers = Student.objects.filter(group=student.group).exclude(pk=student.pk).order_by('last_name', 'first_name')

    if not peers.exists():
        return render(request, 'survey.html', {'no_peers': True, 'survey': active_survey})

    # Check if already rated all peers
    existing_ratings = Rating.objects.filter(survey=active_survey, rater=student)
    rated_ids = set(existing_ratings.values_list('ratee_id', flat=True))
    peer_ids = set(peers.values_list('pk', flat=True))

    if peer_ids.issubset(rated_ids):
        return render(request, 'survey.html', {'completed': True, 'survey': active_survey})

    if request.method == 'POST':
        forms = []
        valid = True
        for peer in peers:
            form = RatingForm(request.POST, prefix=f'peer_{peer.pk}')
            form.peer = peer
            if not form.is_valid():
                valid = False
            forms.append(form)

        if valid:
            try:
                with transaction.atomic():
                    for form in forms:
                        peer_id = form.cleaned_data['ratee_id']
                        score = int(form.cleaned_data['score'])
                        comment = form.cleaned_data.get('comment', '')

                        if peer_id == student.pk:
                            continue  # safety check

                        Rating.objects.update_or_create(
                            survey=active_survey,
                            rater=student,
                            ratee_id=peer_id,
                            defaults={'score': score, 'comment': comment},
                        )
                messages.success(request, 'Değerlendirmeleriniz kaydedildi.')
                return redirect('survey')
            except IntegrityError:
                messages.error(request, 'Bir hata oluştu, lütfen tekrar deneyin.')
        else:
            peer_forms = list(zip(peers, forms))
            return render(request, 'survey.html', {
                'survey': active_survey,
                'peer_forms': peer_forms,
            })

    # Build forms for each peer
    forms = []
    for peer in peers:
        existing = existing_ratings.filter(ratee=peer).first()
        initial = {}
        if existing:
            initial = {'ratee_id': peer.pk, 'score': existing.score, 'comment': existing.comment}
        else:
            initial = {'ratee_id': peer.pk}
        form = RatingForm(initial=initial, prefix=f'peer_{peer.pk}')
        form.peer = peer
        forms.append(form)

    peer_forms = list(zip(peers, forms))
    return render(request, 'survey.html', {
        'survey': active_survey,
        'peer_forms': peer_forms,
    })


@login_required_custom
def profile_view(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Şifreniz başarıyla değiştirildi.')
            return redirect('profile')
        else:
            messages.error(request, 'Lütfen formu doğru doldurun.')

    return render(request, 'profile.html', {'form': form})


# ─── Admin Panel Views ─────────────────────────────────────────────────────────

@admin_required
def dashboard_view(request):
    total_students = Student.objects.filter(is_staff=False).count()
    total_groups = Group.objects.count()
    active_survey = Survey.objects.filter(is_active=True).first()

    context = {
        'total_students': total_students,
        'total_groups': total_groups,
        'active_survey': active_survey,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def groups_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            form = GroupForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Grup oluşturuldu.')
            else:
                messages.error(request, 'Grup adı geçersiz veya zaten mevcut.')

        elif action == 'delete':
            group_id = request.POST.get('group_id')
            group = get_object_or_404(Group, pk=group_id)
            group.delete()
            messages.success(request, f'"{group.name}" grubu silindi.')

        elif action == 'assign':
            student_id = request.POST.get('student_id')
            group_id = request.POST.get('group_id')
            student = get_object_or_404(Student, pk=student_id)
            group = get_object_or_404(Group, pk=group_id) if group_id else None
            student.group = group
            student.save()
            messages.success(request, f'{student.get_full_name()} gruba atandı.')

        return redirect('groups')

    groups = Group.objects.annotate(student_count=Count('students')).order_by('name')
    students = Student.objects.filter(is_staff=False).select_related('group').order_by('last_name', 'first_name')
    form = GroupForm()

    return render(request, 'admin_panel/groups.html', {
        'groups': groups,
        'students': students,
        'form': form,
    })


@admin_required
def students_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            form = AddStudentForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                if Student.objects.filter(username=cd['username']).exists():
                    messages.error(request, f"'{cd['username']}' kullanıcı adı zaten mevcut.")
                else:
                    student = Student(
                        username=cd['username'],
                        first_name=cd['first_name'],
                        last_name=cd['last_name'],
                        ogrenci_no=cd['ogrenci_no'],
                        group=cd['group'],
                    )
                    student.set_password(cd['ogrenci_no'])
                    student.save()
                    messages.success(request, f'{student.get_full_name()} eklendi.')
            else:
                messages.error(request, 'Form hataları var.')

        elif action == 'delete':
            student_id = request.POST.get('student_id')
            student = get_object_or_404(Student, pk=student_id)
            name = student.get_full_name()
            student.delete()
            messages.success(request, f'{name} silindi.')

        elif action == 'import':
            excel_file = request.FILES.get('excel_file')
            if not excel_file:
                messages.error(request, 'Dosya seçilmedi.')
            else:
                try:
                    result = import_students_from_excel(excel_file)
                    messages.success(
                        request,
                        f"{result['added_count']} öğrenci eklendi, {result['error_count']} hata."
                    )
                    for detail in result['error_details']:
                        messages.warning(request, detail)
                except Exception as e:
                    messages.error(request, f'Excel okuma hatası: {str(e)}')

        return redirect('students')

    qs = Student.objects.filter(is_staff=False).select_related('group').order_by('last_name', 'first_name')
    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin_panel/students.html', {
        'page_obj': page_obj,
        'add_form': AddStudentForm(),
        'groups': Group.objects.all().order_by('name'),
    })


@admin_required
def survey_list_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            form = SurveyForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'Anket oluşturuldu.')
            else:
                messages.error(request, 'Anket adı geçersiz.')

        elif action == 'toggle':
            survey_id = request.POST.get('survey_id')
            survey = get_object_or_404(Survey, pk=survey_id)
            survey.is_active = not survey.is_active
            survey.save()  # Survey.save() handles deactivating others
            status = 'aktif edildi' if survey.is_active else 'pasif edildi'
            messages.success(request, f'"{survey.lesson_name}" {status}.')

        elif action == 'delete':
            survey_id = request.POST.get('survey_id')
            survey = get_object_or_404(Survey, pk=survey_id)
            name = survey.lesson_name
            survey.delete()
            messages.success(request, f'"{name}" anketi silindi.')

        return redirect('survey_list')

    surveys = Survey.objects.annotate(rating_count=Count('ratings')).order_by('-created_at')
    return render(request, 'admin_panel/survey_list.html', {
        'surveys': surveys,
        'form': SurveyForm(),
    })


@admin_required
def results_view(request):
    surveys = Survey.objects.all().order_by('-created_at')
    survey_id = request.GET.get('survey_id')
    selected_survey = None
    groups_data = []

    if survey_id:
        selected_survey = get_object_or_404(Survey, pk=survey_id)

        # Export endpoints
        export = request.GET.get('export')
        if export == 'summary':
            return export_summary_excel(selected_survey)
        elif export == 'detail':
            return export_detail_excel(selected_survey)

        # Build per-group, per-student breakdown
        groups = Group.objects.filter(students__isnull=False).distinct().order_by('name')

        for group in groups:
            group_students = Student.objects.filter(group=group, is_staff=False).order_by('last_name', 'first_name')
            students_data = []

            for student in group_students:
                received = Rating.objects.filter(survey=selected_survey, ratee=student).select_related('rater')
                scores = [r.score for r in received]
                avg = round(sum(scores) / len(scores), 2) if scores else None

                # Who has rated this student
                rated_by = [{'rater': r.rater, 'score': r.score, 'comment': r.comment} for r in received]

                # Who hasn't rated this student (peers who should have)
                peers = Student.objects.filter(group=group, is_staff=False).exclude(pk=student.pk)
                rated_rater_ids = set(r.rater_id for r in received)
                not_rated_by = [p for p in peers if p.pk not in rated_rater_ids]

                students_data.append({
                    'student': student,
                    'avg': avg,
                    'rated_by': rated_by,
                    'not_rated_by': not_rated_by,
                    'rated_count': len(rated_by),
                    'not_rated_count': len(not_rated_by),
                })

            groups_data.append({'group': group, 'students': students_data})

    return render(request, 'admin_panel/results.html', {
        'surveys': surveys,
        'selected_survey': selected_survey,
        'groups_data': groups_data,
        'survey_id': survey_id,
    })
