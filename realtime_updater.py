#!/usr/bin/env python3
"""
Système de mise à jour en temps réel
Permet la mise à jour automatique des modèles basée sur les nouveaux retours utilisateurs
"""

import threading
import time
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from pathlib import Path
import sqlite3
import pickle
from queue import Queue
import logging

class RealTimeModelUpdater:
    """Système de mise à jour des modèles en temps réel"""
    
    def __init__(self, hybrid_system, rating_system, 
                 update_interval: int = 3600,  # 1 heure par défaut
                 min_updates_threshold: int = 10):
        self.hybrid_system = hybrid_system
        self.rating_system = rating_system
        self.update_interval = update_interval
        self.min_updates_threshold = min_updates_threshold
        
        # File d'attente pour les mises à jour
        self.update_queue = Queue()
        
        # État du système
        self.is_running = False
        self.last_update = datetime.now()
        self.update_count = 0
        
        # Thread de mise à jour
        self.update_thread = None
        
        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Callbacks pour les événements
        self.on_model_updated = None
        self.on_update_failed = None
        
    def start_real_time_updates(self):
        """Démarre le système de mise à jour en temps réel"""
        if self.is_running:
            self.logger.warning("Le système de mise à jour est déjà en cours")
            return
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        self.logger.info("🚀 Système de mise à jour en temps réel démarré")
        self.logger.info(f"⏰ Intervalle de mise à jour: {self.update_interval}s")
        self.logger.info(f"🎯 Seuil de mises à jour: {self.min_updates_threshold}")
    
    def stop_real_time_updates(self):
        """Arrête le système de mise à jour"""
        self.is_running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=5)
        self.logger.info("⏹️  Système de mise à jour arrêté")
    
    def queue_rating_update(self, user_id: str, movie_id: int, rating: float):
        """Ajoute une nouvelle note à la file de mise à jour"""
        update_data = {
            'type': 'rating',
            'user_id': user_id,
            'movie_id': movie_id,
            'rating': rating,
            'timestamp': datetime.now()
        }
        self.update_queue.put(update_data)
        self.update_count += 1
        
        self.logger.info(f"📝 Note ajoutée à la file: {user_id} -> {movie_id} ({rating}/10)")
        
        # Mise à jour immédiate si seuil atteint
        if self.update_count >= self.min_updates_threshold:
            self._trigger_immediate_update()
    
    def queue_feedback_update(self, user_id: str, movie_id: int, 
                            recommended_movie_id: int, feedback: str):
        """Ajoute un retour utilisateur à la file de mise à jour"""
        update_data = {
            'type': 'feedback',
            'user_id': user_id,
            'movie_id': movie_id,
            'recommended_movie_id': recommended_movie_id,
            'feedback': feedback,
            'timestamp': datetime.now()
        }
        self.update_queue.put(update_data)
        self.update_count += 1
        
        self.logger.info(f"💬 Retour ajouté: {user_id} -> {feedback}")
    
    def _update_loop(self):
        """Boucle principale de mise à jour"""
        while self.is_running:
            try:
                current_time = datetime.now()
                time_since_last_update = (current_time - self.last_update).total_seconds()
                
                # Vérifier si une mise à jour est nécessaire
                should_update = (
                    time_since_last_update >= self.update_interval or
                    self.update_count >= self.min_updates_threshold
                )
                
                if should_update and not self.update_queue.empty():
                    self._perform_model_update()
                
                # Dormir un court moment avant la prochaine vérification
                time.sleep(min(60, self.update_interval // 10))
                
            except Exception as e:
                self.logger.error(f"❌ Erreur dans la boucle de mise à jour: {e}")
                if self.on_update_failed:
                    self.on_update_failed(e)
                time.sleep(60)  # Attendre avant de réessayer
    
    def _trigger_immediate_update(self):
        """Déclenche une mise à jour immédiate"""
        self.logger.info("⚡ Déclenchement d'une mise à jour immédiate")
        threading.Thread(target=self._perform_model_update, daemon=True).start()
    
    def _perform_model_update(self):
        """Effectue la mise à jour des modèles"""
        self.logger.info("🔄 Début de la mise à jour des modèles...")
        start_time = time.time()
        
        try:
            # Traiter toutes les mises à jour en file
            updates_processed = []
            while not self.update_queue.empty():
                update_data = self.update_queue.get()
                updates_processed.append(update_data)
            
            if not updates_processed:
                return
            
            # Créer une sauvegarde des modèles actuels
            self._backup_current_models()
            
            # Re-entraîner les modèles collaboratifs
            self.hybrid_system.train_collaborative_models()
            
            # Sauvegarder les nouveaux modèles
            self.hybrid_system.save_models('models/hybrid_models_latest.pkl')
            
            # Mettre à jour les statistiques
            self.last_update = datetime.now()
            update_time = time.time() - start_time
            
            self.logger.info(f"✅ Mise à jour réussie!")
            self.logger.info(f"📊 {len(updates_processed)} mises à jour traitées")
            self.logger.info(f"⏱️  Temps de mise à jour: {update_time:.2f}s")
            
            # Réinitialiser le compteur
            self.update_count = 0
            
            # Déclencher le callback de succès
            if self.on_model_updated:
                self.on_model_updated(len(updates_processed), update_time)
            
            # Enregistrer les métriques de performance
            self._log_performance_metrics(updates_processed, update_time)
            
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la mise à jour: {e}")
            self._restore_backup_models()
            if self.on_update_failed:
                self.on_update_failed(e)
    
    def _backup_current_models(self):
        """Sauvegarde les modèles actuels"""
        try:
            Path('models/backups').mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f'models/backups/hybrid_models_backup_{timestamp}.pkl'
            
            self.hybrid_system.save_models(backup_path)
            self.logger.info(f"💾 Sauvegarde créée: {backup_path}")
            
        except Exception as e:
            self.logger.warning(f"⚠️  Erreur lors de la sauvegarde: {e}")
    
    def _restore_backup_models(self):
        """Restaure les modèles depuis la dernière sauvegarde"""
        try:
            backup_dir = Path('models/backups')
            if backup_dir.exists():
                backup_files = list(backup_dir.glob('hybrid_models_backup_*.pkl'))
                if backup_files:
                    latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
                    self.hybrid_system.load_models(str(latest_backup))
                    self.logger.info(f"🔄 Modèles restaurés depuis: {latest_backup}")
                    
        except Exception as e:
            self.logger.error(f"❌ Erreur lors de la restauration: {e}")
    
    def _log_performance_metrics(self, updates: List[Dict], update_time: float):
        """Enregistre les métriques de performance"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'updates_count': len(updates),
                'update_time_seconds': update_time,
                'update_types': {},
                'user_activity': {}
            }
            
            # Analyser les types de mises à jour
            for update in updates:
                update_type = update['type']
                metrics['update_types'][update_type] = metrics['update_types'].get(update_type, 0) + 1
                
                user_id = update['user_id']
                metrics['user_activity'][user_id] = metrics['user_activity'].get(user_id, 0) + 1
            
            # Sauvegarder les métriques
            metrics_file = 'models/performance_metrics.jsonl'
            with open(metrics_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(metrics) + '\n')
                
        except Exception as e:
            self.logger.warning(f"⚠️  Erreur logging métriques: {e}")
    
    def get_system_status(self) -> Dict:
        """Retourne l'état actuel du système"""
        return {
            'is_running': self.is_running,
            'last_update': self.last_update.isoformat(),
            'pending_updates': self.update_queue.qsize(),
            'update_count_since_last': self.update_count,
            'update_interval_seconds': self.update_interval,
            'min_updates_threshold': self.min_updates_threshold,
            'time_until_next_update': max(0, self.update_interval - 
                                        (datetime.now() - self.last_update).total_seconds())
        }
    
    def force_update(self):
        """Force une mise à jour immédiate"""
        self.logger.info("🔥 Mise à jour forcée demandée")
        self._trigger_immediate_update()
    
    def get_performance_history(self, days: int = 7) -> List[Dict]:
        """Récupère l'historique des performances"""
        try:
            metrics_file = 'models/performance_metrics.jsonl'
            if not Path(metrics_file).exists():
                return []
            
            cutoff_date = datetime.now() - timedelta(days=days)
            history = []
            
            with open(metrics_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        metric = json.loads(line.strip())
                        metric_date = datetime.fromisoformat(metric['timestamp'])
                        
                        if metric_date >= cutoff_date:
                            history.append(metric)
                    except:
                        continue
            
            return sorted(history, key=lambda x: x['timestamp'])
            
        except Exception as e:
            self.logger.error(f"❌ Erreur récupération historique: {e}")
            return []

class AdaptiveLearningSystem:
    """Système d'apprentissage adaptatif"""
    
    def __init__(self, hybrid_system, rating_system):
        self.hybrid_system = hybrid_system
        self.rating_system = rating_system
        self.learning_rate = 0.01
        
    def adapt_content_weights(self, feedback_data: List[Dict]):
        """Adapte les poids du système hybride basé sur les retours"""
        if not feedback_data:
            return
        
        # Analyser les retours pour ajuster les poids
        positive_feedback = sum(1 for fb in feedback_data if fb['feedback'] in ['like', 'watched'])
        total_feedback = len(feedback_data)
        
        if total_feedback > 0:
            success_rate = positive_feedback / total_feedback
            
            # Ajuster les poids basé sur le taux de succès
            if success_rate < 0.6:  # Mauvaise performance
                # Augmenter légèrement le poids collaboratif
                new_collab_weight = min(0.8, self.hybrid_system.collaborative_weight + self.learning_rate)
                new_content_weight = 1.0 - new_collab_weight
                
                self.hybrid_system.collaborative_weight = new_collab_weight
                self.hybrid_system.content_weight = new_content_weight
                
                print(f"🎛️  Poids ajustés: Contenu={new_content_weight:.2f}, "
                      f"Collaboratif={new_collab_weight:.2f}")

def demo_realtime_system():
    """Démonstration du système en temps réel"""
    print("⚡ Démonstration du Système Temps Réel")
    print("=====================================")
    
    try:
        from movie_recommender import MovieRecommender
        from user_rating_system import UserRatingSystem
        from hybrid_recommender import HybridRecommendationSystem
        
        # Initialiser les composants
        content_recommender = MovieRecommender()
        rating_system = UserRatingSystem()
        hybrid_system = HybridRecommendationSystem(content_recommender, rating_system)
        
        # Créer le système de mise à jour temps réel
        updater = RealTimeModelUpdater(
            hybrid_system, 
            rating_system,
            update_interval=10,  # 10 secondes pour la démo
            min_updates_threshold=3
        )
        
        # Callbacks pour les événements
        def on_update_success(updates_count, time_taken):
            print(f"✅ Modèles mis à jour! {updates_count} changements en {time_taken:.2f}s")
        
        def on_update_failed(error):
            print(f"❌ Échec mise à jour: {error}")
        
        updater.on_model_updated = on_update_success
        updater.on_update_failed = on_update_failed
        
        # Démarrer le système
        updater.start_real_time_updates()
        
        # Simuler des activités utilisateur
        print("\n🎭 Simulation d'activité utilisateur...")
        
        # Simuler des notes
        test_ratings = [
            ('user1', 157336, 8.5),
            ('user2', 155, 9.0),
            ('user1', 27205, 7.5),
            ('user3', 244786, 9.5),
        ]
        
        for user_id, movie_id, rating in test_ratings:
            updater.queue_rating_update(user_id, movie_id, rating)
            time.sleep(1)
        
        # Attendre un peu pour voir les mises à jour
        print("\n⏳ Attente des mises à jour automatiques...")
        time.sleep(15)
        
        # Afficher l'état du système
        status = updater.get_system_status()
        print(f"\n📊 État du système:")
        print(f"  🏃 En cours: {status['is_running']}")
        print(f"  🕐 Dernière mise à jour: {status['last_update']}")
        print(f"  📋 Mises à jour en attente: {status['pending_updates']}")
        
        # Arrêter le système
        updater.stop_real_time_updates()
        
    except Exception as e:
        print(f"❌ Erreur démonstration: {e}")
        print("💡 Assurez-vous que tous les modules sont disponibles")

if __name__ == "__main__":
    demo_realtime_system()
