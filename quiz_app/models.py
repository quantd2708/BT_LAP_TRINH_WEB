from django.db import models
from django.conf import settings # Dùng để gọi CustomUser

# Bảng Subjects (Danh mục môn học)
class Subject(models.Model):
    subject_name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='subject_images/', blank=True, null=True)
    
    def __str__(self):
        return self.subject_name

# Bảng Quizzes (Đề thi)
class Quiz(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    duration = models.IntegerField(default=45) # phút
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

# Bảng Questions (Câu hỏi)
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    content = models.TextField()
    explanation = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Câu hỏi của đề: {self.quiz.title}"

# Bảng Answers (Các phương án trả lời)
class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    is_correct = models.BooleanField(default=False)

# Bảng Results (Lịch sử làm bài)
class Result(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    time_spent = models.IntegerField() # giây
    completed_at = models.DateTimeField(auto_now_add=True)