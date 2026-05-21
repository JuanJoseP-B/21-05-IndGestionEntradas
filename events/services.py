import csv
from io import BytesIO
from openpyxl import Workbook
from django.utils.timezone import localtime

def generate_event_sales_excel(event):
    """
    Genera un archivo Excel (.xlsx) en memoria conteniendo el listado
    de entradas vendidas para un evento específico.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "Ventas de Entradas"

    # Estructura del reporte
    ws.append([f"Reporte de Ventas: {event.title}"])
    ws.append([f"Fecha del Evento: {event.date} - {event.time}"])
    ws.append([f"Recinto: {event.location.name} ({event.location.city})"])
    ws.append([]) # Fila vacía para espaciado

    # Encabezados
    headers = ["Código de Entrada", "Comprador (Username)", "Nombre Completo", "Email", "Precio", "Estado", "Fecha de Compra"]
    ws.append(headers)

    # Datos de las entradas
    tickets = event.tickets.all().select_related('buyer')
    for ticket in tickets:
        full_name = f"{ticket.buyer.first_name} {ticket.buyer.last_name}".strip() or "N/A"
        ws.append([
            str(ticket.uuid_code),
            ticket.buyer.username,
            full_name,
            ticket.buyer.email or "N/A",
            float(ticket.price),
            ticket.get_status_display(),
            localtime(ticket.purchased_at).strftime("%d/%m/%Y %H:%M:%S")
        ])

    # Guardar en memoria
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def generate_event_sales_csv(event):
    """
    Genera un archivo CSV en memoria conteniendo el listado de entradas
    vendidas para un evento específico. Método alternativo de alta velocidad.
    """
    import io
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([f"Reporte de Ventas: {event.title}"])
    writer.writerow([f"Fecha del Evento: {event.date} - {event.time}"])
    writer.writerow([])
    
    writer.writerow(["Codigo de Entrada", "Comprador", "Nombre Completo", "Email", "Precio", "Estado", "Fecha de Compra"])
    
    tickets = event.tickets.all().select_related('buyer')
    for ticket in tickets:
        full_name = f"{ticket.buyer.first_name} {ticket.buyer.last_name}".strip() or "N/A"
        writer.writerow([
            str(ticket.uuid_code),
            ticket.buyer.username,
            full_name,
            ticket.buyer.email or "N/A",
            float(ticket.price),
            ticket.get_status_display(),
            localtime(ticket.purchased_at).strftime("%d/%m/%Y %H:%M:%S")
        ])
        
    bytes_data = b'\xef\xbb\xbf' + output.getvalue().encode('utf-8')
    return BytesIO(bytes_data)
