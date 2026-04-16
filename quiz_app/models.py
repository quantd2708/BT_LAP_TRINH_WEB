from django.db import models
from django.conf import settings 

class Subject(models.Model):
    subject_name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to='subject_images/', blank=True, null=True)
    
    def __str__(self):
        return self.subject_name
    
    class Meta:
        db_table = 'Subjects'

class Quiz(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    duration = models.IntegerField(default=45) # phút
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'Quizzes'

class Question(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='question_bank')
    content = models.TextField()
    explanation = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.subject.subject_name}"
    
    class Meta:
        db_table = 'Questions'

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    is_correct = models.BooleanField(default=False)

    class Meta:
        db_table = 'Answers'

class Result(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    time_spent = models.IntegerField() # giây
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Results'
    
class ResultDetail(models.Model): 
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='result_details')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'ResultDetails'
        
class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_details')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='used_in_quizzes')

    class Meta:
        db_table = 'QuizQuestions'
        unique_together = ('quiz', 'question')

    def __str__(self):
        return f"{self.quiz.title}"