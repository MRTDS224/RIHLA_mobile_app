import secrets
import string
from datetime import datetime, timedelta
from .database import db
from .models import User

class AuthService:
    @staticmethod
    def register(email, password, first_name=None, last_name=None):
        """Enregistre un nouvel utilisateur"""
        if db.get_user_by_email(email):
            return None, "Email déjà utilisé"
        
        user_id = db.add_user(email, password, first_name, last_name)
        if not user_id:
            return None, "Erreur lors de la création du compte"
        
        return User(
            id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name
        ), None

    @staticmethod
    def login(email, password):
        """Connecte un utilisateur"""
        user_data = db.verify_user(email, password)
        if not user_data:
            return None, "Email ou mot de passe incorrect"
        
        user_id, first_name, last_name, preferences = user_data
        return User(
            id=user_id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            preferences=preferences
        ), None

    @staticmethod
    def delete_account(user_id):
        """Supprime le compte utilisateur"""
        
        success = db.delete_user(user_id)
        if not success:
            return False, "Erreur lors de la suppression du compte"
        
        return True, None
    
    @staticmethod
    def update_profile(user_id, **kwargs):
        """Met à jour le profil utilisateur"""
        
        success = db.update_user(user_id, **kwargs)
        if not success:
            return False, "Aucune modification effectuée"
        
        return True, None

    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change le mot de passe"""
        user = db.get_user_by_id(user_id)
        if not user:
            return False, "Utilisateur non trouvé"
        
        _, stored_pw, *_ = user
        if db._hash_password(current_password) != stored_pw:
            return False, "Mot de passe actuel incorrect"
        
        db.update_password(user_id, new_password)
        return True, None

    @staticmethod
    def initiate_password_reset(email):
        """Initie une réinitialisation de mot de passe"""
        user = db.get_user_by_email(email)
        if not user:
            return None, "Email non trouvé"
        
        # Générer un token (simplifié pour le test)
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        expires_at = datetime.now() + timedelta(hours=1)
        
        # Enregistrer le token (simplifié)
        cursor = db.conn.cursor()
        cursor.execute('''
        INSERT INTO password_resets (user_id, token, expires_at)
        VALUES (?, ?, ?)
        ''', (user[0], token, expires_at))
        db.conn.commit()
        
        return token, None

    @staticmethod
    def complete_password_reset(token, new_password):
        """Complète la réinitialisation du mot de passe"""
        cursor = db.conn.cursor()
        cursor.execute('''
        SELECT user_id, expires_at, used 
        FROM password_resets 
        WHERE token = ?
        ''', (token,))
        reset_data = cursor.fetchone()
        
        if not reset_data:
            return False, "Token invalide"
        
        user_id, expires_at, used = reset_data
        
        if used or datetime.now() > datetime.fromisoformat(expires_at):
            return False, "Token expiré ou déjà utilisé"
        
        # Mettre à jour le mot de passe
        db.update_password(user_id, new_password)
        
        # Marquer le token comme utilisé
        cursor.execute('''
        UPDATE password_resets SET used = 1 WHERE token = ?
        ''', (token,))
        db.conn.commit()
        
        return True, None