"""
Servicio de PayPal para procesamiento seguro de donativos.
Implementa las mejores prácticas de seguridad.
"""
import paypalrestsdk
from flask import current_app
import hashlib
import hmac
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class PayPalService:
    """Servicio seguro para PayPal."""
    
    def __init__(self, client_id, client_secret, mode='sandbox'):
        """Inicializa PayPal SDK."""
        paypalrestsdk.configure({
            "mode": mode,
            "client_id": client_id,
            "client_secret": client_secret
        })
        self.mode = mode
    
    def create_donation_payment(self, amount, currency, donor_email, donor_name, description="Donativo"):
        """
        Crea un pago de donativo en PayPal.
        
        Args:
            amount: Monto a donar
            currency: Moneda (USD, EUR, MXN)
            donor_email: Email del donante
            donor_name: Nombre del donante
            description: Descripción del donativo
            
        Returns:
            dict: {'success': bool, 'payment_id': str, 'approval_url': str, 'error': str}
        """
        try:
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": f"{current_app.config['FRONTEND_URL']}/donativos/success",
                    "cancel_url": f"{current_app.config['FRONTEND_URL']}/donativos/cancel"
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": description,
                            "sku": "DONATION",
                            "price": str(round(amount, 2)),
                            "currency": currency,
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(round(amount, 2)),
                        "currency": currency
                    },
                    "description": description,
                    "custom": f"{donor_email}|{donor_name}|{datetime.utcnow().isoformat()}"
                }]
            })
            
            if payment.create():
                # Obtener URL de aprobación
                approval_url = None
                for link in payment.links:
                    if link.rel == "approval_url":
                        approval_url = link.href
                        break
                
                return {
                    'success': True,
                    'payment_id': payment.id,
                    'approval_url': approval_url
                }
            else:
                logger.error(f"Error creando pago PayPal: {payment.error}")
                return {
                    'success': False,
                    'error': 'Error al crear el pago'
                }
                
        except Exception as e:
            logger.error(f"Excepción en PayPal: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def execute_payment(self, payment_id, payer_id):
        """
        Ejecuta un pago después de la aprobación del usuario.
        
        Args:
            payment_id: ID del pago de PayPal
            payer_id: ID del pagador
            
        Returns:
            dict: {'success': bool, 'transaction_id': str, 'error': str}
        """
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                # Extraer información de la transacción
                transaction = payment.transactions[0]
                transaction_id = transaction.related_resources[0].sale.id
                
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'amount': transaction.amount.total,
                    'currency': transaction.amount.currency
                }
            else:
                logger.error(f"Error ejecutando pago: {payment.error}")
                return {
                    'success': False,
                    'error': payment.error
                }
                
        except Exception as e:
            logger.error(f"Excepción ejecutando pago: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_payment(self, payment_id):
        """Verifica el estado de un pago."""
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            return {
                'success': True,
                'state': payment.state,
                'transactions': payment.transactions
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }