
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User , auth
from django.contrib import messages
from django.core.mail import EmailMessage
from django.views import View
from django.utils.encoding import force_bytes, DjangoUnicodeDecodeError, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import account_activation_token
from .models import Profile,Post
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import  login_required
from django.views.generic import TemplateView
# Create your views here.


# tạo lệnh đăng nhặp khi chưa đăng nhập
class Profiletemplateview(TemplateView):
    template_name = 'registration/signin.html'

# đăng ký tài khoản
class signupclass(View):
    def get(self, request):
        return render(request, 'registration/signup.html')
    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password= request.POST['password']
        con_password = request.POST['con_password']
        if not User.objects.filter(username=username).exists() and len(username) > 0:
            if not User.objects.filter(email=email).exists():
                if password == con_password: 
                    if len(password) < 6:
                        messages.warning(request, 'mật khẩu qua ngắn')
                        return redirect("web:signup")
                    else:
                        
                        
                        user = User.objects.create_user(username=username,email=email,password=password)
                        user.is_active =False
                        user.save()
                        current_site = get_current_site(request)
                        email_body = {
                            'user': user,
                            'domain': current_site.domain,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                            'token': account_activation_token.make_token(user),
                        }

                        link = reverse('web:activate', kwargs={'uidb64': email_body['uid'], 'token': email_body['token']})

                        email_subject = 'activate your account'

                        activate_url = 'http://'+current_site.domain+link

                        email = EmailMessage(
                            email_subject,
                            'hello '+user.username + ', Please the link below to activate your account \n'+activate_url,
                            'noreply@semycolon.com',
                            [email],
                        )
                        email.send(fail_silently=False)
                        user_modal = User.objects.get(username=username)
                        new_profile = Profile.objects.create(user=user_modal,id_user=user_modal.id)
                        new_profile.save()
                        messages.success(request,"Kiểm Tra Gmail của bạn để xác Minh")
                        return redirect("web:signup")


                messages.error(request,"Mật Khẩu không Trùng Nhau")
                return redirect("web:signup")
            messages.error(request, "Vui lòng thêm Email")   
            return redirect("web:signup")
        if len(username) ==  0:
            messages.error(request, "Vui Lòng Nhập Tên Tài Khoản")  
            return redirect("web:signup")
        messages.error(request, "Tài Khoản Đã Tồn Tại")   
        return redirect("web:signup")

# đăng nhặp  
class Loginclass(View):
    def get(self,request):
        return render(request, 'registration/login.html')
    def post(self,request):
        username = request.POST['username']
        password = request.POST['password']
        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth.login(request,user)
                    user_login = auth.authenticate(username=username, password=password)
                    auth.login(request,user_login)
                    return redirect("web:home")

                messages.error(request,"Vui lòng kiểm tra Email để Kích Hoạt Tài Khoản")
                return redirect("web:signin")
            messages.error(request,"Vui lòng kiểm tra Email để Kích Hoạt Tài Khoản")
            return redirect("web:signin")
        messages.error(request,"Taì Khoản Hoặc Mật Khẩu Không Chính xác")
        return render(request, 'registration/login.html')

            
# Gửi email xác định tài khoản
class VericationView(View):
    def get(self, request,token, uidb64):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
            if not account_activation_token.check_token(user,token):
                return redirect('login'+"?messages="+"user already activated")
            if user.is_active:
                
                return redirect('web:signin')
            user.is_active = True
            user.save()
            messages.success(request, "Tài Khoản Đã Được Kích Hoạt")
            return redirect('web:signin')
        except Exception as ex:
            pass
        return redirect('web:signin')

# thay đổi profile img/bio,..
class Settingclass(View):
    def get(self,request):
        user_profile = Profile.objects.get(user=request.user)
        content = {'user_profile': user_profile}
        return render(request, 'authecation/settings.html',content)
    def post(self,request):
        user_profile = Profile.objects.get(user=request.user)
        content = {'user_profile': user_profile}
        if request.FILES.get('image') == None:
                image = user_profile.profileimg
                bio = request.POST['bio']
                location = request.POST['location']
                user_profile.profileimg = image
                user_profile.bio = bio  
                user_profile.location = location
                user_profile.save()

        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio  
            user_profile.location = location
            user_profile.save()
        return render(request, 'authecation/settings.html', content)

# trang chính      
class homeclass(View):
    def get(sefl,request):
        user_object = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_object)
        posts = Post.objects.all()
        
        
        content =  {'user_profile':user_profile, 'posts': posts}

        return render(request, 'authecation/home.html',   content)

# tạo post
class uppostclass(View):
    def get(self,request):
        return render(request, 'authecation/home.html')
    def post(self,request):
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        new_post = Post.objects.create(user=user,images=image,caption=caption)
        new_post.save()
        return redirect('web:home')

#đăng xuất
def logout(request):
    auth.logout(request)
    return redirect('/accounts/signin')

class followerclass(View):
    def post(self,request):
        pass

#trang profile
class profileclass(View):
    def get(self,request,pk):
        user_object = User.objects.get(username=pk)
        user_profile = Profile.objects.get(user=user_object)
        user_posts = Post.objects.filter(user=pk)
        user_post_len = len(user_posts)
        context = {
            "user_object" : user_object,
            "user_profile" : user_profile,
            "user_posts": user_posts,
            "user_post_len": user_post_len
        }
        return render(request, 'authecation/profile.html', context)