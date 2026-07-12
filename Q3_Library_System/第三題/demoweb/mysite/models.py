from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# 書籍模型
class Book(models.Model):
    title     = models.CharField(max_length=200)        # 書名
    author    = models.CharField(max_length=100)        # 作者
    isbn      = models.CharField(max_length=20, unique=True)  # ISBN
    quantity  = models.IntegerField(default=1)          # 總數量
    available = models.IntegerField(default=1)          # 可借數量

    def __str__(self):
        return self.title

# 借閱記錄模型
class BorrowRecord(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE)
    book        = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)   # 借閱日期
    due_date    = models.DateTimeField()                     # 到期日期
    return_date = models.DateTimeField(null=True, blank=True)  # 歸還日期
    is_returned = models.BooleanField(default=False)         # 是否已還
    
    # 是否逾期
    @property
    def is_overdue(self):
        if self.is_returned:
            return False
        return timezone.now() > self.due_date

    def save(self, *args, **kwargs):
        # 自動設定到期日為借閱後14天
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} 借了 {self.book.title}'