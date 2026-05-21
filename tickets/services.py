import qrcode
from io import BytesIO
from django.core.files import File
from .models import Ticket

def generate_qr_code(ticket):
    """
    Genera una imagen de código QR con el UUID único de la entrada
    y la guarda en el campo qr_code de la entrada.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        # El QR contiene la información del identificador de la entrada
        qr.add_data(str(ticket.uuid_code))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        blob = BytesIO()
        img.save(blob, 'PNG')
        
        filename = f"qr_{ticket.uuid_code}.png"
        ticket.qr_code.save(filename, File(blob), save=False)
        ticket.save()
        return True
    except Exception as e:
        print(f"Error al generar código QR: {e}")
        return False

def validate_ticket(uuid_code):
    """
    Valida un código de entrada y cambia su estado a UTILIZADA si está ACTIVA.
    Retorna un booleano indicando el éxito de la operación y un mensaje descriptivo.
    """
    try:
        ticket = Ticket.objects.get(uuid_code=uuid_code)
        if ticket.status == 'ACTIVA':
            ticket.status = 'UTILIZADA'
            ticket.save()
            return True, "Entrada validada correctamente. Acceso concedido."
        elif ticket.status == 'UTILIZADA':
            return False, "Alerta: Esta entrada ya ha sido utilizada anteriormente."
        else:
            return False, "Error: Esta entrada se encuentra cancelada."
    except Ticket.DoesNotExist:
        return False, "Error: La entrada escaneada no existe en el sistema."
    except Exception as e:
        return False, f"Error inesperado al validar la entrada: {str(e)}"
