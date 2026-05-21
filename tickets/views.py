from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from events.models import Event
from .models import Ticket
from .services import generate_qr_code, validate_ticket
from events.services import generate_event_sales_excel, generate_event_sales_csv

@login_required
def purchase_ticket_view(request, event_id):
    """
    Simula la compra de una entrada para un evento y genera su QR.
    """
    event = get_object_or_404(Event, id=event_id, status='PUBLICADO')
    
    # Comprobar aforo disponible
    sold_count = Ticket.objects.filter(event=event, status='ACTIVA').count()
    if sold_count >= event.location.capacity:
        messages.error(request, f"¡Lo sentimos! Las entradas para el evento '{event.title}' se encuentran agotadas.")
        return redirect('billboard')

    try:
        # Registrar compra
        ticket = Ticket.objects.create(
            buyer=request.user,
            event=event,
            price=50000.00, # Precio simulado
            status='ACTIVA'
        )
        
        # Generar código QR de forma asíncrona/servicio
        generate_qr_code(ticket)
        
        messages.success(request, f"¡Entrada adquirida con éxito para '{event.title}'! Tu código QR se ha generado y enviado a tu correo.")
    except Exception as e:
        messages.error(request, f"Error al procesar la compra de la entrada: {str(e)}")
        
    return redirect('billboard')

@login_required
def validate_ticket_view(request):
    """
    Valida un ticket a través de su código UUID ingresado o escaneado.
    """
    if request.user.role not in ['ORGANIZADOR', 'ADMINISTRADOR']:
        messages.error(request, "Operación no autorizada.")
        return redirect('billboard')
        
    if request.method == 'POST':
        uuid_code = request.POST.get('uuid_code')
        if uuid_code:
            success, message = validate_ticket(uuid_code)
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
        else:
            messages.error(request, "Código UUID de entrada inválido.")
            
    return redirect('dashboard')

@login_required
def download_report_view(request, event_id, format_type):
    """
    Descarga el reporte de ventas en formato Excel o CSV.
    """
    if request.user.role not in ['ORGANIZADOR', 'ADMINISTRADOR']:
        messages.error(request, "Operación no autorizada.")
        return redirect('billboard')
        
    event = get_object_or_404(Event, id=event_id)
    
    # Verificar que el evento pertenezca al organizador (excepto si es Administrador)
    if event.organizer != request.user and request.user.role != 'ADMINISTRADOR':
        messages.error(request, "No tienes permisos para descargar los reportes de este evento.")
        return redirect('dashboard')
        
    if format_type == 'excel':
        output = generate_event_sales_excel(event)
        response = HttpResponse(
            output.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=Reporte_Ventas_{event.id}.xlsx'
        return response
    elif format_type == 'csv':
        output = generate_event_sales_csv(event)
        response = HttpResponse(
            output.read(),
            content_type='text/csv'
        )
        response['Content-Disposition'] = f'attachment; filename=Reporte_Ventas_{event.id}.csv'
        return response
        
    messages.error(request, "Formato de descarga no soportado.")
    return redirect('dashboard')
