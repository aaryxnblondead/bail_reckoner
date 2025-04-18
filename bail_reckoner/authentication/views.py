from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .forms import UserRegistrationForm, UserLoginForm, AadhaarVerificationForm
from .models import User
from .services import AadhaarVerificationService

def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'Registration successful. Please verify your Aadhaar to continue.')
            return redirect('verify_aadhaar')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'authentication/register.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})

def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

@login_required
def verify_aadhaar_view(request):
    """Aadhaar verification view"""
    if request.method == 'POST':
        form = AadhaarVerificationForm(request.POST)
        if form.is_valid():
            aadhaar_number = form.cleaned_data['aadhaar_number']
            otp = form.cleaned_data['otp']
            
            # Verify Aadhaar using the service
            verification_service = AadhaarVerificationService()
            result = verification_service.verify_aadhaar(aadhaar_number, otp)
            
            if result['success']:
                # Update user's Aadhaar ID
                user = request.user
                user.aadhaar_id = aadhaar_number
                user.save()
                
                messages.success(request, 'Aadhaar verification successful.')
                return redirect('dashboard')
            else:
                messages.error(request, f'Aadhaar verification failed: {result["message"]}')
    else:
        form = AadhaarVerificationForm()
    
    return render(request, 'authentication/verify_aadhaar.html', {'form': form})

# API Views
@api_view(['POST'])
@permission_classes([AllowAny])
def api_register(request):
    """API endpoint for user registration"""
    data = request.data
    
    # Check if username or email already exists
    if User.objects.filter(username=data.get('username')).exists():
        return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=data.get('email')).exists():
        return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Create user
    user = User.objects.create_user(
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password'),
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        user_type=data.get('user_type', 'prisoner')
    )
    
    return Response({
        'message': 'User registered successfully',
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'user_type': user.user_type
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """API endpoint for user login"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # Generate token for the user
        from rest_framework.authtoken.models import Token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'user_type': user.user_type,
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
@api_view(['POST'])
@login_required
def api_verify_aadhaar(request):
        """API endpoint for Aadhaar verification"""
        aadhaar_number = request.data.get('aadhaar_number')
        otp = request.data.get('otp')
    
        if not aadhaar_number or not otp:
            return Response({'error': 'Aadhaar number and OTP are required'}, status=status.HTTP_400_BAD_REQUEST)
    
        # Verify Aadhaar using the service
        verification_service = AadhaarVerificationService()
        result = verification_service.verify_aadhaar(aadhaar_number, otp)
    
        if result['success']:
            # Update user's Aadhaar ID
            user = request.user
            user.aadhaar_id = aadhaar_number
            user.save()
        
            return Response({'message': 'Aadhaar verification successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': result['message']}, status=status.HTTP_400_BAD_REQUEST)            
            