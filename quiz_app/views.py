from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from .models import Subject, Quiz, Question, Answer, Result, ResultDetail, QuizQuestion
from django.core.paginator import Paginator
from django.utils import timezone
import openpyxl

def home_view(request):
    now = timezone.now()

    subjects = Subject.objects.annotate(
        quiz_count=Count('quizzes')
    ).order_by('-quiz_count')[:3]
    
    featured_quizzes = Quiz.objects.annotate(
        attempt_count=Count(
            'result', 
            filter=Q(result__completed_at__year=now.year, result__completed_at__month=now.month),
            distinct=True
        ),
        question_count=Count('quiz_details', distinct=True)
    ).order_by('-attempt_count')[:3]

    context = {
        'subjects': subjects,
        'featured_quizzes': featured_quizzes
    }
    return render(request, 'quizzes/home.html', context)


def subject_list_view(request):
    query = request.GET.get('q', '')
    
    if query:
        subjects = Subject.objects.filter(subject_name__icontains=query).annotate(quiz_count=Count('quizzes'))
    else:
        subjects = Subject.objects.annotate(quiz_count=Count('quizzes'))
        
    context = {
        'subjects': subjects,
        'query': query
    }
    return render(request, 'quizzes/subject_list.html', context)


def add_subject(request):
    if request.method == 'POST':
        if request.user.is_authenticated and request.user.role == 'admin':
            s_name = request.POST.get('subject_name')
            s_image = request.FILES.get('image') 
            
            if Subject.objects.filter(subject_name=s_name).exists():
                messages.error(request, f'Subject "{s_name}" already exists!')
            else:
                Subject.objects.create(subject_name=s_name, image=s_image)
                messages.success(request, 'Subject added successfully!')
        else:
                messages.error(request, 'You do not have permission to perform this action.')
    return redirect('subject_list')


def delete_subject(request, subject_id):
    if request.method == 'POST':
        if request.user.is_authenticated and request.user.role == 'admin':
            subject = get_object_or_404(Subject, id=subject_id)
            subject.delete()
            messages.success(request, 'Subject deleted successfully!')
            
    return redirect('subject_list')


def search_view(request):
    query = request.GET.get('q', '').strip()
    quizzes = []

    if query:
        quizzes = Quiz.objects.filter(
            Q(title__icontains=query) | Q(subject__subject_name__icontains=query)
        ).annotate(
            question_count=Count('quiz_details', distinct=True) 
        ).order_by('-created_at')

    context = {
        'query': query,
        'quizzes': quizzes,
    }
    return render(request, 'quizzes/search.html', context)

