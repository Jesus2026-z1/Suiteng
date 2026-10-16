"""
Servicio de criptomonedas para procesamiento seguro de donativos.
Soporta Bitcoin, Ethereum y USDT.
"""
import requests
from flask import current_app
import hashlib
import hmac
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CryptoService:
    """Servicio seguro para criptomonedas."""
    
    def __init__(self):
        """Inicializa el servicio."""
        # Direcciones de wallet (en producción, usar variables de entorno)
        self.wallets = {
            'BTC': current_app.config.get('BTC_WALLET_ADDRESS', ''),
            'ETH': current_app.config.get('ETH_WALLET_ADDRESS', ''),
            'USDT': current_app.config.get('USDT_WALLET_ADDRESS', '')
        }
        self.networks = {
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum (ERC-20)',
            'USDT': 'Tron (TRC-20)'
        }
    
    def get_exchange_rate(self, crypto, fiat='USD'):
        """
        Obtiene la tasa de cambio actual de criptomoneda a fiat.
        
        Args:
            crypto: Criptomoneda (BTC, ETH, USDT)
            fiat: Moneda fiat (USD, EUR, MXN)
            
        Returns:
            float: Tasa de cambio
        """
        try:
            # Usar CoinGecko API (gratuita)
            crypto_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'USDT': 'tether'
            }
            
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': crypto_map.get(crypto, 'bitcoin'),
                'vs_currencies': fiat.lower(),
                'include_last_updated_at': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            crypto_id = crypto_map.get(crypto, 'bitcoin')
            rate = data[crypto_id][fiat.lower()]
            
            return rate
            
        except Exception as e:
            logger.error(f"Error obteniendo tasa de cambio: {str(e)}")
            return None
    
    def calculate_crypto_amount(self, amount_fiat, fiat_currency, crypto):
        """
        Calcula la cantidad de criptomoneda equivalente.
        
        Args:
            amount_fiat: Monto en moneda fiat
            fiat_currency: Moneda fiat (USD, EUR, MXN)
            crypto: Criptomoneda (BTC, ETH, USDT)
            
        Returns:
            dict: {'crypto_amount': float, 'rate': float, 'error': str}
        """
        try:
            # Obtener tasa de cambio
            rate = self.get_exchange_rate(crypto, fiat_currency)
            
            if rate is None:
                return {'error': 'No se pudo obtener la tasa de cambio'}
            
            crypto_amount = amount_fiat / rate
            
            return {
                'crypto_amount': round(crypto_amount, 8),
                'rate': rate,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error calculando monto: {str(e)}")
            return {'error': str(e)}
    
    def get_wallet_address(self, crypto):
        """
        Obtiene la dirección de wallet para una criptomoneda.
        
        Args:
            crypto: Criptomoneda (BTC, ETH, USDT)
            
        Returns:
            dict: {'address': str, 'network': str}
        """
        return {
            'address': self.wallets.get(crypto, ''),
            'network': self.networks.get(crypto, '')
        }
    
    def verify_transaction(self, tx_hash, crypto, expected_amount):
        """
        Verifica una transacción en la blockchain.
        
        Args:
            tx_hash: Hash de la transacción
            crypto: Criptomoneda
            expected_amount: Monto esperado
            
        Returns:
            dict: {'verified': bool, 'amount': float, 'confirmations': int}
        """
        try:
            # Implementar verificación según la criptomoneda
            # Esto es un ejemplo simplificado
            if crypto == 'BTC':
                return self._verify_btc_transaction(tx_hash, expected_amount)
            elif crypto == 'ETH':
                return self._verify_eth_transaction(tx_hash, expected_amount)
            elif crypto == 'USDT':
                return self._verify_usdt_transaction(tx_hash, expected_amount)
            
            return {'verified': False, 'error': 'Criptomoneda no soportada'}
            
        except Exception as e:
            logger.error(f"Error verificando transacción: {str(e)}")
            return {'verified': False, 'error': str(e)}
    
    def _verify_btc_transaction(self, tx_hash, expected_amount):
        """Verifica transacción Bitcoin."""
        try:
            url = f"https://blockchain.info/rawtx/{tx_hash}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                tx_data = response.json()
                
                # Verificar confirmaciones
                confirmations = tx_data.get('block_height', 0)
                
                # Verificar monto (simplificado)
                # En producción, verificar outputs y direcciones
                
                return {
                    'verified': confirmations >= 3,  # Mínimo 3 confirmaciones
                    'confirmations': confirmations,
                    'success': True
                }
            
            return {'verified': False, 'error': 'Transacción no encontrada'}
            
        except Exception as e:
            return {'verified': False, 'error': str(e)}
    
    def _verify_eth_transaction(self, tx_hash, expected_amount):
        """Verifica transacción Ethereum."""
        # Implementar similar a BTC usando Etherscan API
        pass
    
    def _verify_usdt_transaction(self, tx_hash, expected_amount):
        """Verifica transacción USDT."""
        # Implementar similar a BTC usando Tronscan API
        pass
    
    def generate_payment_qr(self, crypto, amount, address):
        """
        Genera un QR para facilitar el pago.
        
        Args:
            crypto: Criptomoneda
            amount: Monto
            address: Dirección de wallet
            
        Returns:
            str: URL del QR o data URI
        """
        import qrcode
        import base64
        from io import BytesIO
        
        # Crear URI de pago
        if crypto == 'BTC':
            uri = f"bitcoin:{address}?amount={amount}"
        elif crypto == 'ETH':
            uri = f"ethereum:{address}@1?value={int(amount * 10**18)}"
        elif crypto == 'USDT':
            uri = f"tron:{address}?amount={amount}"
        else:
            uri = address
        
        # Generar QR
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"