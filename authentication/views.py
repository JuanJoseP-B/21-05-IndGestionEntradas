from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import CustomUser

def register_view(request):
    if request.user.is_authenticated:
        return redirect('billboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        role = request.POST.get('role', 'ASISTENTE')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'register.html')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya está registrado.")
            return render(request, 'register.html')

        try:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role,
                password=password
            )
            # Log the user in immediately
            login(request, user)
            messages.success(request, f"¡Bienvenido, {username}! Tu cuenta ha sido creada exitosamente.")
            if role == 'ORGANIZADOR':
                return redirect('dashboard')
            return redirect('billboard')
        except Exception as e:
            messages.error(request, f"Error al registrar el usuario: {str(e)}")
            return render(request, 'register.html')
            
    return render(request, 'register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('billboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next', 'billboard')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"¡Hola de nuevo, {user.username}!")
            if user.role == 'ORGANIZADOR' and next_url == 'billboard':
                return redirect('dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Credenciales incorrectas. Inténtalo de nuevo.")
            
    return render(request, 'login.html')

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "Has cerrado sesión correctamente. ¡Esperamos verte pronto!")
    return redirect('billboard')
