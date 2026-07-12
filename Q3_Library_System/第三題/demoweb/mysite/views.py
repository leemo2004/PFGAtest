from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from .models import Book, BorrowRecord
import ollama
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import BookSerializer, BorrowRecordSerializer

@api_view(['GET'])
def api_book_list(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response({
        'status': 'success',
        'data': serializer.data
    })

# API：取得單本書籍
@api_view(['GET'])
def api_book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    serializer = BookSerializer(book)
    return Response({
        'status': 'success',
        'data': serializer.data
    })

# API：借書
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_borrow_book(request):
    book_id = request.data.get('book_id')
    book = get_object_or_404(Book, id=book_id)

    # 檢查借閱數量
    current_borrow_count = BorrowRecord.objects.filter(
        user=request.user,
        is_returned=False
    ).count()

    if current_borrow_count >= 5:
        return Response({
            'status': 'error',
            'message': '已達到最大借閱數量（5本）'
        }, status=status.HTTP_400_BAD_REQUEST)

    if book.available > 0:
        record = BorrowRecord.objects.create(
            user=request.user,
            book=book
        )
        book.available -= 1
        book.save()
        serializer = BorrowRecordSerializer(record)
        return Response({
            'status': 'success',
            'message': f'成功借閱《{book.title}》（目前借閱：{current_borrow_count + 1}/5本）',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'status': 'error',
            'message': '此書目前無庫存'
        }, status=status.HTTP_400_BAD_REQUEST)

# API：還書
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_return_book(request, record_id):
    record = get_object_or_404(
        BorrowRecord,
        id=record_id,
        user=request.user
    )

    if record.is_returned:
        return Response({
            'status': 'error',
            'message': '此書已經歸還'
        }, status=status.HTTP_400_BAD_REQUEST)

    record.is_returned = True
    record.return_date = timezone.now()
    record.save()
    record.book.available += 1
    record.book.save()

    serializer = BorrowRecordSerializer(record)
    return Response({
        'status': 'success',
        'message': f'成功歸還《{record.book.title}》',
        'data': serializer.data
    })

# API：我的借閱記錄
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_my_books(request):
    records = BorrowRecord.objects.filter(
        user=request.user,
        is_returned=False
    )
    serializer = BorrowRecordSerializer(records, many=True)
    return Response({
        'status': 'success',
        'data': serializer.data
    })

# API：逾期書籍
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_overdue_books(request):
    records = BorrowRecord.objects.filter(
        user=request.user,
        is_returned=False
    )
    overdue = [r for r in records if r.is_overdue]
    serializer = BorrowRecordSerializer(overdue, many=True)
    return Response({
        'status': 'success',
        'count': len(overdue),
        'data': serializer.data
    })

# 全域變數，只建立一次
_vectorstore = None
_embeddings = None

def get_vectorstore():
    global _vectorstore, _embeddings
    
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )
    
    # 每次重新取得書籍資料（確保資料是最新的）
    documents = get_library_documents()
    text_splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    split_docs = text_splitter.split_documents(documents)
    _vectorstore = FAISS.from_documents(split_docs, _embeddings)
    
    return _vectorstore

# 首頁 → 書籍目錄
def index(request):
    books = Book.objects.all()
    return render(request, 'index.html', {'books': books})

# 借書
@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    # 檢查用戶目前借閱數量
    current_borrow_count = BorrowRecord.objects.filter(
        user=request.user,
        is_returned=False
    ).count()
    
    # 超過5本就不能借
    if current_borrow_count >= 5:
        messages.error(request, '您已達到最大借閱數量（5本），請先還書再借！')
        return redirect('index')
    
    if book.available > 0:
        BorrowRecord.objects.create(user=request.user, book=book)
        book.available -= 1
        book.save()
        messages.success(request, f'成功借閱《{book.title}》（目前借閱：{current_borrow_count + 1}/5本）')
    else:
        messages.error(request, '此書目前無庫存')
    
    return redirect('index')

# 還書
@login_required
def return_book(request, record_id):
    record = get_object_or_404(BorrowRecord, id=record_id, user=request.user)
    record.is_returned = True
    record.return_date = timezone.now()
    record.save()
    record.book.available += 1
    record.book.save()
    messages.success(request, f'成功歸還《{record.book.title}》')
    return redirect('my_books')

# 我的借閱記錄
@login_required
def my_books(request):
    records = BorrowRecord.objects.filter(
        user=request.user,
        is_returned=False
    )
    return render(request, 'my_books.html', {'records': records})

# 登入
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, '帳號或密碼錯誤')
    return render(request, 'login.html')

# 登出
def logout_view(request):
    logout(request)
    return redirect('login')

from django.contrib.auth.models import User

# 註冊
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        
        # 確認兩次密碼相同
        if password != password2:
            messages.error(request, '兩次密碼不一致')
            return render(request, 'register.html')
        
        # 確認帳號沒有重複
        if User.objects.filter(username=username).exists():
            messages.error(request, '此帳號已被使用')
            return render(request, 'register.html')
        
        # 建立新用戶
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        messages.success(request, f'註冊成功！歡迎 {username}')
        return redirect('index')
    
    return render(request, 'register.html')


def get_library_documents():
    """從資料庫取得圖書館資料，轉換成文件格式"""
    documents = []

    # 取得所有書籍資料
    books = Book.objects.all()
    for book in books:
        content = f'''
        書名：{book.title}
        作者：{book.author}
        ISBN：{book.isbn}
        總數量：{book.quantity}
        目前可借數量：{book.available}
        狀態：{"可借閱" if book.available > 0 else "已借完"}
        '''
        documents.append(Document(page_content=content))

    # 加入圖書館規則
    rules = '''
    圖書館借閱規則：
    1. 每位用戶每次最多借5本書
    2. 借閱期限為14天
    3. 逾期每天每本罰款5元
    4. 圖書館開放時間：週一到週六 9:00-21:00，週日休館
    5. 還書方式：登入後到「我的借閱」頁面點選還書
    6. 如需續借請在到期前3天辦理
    '''
    documents.append(Document(page_content=rules))

    return documents

def get_rag_response(user_message):
    try:
        # 使用快取的向量庫
        vectorstore = get_vectorstore()

        # 搜尋相關資料
        relevant_docs = vectorstore.similarity_search(user_message, k=3)
        context = '\n'.join([doc.page_content for doc in relevant_docs])

        prompt = f'''你是圖書館客服助理，請根據以下圖書館資料回答用戶問題。
        
【圖書館資料】
{context}

【用戶問題】
{user_message}

請用台灣繁體中文回答，回答要簡潔清楚。
如果資料中沒有相關資訊，請說明無法找到相關資料。'''

        response = ollama.chat(
            model='llama3.2',
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        return response['message']['content']

    except Exception as e:
        return f'系統錯誤：{str(e)}'
# 聊天機器人
def chatbot_view(request):
    response_text = ''
    user_message = ''

    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        response_text = get_rag_response(user_message)

    return render(request, 'chatbot.html', {
        'response': response_text,
        'user_message': user_message
    })