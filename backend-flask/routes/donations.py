"""
Rutas para el módulo de donativos.
Maneja donaciones vía PayPal y criptomonedas.
"""
from flask import Blueprint, request, jsonify, current_app
from extensions import db, limiter
from models import Donation, Usuario
from services.paypal_service import PayPalService
from services.crypto_service import CryptoService
from security import sanitizar_input, validar_email, registrar_log
from datetime import datetime, timedelta
import hashlib
import hmac

donations_bp = Blueprint('donations', __name__)

# Inicializar servicios
paypal_service = None
crypto_service = CryptoService()

def get_paypal_service():
    """Obtiene o crea el servicio de PayPal."""
    global paypal_service
    if paypal_service is None:
        config = current_app.config
        paypal_service = PayPalService(
            client_id=config.get('PAYPAL_CLIENT_ID'),
            client_secret=config.get('PAYPAL_CLIENT_SECRET'),
            mode=config.get('PAYPAL_MODE', 'sandbox')
        )
    return paypal_service

# ============================================================
# RUTAS PÚBLICAS - DONATIVOS
# ============================================================

@donations_bp.route('/api/donations/monthly-stats', methods=['GET'])
def get_monthly_stats():
    """
    Obtiene estadísticas mensuales de donativos.
    Retorna datos para gráfica de donaciones por mes.
    """
    try:
        # Obtener últimos 12 meses
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        
        # Consultar donativos completados
        donations = Donation.query.filter(
            Donation.payment_status == 'completed',
            Donation.created_at >= start_date
        ).all()
        
        # Agrupar por mes
        monthly_data = {}
        for d in donations:
            month_key = d.created_at.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'month': month_key,
                    'total_usd': 0,
                    'count': 0,
                    'donors': set()
                }
            monthly_data[month_key]['total_usd'] += d.amount_usd
            monthly_data[month_key]['count'] += 1
            if not d.is_anonymous and d.username:
                monthly_data[month_key]['donors'].add(d.username)
        
        # Convertir a lista y ordenar
        result = []
        for month_key in sorted(monthly_data.keys()):
            data = monthly_data[month_key]
            result.append({
                'month': month_key,
                'total_usd': round(data['total_usd'], 2),
                'count': data['count'],
                'unique_donors': len(data['donors'])
            })
        
        # Meta actual
        goal = current_app.config.get('DONATION_GOAL', 10000)
        total_raised = sum(r['total_usd'] for r in result)
        
        return jsonify({
            'success': True,
            'data': result,
            'goal': goal,
            'total_raised': round(total_raised, 2),
            'progress': round((total_raised / goal) * 100, 2) if goal > 0 else 0
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@donations_bp.route('/api/donations/recent', methods=['GET'])
def get_recent_donations():
    """Obtiene los donativos recientes (públicos)."""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        donations = Donation.query.filter(
            Donation.payment_status == 'completed'
        ).order_by(Donation.created_at.desc()).limit(limit).all()
        
        result = [d.to_dict() for d in donations]
        
        return jsonify({
            'success': True,
            'donations': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@donations_bp.route('/api/donations/create-paypal', methods=['POST'])
@limiter.limit("10 per hour")
def create_paypal_donation():
    """Crea un donativo vía PayPal."""
    try:
        data = request.get_json()
        
        amount = float(data.get('amount', 0))
        currency = sanitizar_input(data.get('currency', 'USD'), 10)
        donor_name = sanitizar_input(data.get('name', ''), 100)
        donor_email = sanitizar_input(data.get('email', ''), 120)
        is_anonymous = data.get('anonymous', False)
        message = sanitizar_input(data.get('message', ''), 500)
        
        # Validaciones
        if amount <= 0:
            return jsonify({'error': 'El monto debe ser mayor a 0'}), 400
        
        if not validar_email(donor_email) and not is_anonymous:
            return jsonify({'error': 'Email inválido'}), 400
        
        # Crear registro en base de datos
        donation = Donation(
            username=donor_name if not is_anonymous else None,
            email=donor_email if not is_anonymous else None,
            amount=amount,
            currency=currency,
            amount_usd=amount,  # Asumiendo USD, convertir si es necesario
            payment_method='paypal',
            payment_status='pending',
            is_anonymous=is_anonymous,
            message=message if not is_anonymous else None
        )
        
        db.session.add(donation)
        db.session.commit()
        
        # Crear pago en PayPal
        paypal = get_paypal_service()
        description = f"Donativo - {donor_name}" if not is_anonymous else "Donativo anónimo"
        
        result = paypal.create_donation_payment(
            amount=amount,
            currency=currency,
            donor_email=donor_email,
            donor_name=donor_name,
            description=description
        )
        
        if result['success']:
            # Actualizar donation con payment_id
            donation.transaction_id = result['payment_id']
            db.session.commit()
            
            registrar_log('donation_paypal_created', donor_name, {
                'amount': amount,
                'currency': currency,
                'payment_id': result['payment_id']
            })
            
            return jsonify({
                'success': True,
                'payment_id': result['payment_id'],
                'approval_url': result['approval_url'],
                'donation_id': donation.id
            })
        else:
            db.session.delete(donation)
            db.session.commit()
            
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error al crear pago')
            }), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@donations_bp.route('/api/donations/execute-paypal', methods=['POST'])
def execute_paypal_donation():
    """Ejecuta un pago de PayPal después de la aprobación."""
    try:
        data = request.get_json()
        payment_id = data.get('payment_id')
        payer_id = data.get('payer_id')
        
        if not payment_id or not payer_id:
            return jsonify({'error': 'Faltan parámetros'}), 400
        
        # Ejecutar pago
        paypal = get_paypal_service()
        result = paypal.execute_payment(payment_id, payer_id)
        
        if result['success']:
            # Actualizar donation
            donation = Donation.query.filter_by(transaction_id=payment_id).first()
            
            if donation:
                donation.payment_status = 'completed'
                donation.confirmed_at = datetime.utcnow()
                donation.transaction_id = result['transaction_id']
                db.session.commit()
                
                registrar_log('donation_paypal_completed', donation.username, {
                    'amount': donation.amount,
                    'transaction_id': result['transaction_id']
                })
                
                return jsonify({
                    'success': True,
                    'message': 'Donativo completado exitosamente',
                    'donation_id': donation.id
                })
            else:
                return jsonify({'error': 'Donativo no encontrado'}), 404
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Error al ejecutar pago')
            }), 500
            
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@donations_bp.route('/api/donations/create-crypto', methods=['POST'])
@limiter.limit("5 per hour")
def create_crypto_donation():
    """Crea un donativo vía criptomonedas."""
    try:
        data = request.get_json()
        
        amount = float(data.get('amount', 0))
        fiat_currency = sanitizar_input(data.get('fiat_currency', 'USD'), 10)
        crypto = sanitizar_input(data.get('crypto', 'BTC'), 10).upper()
        donor_name = sanitizar_input(data.get('name', ''), 100)
        donor_email = sanitizar_input(data.get('email', ''), 120)
        is_anonymous = data.get('anonymous', False)
        message = sanitizar_input(data.get('message', ''), 500)
        
        # Validaciones
        if amount <= 0:
            return jsonify({'error': 'El monto debe ser mayor a 0'}), 400
        
        if crypto not in ['BTC', 'ETH', 'USDT']:
            return jsonify({'error': 'Criptomoneda no soportada'}), 400
        
        # Calcular monto en cripto
        crypto_service = CryptoService()
        calc_result = crypto_service.calculate_crypto_amount(amount, fiat_currency, crypto)
        
        if not calc_result.get('success'):
            return jsonify({
                'error': calc_result.get('error', 'Error al calcular monto')
            }), 500
        
        crypto_amount = calc_result['crypto_amount']
        exchange_rate = calc_result['rate']
        
        # Obtener wallet address
        wallet_info = crypto_service.get_wallet_address(crypto)
        
        # Crear registro en base de datos
        donation = Donation(
            username=donor_name if not is_anonymous else None,
            email=donor_email if not is_anonymous else None,
            amount=crypto_amount,
            currency=crypto,
            amount_usd=amount,  # Valor en USD
            payment_method=crypto.lower(),
            payment_status='pending',
            is_anonymous=is_anonymous,
            message=message if not is_anonymous else None
        )
        
        db.session.add(donation)
        db.session.commit()
        
        # Generar QR
        qr_data = crypto_service.generate_payment_qr(
            crypto, crypto_amount, wallet_info['address']
        )
        
        registrar_log('donation_crypto_created', donor_name, {
            'crypto': crypto,
            'amount': crypto_amount,
            'fiat': amount,
            'fiat_currency': fiat_currency
        })
        
        return jsonify({
            'success': True,
            'donation_id': donation.id,
            'crypto': crypto,
            'crypto_amount': crypto_amount,
            'fiat_amount': amount,
            'fiat_currency': fiat_currency,
            'exchange_rate': exchange_rate,
            'wallet_address': wallet_info['address'],
            'network': wallet_info['network'],
            'qr_code': qr_data,
            'instructions': f"Envía exactamente {crypto_amount} {crypto} a la dirección mostrada"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@donations_bp.route('/api/donations/verify-crypto/<int:donation_id>', methods=['POST'])
def verify_crypto_donation(donation_id):
    """Verifica una transacción de criptomoneda."""
    try:
        data = request.get_json()
        tx_hash = data.get('tx_hash')
        
        if not tx_hash:
            return jsonify({'error': 'Hash de transacción requerido'}), 400
        
        donation = Donation.query.get_or_404(donation_id)
        
        if donation.payment_method not in ['btc', 'eth', 'usdt']:
            return jsonify({'error': 'No es un donativo de criptomoneda'}), 400
        
        # Verificar transacción
        crypto_service = CryptoService()
        verification = crypto_service.verify_transaction(
            tx_hash,
            donation.currency.upper(),
            donation.amount
        )
        
        if verification.get('verified'):
            donation.payment_status = 'completed'
            donation.confirmed_at = datetime.utcnow()
            donation.transaction_id = tx_hash
            db.session.commit()
            
            registrar_log('donation_crypto_verified', donation.username, {
                'tx_hash': tx_hash,
                'confirmations': verification.get('confirmations', 0)
            })
            
            return jsonify({
                'success': True,
                'message': 'Donativo verificado exitosamente',
                'confirmations': verification.get('confirmations', 0)
            })
        else:
            return jsonify({
                'success': False,
                'error': verification.get('error', 'Transacción no verificada'),
                'confirmations': verification.get('confirmations', 0)
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500