from django.shortcuts import render


def home_view(request):
    # Sau này dữ liệu từ bảng Subjects và Quizzes sẽ được lấy ở đây
    return render(request, 'quizzes/home.html')

def subject_list_view(request):
    # Dữ liệu giả (Dummy data) để hiển thị giao diện
    dummy_subjects = [
        {'subject_name': 'Marxist-Leninist Philosophy', 'quiz_count': 80},
        {'subject_name': 'Ho Chi Minh Ideology', 'quiz_count': 72},
        {'subject_name': 'General Law', 'quiz_count': 63},
    ]
    
    # Gửi dummy_subjects sang template
    return render(request, 'quizzes/subject_list.html', {'subjects': dummy_subjects})

def quiz_list_view(request):
    # Dữ liệu giả cho danh sách đề thi
    subject_name = request.GET.get('subject', 'Ho Chi Minh Ideology')
    dummy_quizzes = [
        {
            'id': 1,
            'title': 'Practice Test on Ho Chi Minh Ideology Online - Chapter 6 - Test 84',
            'subject': 'Ho Chi Minh Ideology',
            'questions': 25,
            'duration': 30,
        },
        {
            'id': 2,
            'title': 'Practice Test on Ho Chi Minh Ideology Online - Chapter 6 - Test 63',
            'subject': 'Ho Chi Minh Ideology',
            'questions': 24,
            'duration': 30,
        },
        {
            'id': 3,
            'title': 'Practice Test on Ho Chi Minh Ideology Online - Chapter 6 - Test 62',
            'subject': 'Ho Chi Minh Ideology',
            'questions': 25,
            'duration': 30,
        },
        {
            'id': 4,
            'title': 'Practice Test on Ho Chi Minh Ideology Online - Chapter 5 - Test 61',
            'subject': 'Ho Chi Minh Ideology',
            'questions': 25,
            'duration': 30,
        },
        {
            'id': 5,
            'title': 'Practice Test on Ho Chi Minh Ideology Online - Chapter 1 - Test 48',
            'subject': 'Ho Chi Minh Ideology',
            'questions': 24,
            'duration': 30,
        },
    ]
    
    return render(request, 'quizzes/quiz_list.html', {
        'subject_name': subject_name,
        'quizzes': dummy_quizzes
    })

def create_quiz_view(request):
    # placeholder for quiz creation interface
    return render(request, 'quizzes/create_quiz.html')


def exam_view(request, quiz_id):
    # dummy quiz data
    quiz = {
        'id': quiz_id,
        'title': 'Bài tập trắc nghiệm thì hiện tại tiếp diễn (Present Continuous) online',
        'question_count': 20,
        'duration': '--',
        'language': 'Tiếng Anh',
        'questions': [
            {'text': 'Gordon? I think he ______ a letter at the moment',
             'options': ['is writing', 'write', 'wrote', 'written']},
            {'text': 'Yes, the match is on TV now, but we ______',
             'options': ['lost', 'are losing', 'is losing', 'are lose']},
            {'text': 'I ______ drinking apple juice.',
             'options': ['likes', 'am liking', 'like', 'am like']},
            {'text': 'They ______ with us at the moment.',
             'options': ['staying', 'stay', 'are staying', 'are stay']},
            {'text': 'Listen! The teacher ______.',
             'options': ['speak', 'is speaking', 'speaks', 'spoken']},
            {'text': 'Maxwell ______ not sleeping on our sofa.',
             'options': ['is', 'are', 'am', '']},
        ]
    }
    return render(request, 'quizzes/exam.html', {'quiz': quiz})


def result_view(request, quiz_id):
    # dummy result data
    result = {
        'title': 'Bài tập trắc nghiệm thì hiện tại tiếp diễn (Present Continuous) online',
        'duration': 40,
        'score': 8.5,
        'total': 10
    }
    return render(request, 'quizzes/result.html', {'result': result})