def quiz_list_view(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    query = request.GET.get('q', '')
    
    quizzes = Quiz.objects.filter(subject=subject).annotate(question_count=Count('quiz_details'))

    if query:
        quizzes = quizzes.filter(title__icontains=query)
        
    context = {
        'subject': subject,
        'subject_name': subject.subject_name,
        'quizzes': quizzes,
        'query': query, 
    }
    return render(request, 'quizzes/quiz_list.html', context)

def create_quiz_view(request, subject_id):
    if request.user.is_authenticated and request.user.role == 'admin':
        subject = get_object_or_404(Subject, id=subject_id)
        
        existing_questions = Question.objects.filter(subject=subject).order_by('-id')

        if request.method == 'POST':
            upload_type = request.POST.get('upload_type') 

            if upload_type == 'excel':
                title = request.POST.get('quiz_title')
                duration = request.POST.get('quiz_duration')
                excel_file = request.FILES.get('excel_file')

                if not excel_file or not excel_file.name.endswith(('.xlsx', '.xls')):
                    messages.error(request, 'Please upload a valid Excel file (.xlsx)')
                    return redirect('create_quiz', subject_id=subject.id)

                quiz = Quiz.objects.create(subject=subject, title=title, duration=duration)

                wb = openpyxl.load_workbook(excel_file)
                sheet = wb.active

                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if not row[0]:  
                        continue
                    
                    q_content = str(row[0])
                    options = [row[1], row[2], row[3], row[4]]
                    options = [str(opt) for opt in options if opt is not None] 
                    
                    correct_val = str(row[5]).strip().upper() if row[5] is not None else '1'

                    if correct_val in ['A', 'B', 'C', 'D']:
                        mapping = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
                        correct_idx = mapping[correct_val]
                    else:
                        try:
                            correct_idx = int(float(correct_val)) - 1
                            correct_idx = max(0, min(correct_idx, 3))
                        except ValueError:
                            correct_idx = 0
                        
                    explanation = str(row[6]) if len(row) > 6 and row[6] else ''

                    question = Question.objects.create(subject=subject, content=q_content, explanation=explanation)
                    
                    QuizQuestion.objects.create(quiz=quiz, question=question)

                    for idx, opt_content in enumerate(options):
                        is_correct = (idx == correct_idx)
                        Answer.objects.create(question=question, content=opt_content, is_correct=is_correct)

                messages.success(request, 'Quiz created from Excel file successfully!')
                return redirect('quiz_list', subject_id=subject.id)

            elif upload_type == 'manual':
                title = request.POST.get('quiz_title')
                duration = request.POST.get('quiz_duration')
                total_questions = int(request.POST.get('total_questions', 0))

                quiz = Quiz.objects.create(subject=subject, title=title, duration=duration)

                for i in range(1, total_questions + 1):
                    q_content = request.POST.get(f'q_content_{i}')
                    q_explanation = request.POST.get(f'q_explanation_{i}', '')

                    if q_content:
                        question = Question.objects.create(subject=subject, content=q_content, explanation=q_explanation)
                        
                        QuizQuestion.objects.create(quiz=quiz, question=question)
                        
                        options = request.POST.getlist(f'q_opt_{i}')
                        correct_idx_str = request.POST.get(f'q_correct_{i}')
                        correct_idx = int(correct_idx_str) if correct_idx_str and correct_idx_str.isdigit() else 0

                        for opt_idx, opt_content in enumerate(options):
                            is_correct = (opt_idx == correct_idx)
                            Answer.objects.create(question=question, content=opt_content, is_correct=is_correct)

                messages.success(request, 'Quiz created manually successfully!')
                return redirect('quiz_list', subject_id=subject.id)

            elif upload_type == 'bank':
                title = request.POST.get('quiz_title')
                duration = request.POST.get('quiz_duration')
                selected_q_ids = request.POST.getlist('selected_questions') 
                
                if not selected_q_ids:
                    messages.error(request, 'Please select at least one question from the bank!')
                    return redirect('create_quiz', subject_id=subject.id)
                    
                quiz = Quiz.objects.create(subject=subject, title=title, duration=duration)
                
                for q_id in selected_q_ids:
                    question_obj = Question.objects.get(id=q_id)
                    QuizQuestion.objects.create(quiz=quiz, question=question_obj)
                    
                messages.success(request, 'Quiz created successfully from Question Bank!')
                return redirect('quiz_list', subject_id=subject.id)

        context = {
            'subject': subject,
            'existing_questions': existing_questions
        }
        return render(request, 'quizzes/create_quiz.html', context)

def edit_quiz_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if not (request.user.is_authenticated and request.user.role == 'admin'):
        messages.error(request, 'You do not have permission to edit this quiz.')
        return redirect('quiz_list', subject_id=quiz.subject.id)

    if request.method == 'POST':
        quiz.title = request.POST.get('quiz_title')
        quiz.duration = request.POST.get('quiz_duration')
        quiz.save()

        total_questions = int(request.POST.get('total_questions', 0))

        quiz.questions.all().delete()

        for i in range(1, total_questions + 1):
            q_content = request.POST.get(f'q_content_{i}')
            q_explanation = request.POST.get(f'q_explanation_{i}', '')

            if q_content:
                question = Question.objects.create(quiz=quiz, content=q_content, explanation=q_explanation)
                options = request.POST.getlist(f'q_opt_{i}')
                correct_idx_str = request.POST.get(f'q_correct_{i}')
                correct_idx = int(correct_idx_str) if correct_idx_str and correct_idx_str.isdigit() else 0

                for opt_idx, opt_content in enumerate(options):
                    is_correct = (opt_idx == correct_idx)
                    Answer.objects.create(question=question, content=opt_content, is_correct=is_correct)

        messages.success(request, 'Quiz updated successfully!')
        return redirect('quiz_list', subject_id=quiz.subject.id)

    return render(request, 'quizzes/edit_quiz.html', {'quiz': quiz})


def delete_quiz(request, quiz_id):
    if request.user.is_authenticated and request.user.role == 'admin':
        if request.method == 'POST':
            if request.user.is_authenticated and request.user.role == 'admin':
                quiz = get_object_or_404(Quiz, id=quiz_id)
                subject_id = quiz.subject.id 
                quiz.delete()
                messages.success(request, 'Quiz deleted successfully!')
                return redirect('quiz_list', subject_id=subject_id)
            else:
                messages.error(request, 'You do not have permission to perform this action.')
                
        return redirect('subject_list') 

def exam_view(request, quiz_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    questions = Question.objects.filter(used_in_quizzes__quiz=quiz).prefetch_related('answers')

    if request.method == 'POST':
        score = 0
        total_questions = questions.count()
        user_choices = {} 
        
        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            
            if selected_answer_id:
                user_choices[question.id] = selected_answer_id 
                
                is_correct = Answer.objects.filter(id=selected_answer_id, question=question, is_correct=True).exists()
                if is_correct:
                    score += 1
        
        final_score = (score / total_questions * 10) if total_questions > 0 else 0
        time_spent = int(request.POST.get('time_spent', 0))

        result = Result.objects.create(
            user=request.user,
            quiz=quiz,
            score=final_score,
            time_spent=time_spent
        )
        
        for question in questions:
            ans_id = user_choices.get(question.id)
            selected_ans = Answer.objects.filter(id=ans_id).first() if ans_id else None
            ResultDetail.objects.create(
                result=result,
                question=question,
                selected_answer=selected_ans
            )
        
        return redirect('result', result_id=result.id)

    context = {
        'quiz': quiz,
        'questions': questions
    }
    return render(request, 'quizzes/exam.html', context)


def result_view(request, result_id):
    result = get_object_or_404(Result, id=result_id, user=request.user)
    return render(request, 'quizzes/result.html', {'result': result})

def review_view(request, result_id):
    result = get_object_or_404(Result, id=result_id, user=request.user)
    
    result_details = result.result_details.select_related('question', 'selected_answer').all()
    
    review_data = []
    for detail in result_details:
        q = detail.question
        review_data.append({
            'question': q,
            'options': q.answers.all(),
            'selected_answer_id': detail.selected_answer.id if detail.selected_answer else None,
        })

    return render(request, 'quizzes/review.html', {'result': result, 'review_data': review_data})



def history_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'newest')
    
    results = Result.objects.filter(user=request.user)
    
    if query:
        results = results.filter(quiz__title__icontains=query)
        
    if sort == 'newest':
        results = results.order_by('-completed_at')
    else:
        results = results.order_by('completed_at')
        
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1)
    entries = []
    for r in page_obj:
        total_q = r.quiz.quiz_details.count()   
        correct_q = int(round(float(r.score) / 10.0 * total_q)) if total_q > 0 else 0
        percent = int(float(r.score) * 10)
        
        entries.append({
            'id': r.id,
            'quiz_id': r.quiz.id,
            'title': r.quiz.title,
            'time': r.completed_at.strftime("%d/%m/%Y %H:%M"),
            'percent': percent,
            'correct': correct_q,
            'total': total_q,
            'score': r.score
        })
        
    context = {
        'page_obj': page_obj,
        'page_range': page_range,
        'entries': entries,
        'query': query,
        'sort': sort,
    }
    return render(request, 'quizzes/history.html', context)
