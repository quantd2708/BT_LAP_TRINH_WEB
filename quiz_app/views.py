from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from .models import Subject, Quiz, Question, Answer, Result, ResultDetail
from django.core.paginator import Paginator
from django.utils import timezone

def home_view(request):
    # Lấy thời gian hiện tại (Năm và Tháng)
    now = timezone.now()

    # 1. Lấy 3 môn học (Giữ nguyên)
    subjects = Subject.objects.annotate(
        quiz_count=Count('quizzes')
    ).order_by('-quiz_count')[:3]
    
    # 2. Lấy 3 đề thi được làm nhiều nhất TRONG THÁNG NÀY
    featured_quizzes = Quiz.objects.annotate(
        attempt_count=Count(
            'result', 
            # THÊM ĐIỀU KIỆN LỌC (FILTER) VÀO ĐÂY:
            filter=Q(result__completed_at__year=now.year, result__completed_at__month=now.month),
            distinct=True
        ),
        question_count=Count('questions', distinct=True)
    ).order_by('-attempt_count')[:3]

    context = {
        'subjects': subjects,
        'featured_quizzes': featured_quizzes
    }
    return render(request, 'quizzes/home.html', context)

# 1. Hiển thị danh sách & Tìm kiếm
def subject_list_view(request):
    query = request.GET.get('q', '')
    
    # Lấy danh sách môn học và ĐẾM số lượng Quiz thuộc về môn đó
    if query:
        subjects = Subject.objects.filter(subject_name__icontains=query).annotate(quiz_count=Count('quizzes'))
    else:
        subjects = Subject.objects.annotate(quiz_count=Count('quizzes'))
        
    context = {
        'subjects': subjects,
        'query': query
    }
    return render(request, 'quizzes/subject_list.html', context)

# 2. Thêm môn học mới
def add_subject(request):
    if request.method == 'POST':
        if request.user.is_authenticated and request.user.role == 'admin':
            s_name = request.POST.get('subject_name')
            # Lấy file ảnh từ form gửi lên
            s_image = request.FILES.get('image') 
            
            if Subject.objects.filter(subject_name=s_name).exists():
                messages.error(request, f'Subject "{s_name}" already exists!')
            else:
                # Lưu cả tên và ảnh vào database
                Subject.objects.create(subject_name=s_name, image=s_image)
                messages.success(request, 'Subject added successfully!')
        else:
                messages.error(request, 'You do not have permission to perform this action.')
    return redirect('subject_list')

# 3. Xóa môn học
def delete_subject(request, subject_id):
    if request.method == 'POST':
        if request.user.is_authenticated and request.user.role == 'admin':
            subject = get_object_or_404(Subject, id=subject_id)
            subject.delete()
            messages.success(request, 'Subject deleted successfully!')
            
    return redirect('subject_list')

def search_view(request):
    # quiz search results page
    q = request.GET.get('q', '').strip()
    # dummy quizzes (could be filtered by q)
    dummy_quizzes = [
        {'title': 'toán đh', 'questions': 25, 'duration': 45},
        {'title': 'BÀI 9: GIAO TIẾP AN TOÀN TRÊN INTERNET', 'questions': 50, 'duration': 45},
        {'title': 'Trắc nghiệm kế toán lương 3', 'questions': 20, 'duration': 45},
        {'title': 'TRẮC NGHIỆM KẾ TOÁN LƯƠNG', 'questions': 20, 'duration': 45},
        {'title': 'Trắc nghiệm kế toán lương và các khoản trích theo lương', 'questions': 20, 'duration': 45},
        {'title': 'Đề thi thử tốt nghiệp THPT 2025 môn Toán -THPT Yên Lạc - Vĩnh Phúc', 'questions': 22, 'duration': 90},
    ]
    if q:
        dummy_quizzes = [z for z in dummy_quizzes if q.lower() in z['title'].lower()]
    return render(request, 'quizzes/search.html', {'quizzes': dummy_quizzes, 'query': q})

def quiz_list_view(request, subject_id):
    # Lấy thông tin môn học
    subject = get_object_or_404(Subject, id=subject_id)
    
    # Lấy danh sách đề thi của môn học này và đếm số câu hỏi
    quizzes = Quiz.objects.filter(subject=subject).annotate(question_count=Count('questions'))
    
    context = {
        'subject': subject,
        'subject_name': subject.subject_name,
        'quizzes': quizzes,
    }
    return render(request, 'quizzes/quiz_list.html', context)

def create_quiz_view(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)

    if request.method == 'POST':
        # 1. Lấy thông tin chung của đề thi
        title = request.POST.get('quiz_title')
        duration = request.POST.get('quiz_duration')
        total_questions = int(request.POST.get('total_questions', 0))

        # 2. Lưu Đề thi (Quiz) vào DB
        quiz = Quiz.objects.create(
            subject=subject,
            title=title,
            duration=duration,
            created_by=request.user
        )

        # 3. Duyệt qua từng câu hỏi được gửi lên
        for i in range(1, total_questions + 1):
            q_content = request.POST.get(f'q_content_{i}')
            q_explanation = request.POST.get(f'q_explanation_{i}', '')

            if q_content:
                # Lưu Câu hỏi (Question)
                question = Question.objects.create(
                    quiz=quiz, 
                    content=q_content, 
                    explanation=q_explanation
                )

                # Lấy danh sách các đáp án (options) của câu hỏi này
                options = request.POST.getlist(f'q_opt_{i}')
                # Lấy index của đáp án đúng (0, 1, 2...)
                correct_idx_str = request.POST.get(f'q_correct_{i}')
                correct_idx = int(correct_idx_str) if correct_idx_str and correct_idx_str.isdigit() else 0

                # 4. Lưu các Đáp án (Answer)
                for opt_idx, opt_content in enumerate(options):
                    is_correct = (opt_idx == correct_idx)
                    Answer.objects.create(
                        question=question,
                        content=opt_content,
                        is_correct=is_correct
                    )

        messages.success(request, 'Quiz created successfully!')
        return redirect('quiz_list', subject_id=subject.id)

    return render(request, 'quizzes/create_quiz.html', {'subject': subject})

