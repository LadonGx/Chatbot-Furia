# alerts.py
from datetime import datetime
import threading
import time
from firestore_db import db
from flask import current_app

class FanAlertSystem:
    def __init__(self, flask_app):
        self.app = flask_app
        self.running = False
        self.alert_thread = None

    def start(self):
        """Inicia o monitoramento em background"""
        if not self.running:
            self.running = True
            self.alert_thread = threading.Thread(target=self._monitor_fans)
            self.alert_thread.daemon = True
            self.alert_thread.start()

    def stop(self):
        """Para o monitoramento"""
        self.running = False
        if self.alert_thread:
            self.alert_thread.join()

    def _monitor_fans(self):
        """Verifica periodicamente por menções relevantes"""
        with self.app.app_context():
            while self.running:
                try:
                    fans_ref = db.collection('usuarios')
                    fans = fans_ref.stream()
                    
                    for fan in fans:
                        fan_data = fan.to_dict()
                        alerts = self._check_for_alerts(fan_data)
                        
                        if alerts:
                            self._store_alerts(fan.id, alerts)
                
                except Exception as e:
                    current_app.logger.error(f"Erro no monitoramento: {str(e)}")
                
                time.sleep(3600)  # Verifica a cada hora

    def _check_for_alerts(self, fan_data):
        """Verifica condições para alertas"""
        alerts = []
        
        # Alerta 1: Menção à FURIA
        furia_mentions = 0
        for platform in ['twitter', 'instagram', 'twitch']:
            platform_data = fan_data.get(f"{platform}_data", {})
            furia_mentions += platform_data.get('esports_engagement', {}).get('furia_mentions', 0)
        
        if furia_mentions > 0:
            alerts.append({
                'type': 'furia_mention',
                'message': f'{furia_mentions} menções à FURIA encontradas',
                'priority': 'medium',
                'timestamp': datetime.now().isoformat()  # Corrigido aqui
            })
        
        # Alerta 2: Alto engajamento com e-sports
        total_mentions = sum(
            fan_data.get(f"{platform}_data", {}).get('esports_engagement', {}).get('esports_mentions', 0)
            for platform in ['twitter', 'instagram', 'twitch']
        )
        
        if total_mentions > 10:
            alerts.append({
                'type': 'high_engagement',
                'message': 'Alto engajamento com e-sports detectado',
                'priority': 'high',
                'timestamp': datetime.now().isoformat()  # Corrigido aqui
            })
        
        return alerts

    def _store_alerts(self, user_id, alerts):
        """Armazena alertas no Firestore"""
        try:
            doc_ref = db.collection('user_alerts').document(user_id)
            doc_ref.set({
                'alerts': alerts,
                'last_updated': datetime.now().isoformat(),
                'read': False
            }, merge=True)
        except Exception as e:
            current_app.logger.error(f"Erro ao salvar alertas: {str(e)}")