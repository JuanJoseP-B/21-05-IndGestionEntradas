from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Event, Location

def billboard_view(request):
    """
    Cartelera pública de eventos con filtros dinámicos.
    """
    events = Event.objects.filter(status='PUBLICADO').select_related('location')
    
    # Filtro por búsqueda de texto
    q = request.GET.get('q')
    if q:
        events = events.filter(title__icontains=q) | events.filter(description__icontains=q)
        
    # Filtro por ciudad
    city = request.GET.get('city')
    if city:
        events = events.filter(location__city__iexact=city)

    cities = Location.objects.values_list('city', flat=True).distinct()
    
    context = {
        'events': events,
        'cities': cities
    }
    return render(request, 'billboard.html', context)

@login_required
def dashboard_view(request):
    """
    Dashboard exclusivo para Organizadores y Administradores.
    """
    if request.user.role not in ['ORGANIZADOR', 'ADMINISTRADOR']:
        messages.error(request, "Acceso restringido. Solo organizadores pueden acceder al panel.")
        return redirect('billboard')

    # Filtrar eventos que pertenezcan al organizador
    my_events = Event.objects.filter(organizer=request.user).select_related('location')
    
    # Calcular métricas básicas
    events_count = my_events.count()
    tickets_sold = sum(event.tickets.count() for event in my_events)
    # Suma total de los precios pagados en las entradas vendidas
    revenue = sum(
        event.tickets.filter(status='ACTIVA').aggregate(total=Sum('price'))['total'] or 0
        for event in my_events
    )
    
    locations = Location.objects.all()
    
    context = {
        'events': my_events,
        'events_count': events_count,
        'tickets_sold': tickets_sold,
        'revenue': float(revenue),
        'locations': locations
    }
    return render(request, 'dashboard.html', context)

@login_required
def create_event_view(request):
    if request.method == 'POST':
        if request.user.role not in ['ORGANIZADOR', 'ADMINISTRADOR']:
            messages.error(request, "Operación no autorizada.")
            return redirect('billboard')
            
        title = request.POST.get('title')
        description = request.POST.get('description')
        date = request.POST.get('date')
        time = request.POST.get('time')
        location_id = request.POST.get('location')
        status = request.POST.get('status', 'BORRADOR')

        location = get_object_or_404(Location, id=location_id)
        
        # Validar disponibilidad de recinto: evitar colisión en misma fecha, hora y ubicación
        # (Para simplicidad, validamos que no exista un evento publicado a la misma fecha y hora en el mismo lugar)
        if Event.objects.filter(location=location, date=date, time=time, status='PUBLICADO').exists():
            messages.error(request, f"Conflicto de reserva: Ya existe un evento programado en el recinto '{location.name}' en la fecha y hora seleccionada.")
            return redirect('dashboard')

        try:
            Event.objects.create(
                title=title,
                description=description,
                date=date,
                time=time,
                location=location,
                status=status,
                organizer=request.user
            )
            messages.success(request, f"¡El evento '{title}' ha sido registrado exitosamente!")
        except Exception as e:
            messages.error(request, f"Error al registrar evento: {str(e)}")
            
    return redirect('dashboard')

@login_required
def create_location_view(request):
    if request.method == 'POST':
        if request.user.role not in ['ORGANIZADOR', 'ADMINISTRADOR']:
            messages.error(request, "Operación no autorizada.")
            return redirect('billboard')
            
        name = request.POST.get('name')
        capacity = request.POST.get('capacity')
        address = request.POST.get('address')
        city = request.POST.get('city')

        try:
            Location.objects.create(
                name=name,
                capacity=capacity,
                address=address,
                city=city
            )
            messages.success(request, f"El recinto '{name}' ha sido registrado en {city}.")
        except Exception as e:
            messages.error(request, f"Error al registrar ubicación: {str(e)}")
            
    return redirect('dashboard')