def edit_quiz_view(request, quiz_id):
    # Lấy đề thi cần sửa
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Chỉ Admin mới được sửa
    if not (request.user.is_authenticated and request.user.role == 'admin'):
        messages.error(request, 'You do not have permission to edit this quiz.')
        return redirect('quiz_list', subject_id=quiz.subject.id)

    if request.method == 'POST':
        # 1. Cập nhật thông tin cơ bản của Quiz
        quiz.title = request.POST.get('quiz_title')
        quiz.duration = request.POST.get('quiz_duration')
        quiz.save()

        total_questions = int(request.POST.get('total_questions', 0))

        # 2. XÓA TOÀN BỘ CÂU HỎI CŨ ĐỂ LÀM LẠI TỪ ĐẦU (Tránh rác DB)
        quiz.questions.all().delete()

        # 3. Tạo lại các câu hỏi dựa trên Form gửi lên (Giống hệt lúc Create)
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

# Hàm Xóa đề thi
def delete_quiz(request, quiz_id):
    if request.method == 'POST':
        # Chỉ Admin mới được quyền xóa
        if request.user.is_authenticated and request.user.role == 'admin':
            quiz = get_object_or_404(Quiz, id=quiz_id)
            subject_id = quiz.subject.id # Lưu lại ID môn học để lát nữa quay về đúng trang
            quiz.delete()
            messages.success(request, 'Quiz deleted successfully!')
            return redirect('quiz_list', subject_id=subject_id)
        else:
            messages.error(request, 'You do not have permission to perform this action.')
            
    return redirect('subject_list') # Nếu không phải POST thì đẩy về trang môn học

# Thêm hàm này vào views.py
def exam_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # Lấy tất cả câu hỏi của đề thi, prefetch_related giúp lấy đáp án nhanh hơn
    questions = quiz.questions.all().prefetch_related('answers')

    if request.method == 'POST':
        score = 0
        total_questions = questions.count()
        
        # Tạo một dictionary để tạm lưu các đáp án user đã chọn
        user_choices = {} 
        
        # 1. Chấm điểm
        for question in questions:
            selected_answer_id = request.POST.get(f'question_{question.id}')
            
            if selected_answer_id:
                # Lưu lại lựa chọn này vào dictionary
                user_choices[question.id] = selected_answer_id 
                
                is_correct = Answer.objects.filter(id=selected_answer_id, question=question, is_correct=True).exists()
                if is_correct:
                    score += 1
        
        # Tính điểm hệ 10
        final_score = (score / total_questions * 10) if total_questions > 0 else 0
        time_spent = int(request.POST.get('time_spent', 0))

        # 2. Lưu kết quả tổng vào DB (Bảng Results)
        result = Result.objects.create(
            user=request.user,
            quiz=quiz,
            score=final_score,
            time_spent=time_spent
        )
        
        # 3. LƯU CHI TIẾT TỪNG ĐÁP ÁN (Bảng ResultDetails) - ĐÂY LÀ PHẦN BẠN THIẾU
        for question in questions:
            ans_id = user_choices.get(question.id)
            selected_ans = Answer.objects.filter(id=ans_id).first() if ans_id else None
            ResultDetail.objects.create(
                result=result,
                question=question,
                selected_answer=selected_ans
            )
        
        # 4. Chuyển hướng sang trang kết quả
        return redirect('result', result_id=result.id)

    context = {
        'quiz': quiz,
        'questions': questions
    }
    return render(request, 'quizzes/exam.html', context)
# Hàm hiển thị trang kết quả
def result_view(request, result_id):
    # Chỉ cho phép người dùng xem kết quả của chính họ
    result = get_object_or_404(Result, id=result_id, user=request.user)
    return render(request, 'quizzes/result.html', {'result': result})

# HÀM XEM LẠI BÀI THI
def review_view(request, result_id):
    # Lấy kết quả của user hiện tại
    result = get_object_or_404(Result, id=result_id, user=request.user)
    
    # Lấy chi tiết các câu trả lời thông qua related_name='result_details'
    result_details = result.result_details.select_related('question', 'selected_answer').all()
    
    review_data = []
    for detail in result_details:
        q = detail.question
        review_data.append({
            'question': q,
            'options': q.answers.all(),
            # Nếu user có chọn đáp án thì lấy ID, không thì để None
            'selected_answer_id': detail.selected_answer.id if detail.selected_answer else None,
        })

    return render(request, 'quizzes/review.html', {'result': result, 'review_data': review_data})



# Cập nhật hàm history_view
def history_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    query = request.GET.get('q', '')
    sort = request.GET.get('sort', 'newest')
    
    # Lấy toàn bộ lịch sử của người dùng này
    results = Result.objects.filter(user=request.user)
    
    # Xử lý tìm kiếm
    if query:
        results = results.filter(quiz__title__icontains=query)
        
    # Xử lý sắp xếp
    if sort == 'newest':
        results = results.order_by('-completed_at')
    else:
        results = results.order_by('completed_at')
        
    # Phân trang: 10 bài / trang
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1)
    # Tính toán thông số (số câu đúng, %) cho trang hiện tại
    entries = []
    for r in page_obj:
        total_q = r.quiz.questions.count()
        # Tính số câu đúng dựa trên điểm hệ 10
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
