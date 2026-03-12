from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from .models import Subject, Quiz, Question, Answer, Result

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
                messages.error(request, f'Môn học "{s_name}" đã tồn tại!')
            else:
                # Lưu cả tên và ảnh vào database
                Subject.objects.create(subject_name=s_name, image=s_image)
                messages.success(request, 'Thêm môn học thành công!')
        else:
            messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')
            
    return redirect('subject_list')

# 3. Xóa môn học
def delete_subject(request, subject_id):
    if request.method == 'POST':
        if request.user.is_authenticated and request.user.role == 'admin':
            subject = get_object_or_404(Subject, id=subject_id)
            subject.delete()
            messages.success(request, 'Đã xóa môn học thành công!')
            
    return redirect('subject_list')



def home_view(request):
    # Sau này dữ liệu từ bảng Subjects và Quizzes sẽ được lấy ở đây
    return render(request, 'quizzes/home.html')


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

        messages.success(request, 'Đã tạo đề thi thành công!')
        return redirect('quiz_list', subject_id=subject.id)

    return render(request, 'quizzes/create_quiz.html', {'subject': subject})

def edit_quiz_view(request, quiz_id):
    # Lấy đề thi cần sửa
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    # Chỉ Admin mới được sửa
    if not (request.user.is_authenticated and request.user.role == 'admin'):
        messages.error(request, 'Bạn không có quyền sửa đề thi này.')
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

        messages.success(request, 'Cập nhật đề thi thành công!')
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
            messages.success(request, 'Đã xóa đề thi thành công!')
            return redirect('quiz_list', subject_id=subject_id)
        else:
            messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')
            
    return redirect('subject_list') # Nếu không phải POST thì đẩy về trang môn học


def exam_view(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # Lấy tất cả câu hỏi của đề thi, prefetch_related giúp lấy đáp án nhanh hơn
    questions = quiz.questions.all().prefetch_related('answers')

    if request.method == 'POST':
        score = 0
        total_questions = questions.count()
        
        # 1. Chấm điểm
        for question in questions:
            # Lấy ID của đáp án mà sinh viên chọn cho câu hỏi này
            selected_answer_id = request.POST.get(f'question_{question.id}')
            
            if selected_answer_id:
                # Kiểm tra xem đáp án đó có thuộc về câu hỏi này và có is_correct=True không
                is_correct = Answer.objects.filter(id=selected_answer_id, question=question, is_correct=True).exists()
                if is_correct:
                    score += 1
        
        # Tính điểm hệ 10 (Ví dụ: đúng 8/10 câu -> 8.0 điểm)
        final_score = (score / total_questions * 10) if total_questions > 0 else 0
        
        # Lấy thời gian làm bài (được JS truyền lên)
        time_spent = int(request.POST.get('time_spent', 0))

        # 2. Lưu kết quả vào DB
        result = Result.objects.create(
            user=request.user,
            quiz=quiz,
            score=final_score,
            time_spent=time_spent
        )
        
        # 3. Chuyển hướng sang trang kết quả
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





def history_view(request):
    # dummy history entries
    entries = [
        {'title': 'Bài tập trắc nghiệm thì hiện tại đơn (Simple Present) online',
         'time': '14:24 02/02/2026', 'correct': 5, 'total': 20},
        {'title': 'Bài tập trắc nghiệm thì hiện tại tiếp diễn (Present Continuous) online',
         'time': '14:27 02/02/2026', 'correct': 17, 'total': 20},
        {'title': 'Thi thử trắc nghiệm ôn tập môn Pháp luật Đại Cương online - Đề #1',
         'time': '00:41 02/02/2026', 'correct': 0, 'total': 40},
        {'title': 'Thi thử trắc nghiệm ôn tập môn Tư tưởng Hồ Chí Minh online - Chương 6 - Đề 64',
         'time': '18:23 25/01/2026', 'correct': 6, 'total': 25},
        {'title': 'Thi thử trắc nghiệm ôn tập triết học Mác Lênin online - Chương 1 - Đề #42',
         'time': '16:52 25/01/2026', 'correct': 4, 'total': 25},
    ]
    query = request.GET.get('q', '').strip()
    if query:
        entries = [e for e in entries if query.lower() in e['title'].lower()]
    # compute percentage for display
    for e in entries:
        e['percent'] = int(e['correct'] * 100 / e['total']) if e['total'] else 0
    # sorting not implemented but placeholder param
    sort = request.GET.get('sort','')
    return render(request, 'quizzes/history.html', {'entries': entries, 'query': query, 'sort': sort})
