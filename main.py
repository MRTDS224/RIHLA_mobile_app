from kivy.config import Config

# Définir la taille de la fenêtre (par exemple, 360x640 pour un téléphone standard)
Config.set('graphics', 'width', '360')  # Largeur en pixels
Config.set('graphics', 'height', '640')  # Hauteur en pixels
Config.set('graphics', 'resizable', False)  # Désactiver le redimensionnement de la fenêtre

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.uix.filechooser import FileChooserIconView
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
import cv2
from classUsers import Users
from modules.assistant import Assistant
from modules.recommender import Recommender
from modules.translator import Translator
from modules.image_recognition import predict_monument
from modules.send_email import send_email_with_attachment
from functools import partial
import pygame
from auth.services import AuthService
from auth.models import User

def show_popup(title, message, text_color=(0, 0, 0, 1)):
    """
    Affiche un popup avec un message et une couleur de texte personnalisée.
    
    :param title: Titre du popup
    :param message: Message à afficher
    :param text_color: Couleur du texte (par défaut : noir)
    """
    # Créer un label avec une largeur limitée
    content = Label(
        text=message,
        text_size=(400, None),  # Limiter la largeur du texte à 400 pixels
        size_hint_y=None,
        pos_hint={'center_y': 0.5},
        color=text_color
    )
    content.bind(
        texture_size=lambda instance, value: setattr(instance, 'height', value[1])
    )  # Ajuster la hauteur du Label en fonction de son contenu

    # Créer une popup pour afficher les messages d'erreur
    popup = Popup(
        title=title,
        title_color=(1, 0, 0, 1),  # Rouge
        content=content,
        size_hint=(0.8, None),
        height=content.height + 100,  # Ajuster la hauteur du popup,
        auto_dismiss=True,
        background='white',
        background_color=(0.7, 1, 0.7, 0.9),  # Rouge
    )
    popup.open()

class RootWidget(BoxLayout):
    allowed_screens = ['assistant', 'translation', 'recommendation', 'recognition']
    
    def update_nav_bar_visibility(self, *args):
        current = self.ids.screen_manager.current
        nav_bar = self.ids.navigation_bar
        title_bar = self.ids.title_bar
        if current in self.allowed_screens:
            # Rendre la barre visible
            nav_bar.height = '50dp'  # Ajuster la hauteur de la barre de navigation
            nav_bar.opacity = 1  # Rendre la barre visible
            nav_bar.disabled = False  # Activer la barre de navigation
            
            title_bar.height = '50dp'
            title_bar.opacity = 1
            title_bar.disabled = False
            
            # Mettre à jour le titre de la barre
            if current == 'translation':
                title_bar.ids.title.text = "Traduction"
            elif current == 'recommendation':
                title_bar.ids.title.text = "Recommandations"
            elif current == 'recognition':
                title_bar.ids.title.text = "Reconnaissance d'image"
            elif current == 'assistant':
                title_bar.ids.title.text = "Assistant virtuel"
        else:
            # Masquer la barre
            nav_bar.height = 0
            nav_bar.opacity = 0
            nav_bar.disabled = True
            
            title_bar.height = 0
            title_bar.opacity = 0
            title_bar.disabled = True

    def on_kv_post(self, base_widget):
        sm = self.ids.screen_manager
        nav = self.ids.navigation_bar
        nav.current_screen = sm.current
        sm.bind(current=nav.setter('current_screen'))
    
class ChatBubble(BoxLayout):
    message_text = StringProperty("")
    bubble_width = NumericProperty(0)

class ChatMessage(BoxLayout):
    message_text = StringProperty("")
    is_sent = BooleanProperty(False)
    timestamp = StringProperty("")

class AssistantScreen(Screen):
    thinking = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history = []
        Clock.schedule_once(self._finish_init)
    
    def _finish_init(self, dt):
        """Ajoute un message de bienvenue après l'initialisation"""
        self.add_bot_message("Bonjour ! Je suis votre assistant. Comment puis-je vous aider ?")
    
    def send_message(self, text):
        if not text.strip() or self.thinking:
            return
            
        self.add_user_message(text)
        self.simulate_bot_response(text)
    
    def add_user_message(self, text):
        """Ajoute un message de l'utilisateur à l'interface"""
        self.history.append(("user", text))
        self._add_message_to_ui(text, is_sent=True)
        self.ids.message_input.text = ""
    
    def add_bot_message(self, text):
        """Ajoute un message du bot à l'interface"""
        self.history.append(("bot", text))
        self._add_message_to_ui(text, is_sent=False)
    
    def _add_message_to_ui(self, text, is_sent):
        """Ajoute un message à l'interface graphique"""
        msg = ChatMessage(is_sent=is_sent, message_text=text)
        # Accédez au messages_box via la hiérarchie des widgets
        messages_box = self.ids.messages_box
        messages_box.add_widget(msg)
        Clock.schedule_once(lambda dt: self.ids.scroll_view.scroll_to(msg), 0.1)
    
    def simulate_bot_response(self, user_text):
        """Simule une réponse du bot"""
        self.thinking = True
        self.ids.send_btn.disabled = True
        
        Clock.schedule_once(lambda dt: self._generate_response(user_text), 1)
    
    def _generate_response(self, user_text):
        """Génère une réponse du bot en utilisant l'assistant"""
        prompt = f"You are a helpful assistant. I need you to answer the following question:\n{user_text}\nPlease provide a concise and informative response."
        response = Assistant.get_response(prompt)
        self.add_bot_message(response)
        self.thinking = False
        self.ids.send_btn.disabled = False

    def on_message_input(self, instance, value):
        if hasattr(self, 'ids'):
            if value.strip():
                self.ids.send_btn.background_color = get_color_from_hex("#25D366")  # Vert
            else:
                self.ids.send_btn.background_color = get_color_from_hex("#FF3B30")  # Rouge
class TitleBar(BoxLayout):
    def change_screen(self, screen_name):
        """
        Change l'écran actif du ScreenManager.
        :param screen_name: Nom de l'écran à afficher
        """
        sm = App.get_running_app().root.ids.screen_manager
        if screen_name == 'Compte':
            self.ids.menu_spinner.text = 'Menu'
            sm.current = 'account'
        else:
            self.ids.menu_spinner.text = 'Menu'
            App.get_running_app().logout()

class HomeScreen(Screen):
    can_login = BooleanProperty(False)  # Propriété pour contrôler l'accès à la connexion
    
    def on_text_fields(self, *args):
        email = self.ids.email.text.strip()
        password = self.ids.password.text.strip()
        self.can_login = bool(email and password)
    
    def login(self):
        email = self.ids.email.text
        self.ids.email.text = ''
        password = self.ids.password.text
        self.ids.password.text = ''
        
        # Vérifier que les champs ne sont pas vides
        if not email or not password:
            show_popup("Erreur", "Veuillez remplir tous les champs.")
            return

        if email == "a" and password == "a":
            self.ids.message.text = "Connexion réussie, Soyez la bienvenue"
            self.ids.message.text = ""
            # Rediriger vers l'écran de traduction
            App.get_running_app().root.ids.screen_manager.current = 'translation'
            return

        # Chercher l'utilisateur
        user, error = AuthService.login(email, password)
        if error:
            show_popup("Erreur", f"Erreur de connexion : {error}")
            self.ids.message.text = "Erreur de connexion, veuillez réessayer"
            return
        
        self.ids.message.text = "Connexion réussie, Soyez la bienvenue"
        self.ids.message.text = ""
        
        App.get_running_app().user = user  # Stocker l'utilisateur dans l'application
        # Rediriger vers l'écran de traduction
        App.get_running_app().root.ids.screen_manager.current = 'translation'

class SignupScreen(Screen):
    def go_to_preferences_screen(self):
        # Récupérer les informations saisies par l'utilisateur
        first_name = self.ids.first_name.text
        last_name = self.ids.last_name.text
        email = self.ids.email.text
        password = self.ids.password.text
        confirm_password = self.ids.confirm_password.text
        
        # Supprimer les informations saisies
        self.ids.first_name.text = ''
        self.ids.last_name.text = ''
        self.ids.email.text = ''
        self.ids.password.text = ''
        self.ids.confirm_password.text = ''
        
        # Vérifier que les mots de passe correspondent
        if password != confirm_password:
            show_popup("Erreur", "Les mots de passe ne correspondent pas.")
            return

        # Validation simple des champs
        if not first_name or not last_name or not email or not password:
            show_popup("Erreur", "Tous les champs doivent être remplis.")
            return

        # Validation de l'email et du mot de passe
        try:
            user = Users(last_name, first_name, email, password)
            
            # Stocker l'utilisateur dans l'application
            App.get_running_app().user = user  
            
            # Rediriger vers l'écran de traduction
            App.get_running_app().root.ids.screen_manager.current = 'preferences'

        except ValueError as e:
            show_popup("Erreur", str(e))
            return

class PreferencesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_preferences = []  # Liste pour stocker les goûts sélectionnés

    def toggle_preference(self, preference):
        """
        Ajoute ou supprime un goût touristique de la liste des préférences sélectionnées.
        Limite la sélection à 3 goûts maximum.
        """
        if preference in self.selected_preferences:
            self.selected_preferences.remove(preference)
            print(f"{preference} retiré de la sélection.")
            self.ids.title.text = f"Préférence retirée : {preference}\nPréférences sélectionnées : {', '.join(self.selected_preferences)}\nIl vous reste {3 - len(self.selected_preferences)} choix."
        elif len(self.selected_preferences) < 3:
            self.selected_preferences.append(preference)
            self.ids.title.text = f"Préférences sélectionnées : {', '.join(self.selected_preferences)}\nIl vous reste {3 - len(self.selected_preferences)} choix."
            print(f"{preference} ajouté à la sélection.")
        else:
            self.ids.message.text = "Vous ne pouvez sélectionner que 3 goûts maximum."

        print(f"Préférences sélectionnées : {self.selected_preferences}")

    def create_account(self):
        """
        Enregistre les préférences sélectionnées.
        """
        if not self.selected_preferences:
            show_popup("Erreur", "Veuillez sélectionner au moins un goût touristique.")
            return

        # Logique pour enregistrer les préférences (par exemple, dans un fichier JSON ou une base de données)
        print(f"Préférences enregistrées : {self.selected_preferences}")
        self.ids.message.text = "Vos préférences ont été enregistrées avec succès."
        
        # Sauvegarder l'utilisateur dans le fichier JSON
        user = App.get_running_app().user
        user.preferences = self.selected_preferences
        try:
            self.save_user_to_json(user)
        except ValueError as e:
            show_popup("Erreur", str(e))
            return
        
        # Afficher un message de succès après l'enregistrement durant 2 secondes
        Clock.schedule_once(lambda dt: self.show_success_message(), 2)
        
    def show_success_message(self):
        """ Affiche un message de succès après l'enregistrement des préférences.
        """
        self.ids.message.text = "Votre compte a été créé avec succès."
        
        # Supprimer le message après 2 secondes
        Clock.schedule_once(lambda dt: self.ids.message.__setattr__('text', ""), 2)
        
        # Rediriger vers l'écran de traduction
        App.get_running_app().root.ids.screen_manager.current = 'translation'
    
    def save_user_to_json(self, user):
        saved_user, error = AuthService.register(user.email, user.password, user.first_name, user.last_name)
        if error:
            raise ValueError(f"Erreur lors de l'enregistrement de l'utilisateur : {error}")

class EmailInputScreen(Screen):
    def send_reset_code(self):
        email = self.ids.email_reset.text
        self.ids.email_reset.text = ''
        
        if not email:
            show_popup("Erreur", "Veuillez entrer une adresse e-mail.")
            return
        
        token, error = AuthService.initiate_password_reset(email)
        App.get_running_app().email_reset = email
        App.get_running_app().token = token  # Stocker le token pour la vérification ultérieure
        if error:
            show_popup("Erreur", f"Erreur lors de l'initiation de la réinitialisation : {error}")
            return
        
        code = send_email_with_attachment(email)
        if code:
            App.get_running_app().root.ids.screen_manager.current = 'code_input'
            App.get_running_app().generated_code = code  # Stocker le code généré pour la vérification
            print(f"Code envoyé à {email}: {code}")  # Pour le débogage
        else:
            show_popup("Erreur", "Échec de l'envoi du code de réinitialisation. Vérifiez l'adresse e-mail.")

class CodeInputScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.remaining_time = 180
        self.timer_running = False
        self.count = 0  # Compteur pour le nombre de tentatives de saisie du code
        
    def on_pre_enter(self):
        """Méthode appelée avant que l'utilisateur n'entre dans l'écran CodeInputScreen.
        Réinitialise le compteur de tentatives de saisie du code. 
        """
        self.count = 0
        self.ids.code_input.text = ''
        
    def on_enter(self):
        """
        Méthode appelée lorsque l'utilisateur entre dans l'écran CodeInputScreen.
        Démarre le compte à rebours pour la validité du code.
        """
        if not self.timer_running:
            self.timer_running = True
            self.remaining_time = 180
            self.ids.countdown_label.text = "Temps restant : 3:00"
            self.ids.resend_button.disabled = True
            Clock.schedule_interval(self.update_timer, 1)
            
    def update_timer(self, dt):
        """
        Met à jour le compte à rebours toutes les secondes.
        Si le temps est écoulé, désactive le bouton de renvoi et affiche un message.
        """
        if self.remaining_time > 0:
            minutes, seconds = divmod(self.remaining_time, 60)
            
            # Animation de fade-out avant mise à jour
            fade_out = Animation(opacity=0.3, duration=0.2)
            fade_out.bind(on_complete=lambda *args: self.update_text(minutes, seconds))
            fade_out.start(self.ids.countdown_label)
            self.remaining_time -= 1
        else:
            self.ids.countdown_label.text = "Code expiré."
            self.ids.resend_button.disabled = False
            Clock.unschedule(self.update_timer)
            self.timer_running = False
    
    def update_text(self, minutes, seconds):
        """ Met à jour le texte et applique une animation de réapparition """
        self.ids.countdown_label.text = f"Temps restant : {minutes:02}:{seconds:02}"

        # Animation de fade-in après mise à jour
        fade_in = Animation(opacity=1, duration=0.3)
        fade_in.start(self.ids.countdown_label)
    
    def verify_code(self):
        entered_code = self.ids.code_input.text
        self.ids.code_input.text = ''
        
        if entered_code == App.get_running_app().generated_code:
            App.get_running_app().generated_code = None  # Réinitialiser le code généré
            App.get_running_app().root.ids.screen_manager.current = 'new_password'
        else:
            show_popup("Erreur", "Code incorrect. Veuillez réessayer.")

    def resend_code(self):
        """ Envoie un nouvel email contenant un code si le code précédent a expiré ou est incorrect,
        et le nombre de tentatives de saisie du code est inférieur à 3.
        """
        if self.count >= 3:
            show_popup("Erreur", "Vous avez atteint le nombre maximum de tentatives de saisie du code.")
            App.get_running_app().root.ids.screen_manager.current = 'home'
            return
        
        self.count += 1  # Incrémenter le compteur de tentatives
        user_email = App.get_running_app().email_reset
        App.get_running_app().generated_code = send_email_with_attachment(user_email)

        # Réinitialiser le décompteur après l'envoi du code
        self.remaining_time = 180
        self.ids.countdown_label.text = "Temps restant : 3:00"
        self.ids.resend_button.disabled = True  # Désactiver temporairement
        Clock.schedule_interval(self.update_timer, 1)
        
class NewPasswordScreen(Screen):
    def reset_password(self):
        new_password = self.ids.new_password.text
        confirm_password = self.ids.confirm_new_password.text
        
        self.ids.new_password.text = ''
        self.ids.confirm_new_password.text = ''
        
        if new_password != confirm_password:
            show_popup("Erreur", "Les mots de passe ne correspondent pas.")
            return
        
        token = App.get_running_app().token
        
        success, error = AuthService.complete_password_reset(token, new_password)
        if error:
            show_popup("Erreur", f"Erreur lors de la réinitialisation du mot de passe : {error}")
            return
        
        self.ids.message.text = "Mot de passe réinitialisé avec succès."
        # Rediriger vers l'écran de connexion
        Clock.schedule_once(self.go_to_login, 2)
    
    def go_to_login(self, dt):
        # Rediriger vers l'écran de connexion après 2 secondes
        App.get_running_app().root.ids.screen_manager.current = 'home' 
   
class AccountScreen(Screen):
    def on_enter(self, *args):
        """
        Méthode appelée lorsque l'utilisateur entre dans l'écran.
        Affiche les informations de l'utilisateur connecté.
        """
        user = App.get_running_app().user
        if user:
            self.ids.user_first_name.text = user.first_name
            self.ids.user_last_name.text = user.last_name
            self.ids.user_email.text = user.email
            self.ids.user_preferences.text = ', '.join(pref if pref is not None else "" for pref in user.preferences) if user.preferences else "Aucune préférence sélectionnée"
       
    def activate_modify_account(self, boolean):
        """
        Active ou desactive le mode de modification des informations de l'utilisateur.
        Affiche ou Masque les champs de saisie pour modifier les informations.
        """
        
        # Activer les champs de saisie pour la modification
        self.ids.user_first_name.disabled = boolean
        self.ids.user_last_name.disabled = boolean
        self.ids.user_email.disabled = boolean
        self.ids.user_preferences.disabled = boolean
        self.ids.save_button.opacity = 1
        self.ids.save_button.disabled = not boolean
         
    def modify_account(self):
        """
        Modifie les informations de l'utilisateur connecté.
        """
        user = App.get_running_app().user
        if not user:
            show_popup("Erreur", "Aucun utilisateur connecté.")
            return
        
        # Récupérer les nouvelles informations saisies par l'utilisateur
        new_first_name = self.ids.user_first_name.text.strip()
        new_last_name = self.ids.user_last_name.text.strip()
        new_email = self.ids.user_email.text.strip()
        new_preferences = self.ids.user_preferences.text.strip().split(",") if self.ids.user_preferences.text else []
        
        # Vérifier que les champs ne sont pas vides
        if not new_first_name or not new_last_name or not new_email:
            show_popup("Erreur", "Tous les champs doivent être remplis.")
            return
        
        # Mettre à jour les informations de l'utilisateur
        user.first_name = new_first_name
        user.last_name = new_last_name
        user.email = new_email
        user.preferences = [pref.strip() for pref in new_preferences if pref.strip()]  # Nettoyer les préférences
        
        # Enregistrer les modifications dans la base de données
        success, error = AuthService.update_profile(
            user.id,
            first_name=new_first_name,
            last_name=new_last_name,
            email=new_email,
            preferences=user.preferences
        )
        if error:
            show_popup("Erreur", f"Erreur lors de la mise à jour du compte : {error}")
            return
        
        self.activate_modify_account(False)  # Désactiver le mode de modification
        App.get_running_app().user = user  # Mettre à jour l'utilisateur dans l'application
        show_popup("Succès", "Informations du compte mises à jour avec succès.")
            
    def delete_account(self):
        """
        Supprime le compte de l'utilisateur connecté.
        """
        user = App.get_running_app().user
        if not user:
            show_popup("Erreur", "Aucun utilisateur connecté.")
            return
        
        # Demander confirmation avant de supprimer le compte
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        content.add_widget(Label(text="Êtes-vous sûr de vouloir supprimer votre compte ? Cette action est irréversible.", size_hint_y=None, height=200, text_size=(300, None), color=(0, 0, 0, 1)))
        input_password = TextInput(
            hint_text="Entrez votre mot de passe pour confirmer",
            password=True,
            size_hint_y=None,
            height=60
        )
        content.add_widget(input_password)
        
        btn_layout = BoxLayout(size_hint_y=None, height=50)
        btn_layout.add_widget(Button(text="Annuler", on_release=lambda x: popup.dismiss(), background_color=(0, 1, 0, 1)))
        btn_layout.add_widget(Button(text="Supprimer", on_release=lambda x: App.get_running_app().delete_account(input_password.text, popup), background_color=(1, 0, 0, 1)))  
        
        content.add_widget(btn_layout)
        
        popup = Popup(title="Confirmation de suppression", title_color=(1, 0, 0, 1), content=content, size_hint=(0.8, 0.4), auto_dismiss=False, background='white') 
        popup.open()    
class TranslationScreen(Screen):
    Languages = {
        'Detection automatique': 'auto',
        'Anglais': 'en',
        'Français': 'fr',
        'Espagnol': 'es',
        'Allemand': 'de',
        'Italien': 'it',
        'Arabe': 'ar',
        'Chinois': 'zh-CN',
        'Japonais': 'ja'
    }
    
    def translate_text(self):
        text = self.ids.source_text.text
        source_language = self.ids.source_language.text
        target_language = self.ids.target_language.text
        
        # Si le darija texte source est en Darija, on utilise la traduction spécifique
        if source_language == "Darija":
            prompt = f"Translate this from Moroccan Darija Arabic to {target_language}:\n{text}\nGive me the translation in Slightly more formal. give me only one proposition."
            translation = Translator.translate_to_darija(prompt)
            if translation.startswith("Erreur:"):
                show_popup("Erreur", translation, text_color=(1, 0, 0, 1))
            else:
                # Afficher la traduction dans le champ de texte
                self.ids.translated_text.text = translation
            return
        
        # Si la langue cible est le Darija, on utilise la traduction spécifique
        if self.ids.target_language.text == "Darija":
            prompt = f"Translate this from {source_language} to Moroccan Darija Arabic:\n{text}\nGive me the translation in Slightly more formal. give me only one proposition."
            translation = Translator.translate_to_darija(prompt)
            if translation.startswith("Erreur:"):
                show_popup("Erreur", translation, text_color=(1, 0, 0, 1))
            else:
                # Afficher la traduction dans le champ de texte
                self.ids.translated_text.text = translation
            return
        
        source_language = self.Languages.get(source_language, 'en')  # Par défaut à l'anglais
        target_language = self.Languages.get(target_language, 'en')  # Par défaut à l'anglais
        translation = Translator.translate(text, source_language, target_language)
        self.ids.translated_text.text = translation
        if translation.startswith("Erreur:"):
            show_popup("Erreur", translation, text_color=(1, 0, 0, 1))
    
    def listen_translation(self):
        text = self.ids.translated_text.text
        if not text:
            show_popup("Erreur", "Aucune traduction à lire.")
            return
        # Logique pour lire le texte traduit  à implémenter après
        print(f"Lecture du texte traduit : {text}")
        self.ids.message_label.text = "Fonctionnalité en cours de developpement..."
        
    def record_audio(self):
        self.ids.message_label.text = "Fonctionnalité en cours de developpement..."

class RecommendationScreen(Screen):
    def on_enter(self):
        """
        Méthode appelée lorsque l'utilisateur entre dans l'écran.
        Affiche tous les sites touristiques.
        """
        # Récupérer tous les sites touristiques
        tourist_sites = Recommender.get_sites()
        # Appeler la méthode générique pour afficher les sites
        self.display_recommendations(tourist_sites)

    def research_recommendations(self):
        """
        Recherche les recommandations basées sur l'entrée utilisateur et les affiche dynamiquement.
        """
        # Récupérer l'entrée utilisateur
        preferences = self.ids.preferences_input.text.split(",")

        # Obtenir les recommandations
        recommendations = Recommender.get_recommendations(preferences)

        # Vérifier si aucune recommandation n'a été trouvée
        if recommendations == "Aucune recommandation trouvée.":
            self.ids.recommendations_scroll.clear_widgets()
            self.ids.recommendations_scroll.add_widget(Label(
                text=f"[b]Aucune recommandation trouvée.[/b]",
                markup=True, font_size=30, color=(0, 0, 0, 1),
                halign='center', valign='middle',
                size_hint_y=None, height=50
            ))
            return

        # Appeler la méthode générique pour afficher les recommandations
        self.display_recommendations(recommendations)

    def display_recommendations(self, sites):
        """
        Affiche une liste de sites touristiques dans le ScrollView.
        :param sites: Liste des sites touristiques à afficher
        """
        # Récupérer le ScrollView et le GridLayout
        sc = self.ids.recommendations_scroll
        grid = GridLayout(cols=1, spacing=20, padding=(20, 20, 20, 20), size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))  # Ajuster la hauteur du GridLayout

        # Effacer les widgets existants
        sc.clear_widgets()

        # Ajouter dynamiquement les résultats
        for site in sites:
            # BoxLayout principal (horizontal)
            box = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=200)

            # Image du site touristique
            image = Image(source=site.get('image', ""), size_hint=(0.3, 1))
            box.add_widget(image)

            # BoxLayout pour les détails du site
            second_box = BoxLayout(orientation='vertical', size_hint_x=0.7, spacing=5, padding=[10, 0, 10, 0])

            # Nom du site (en gras)
            label_site_name = Label(
                text=f"[b]{site.get('name', 'Nom inconnu')}[/b]",
                markup=True, font_size=20, color=(1, 1, 1, 1),
                halign='left', valign='middle', text_size=(300, None),
                size_hint_y=None, height=30
            )
            second_box.add_widget(label_site_name)

            # Localisation du site
            label_site_location = Label(
                text=f"📍 {site.get('location', 'Lieu inconnu')}",
                font_name="seguiemj",
                font_size=16, color=(1, 1, 1, 1),
                halign='left', valign='middle', text_size=(300, None),
                size_hint_y=None, height=30
            )
            second_box.add_widget(label_site_location)

            # Description du site (tronquée)
            description = site.get('description', 'Aucune description disponible')
            site_description = description[:80] + "..." if len(description) > 80 else description
            label_site_description = Label(
                text=site_description,
                font_size=16, color=(1, 1, 1, 1),
                halign='left', valign='top', text_size=(300, None),
                size_hint_y=None, height=50
            )
            second_box.add_widget(label_site_description)

            # Informations supplémentaires (Durée, Prix, Note)
            info_text = f"🕒 {site.get('duration', 'N/A')}      💰 {site.get('price', 'N/A')}       ⭐ {site.get('rating', 'N/A')}"
            label_info = Label(
                text=info_text,
                font_name="seguiemj",
                font_size=16, color=(1, 1, 1, 1),
                halign='left', valign='middle', text_size=(300, None),
                size_hint_y=None, height=30,
                
            )
            second_box.add_widget(label_info)

            # Bouton "Voir plus"
            button = Button(
                text="Voir plus", size_hint_y=None, height=40,
                on_press=partial(self.show_details, site),
                background_normal='', color=(1, 1, 1, 1),
                background_color=(0, 1, 0, 1)
            )
            second_box.add_widget(button)

            # Ajouter la box secondaire et la box principale au GridLayout
            box.add_widget(second_box)
            grid.add_widget(box)

        # Ajouter le GridLayout au ScrollView
        sc.add_widget(grid)
         
    def show_details(self, site, *args):
        """
        Redirige vers l'écran RecommendationDetailScreen et affiche les détails complets du site.
        """
        # Récupérer l'écran RecommendationDetailScreen
        detail_screen = self.manager.get_screen('recommendation_detail')

        # Mettre à jour les informations du site sur l'écran de détails
        detail_screen.ids.recommendation_detail_label.text = f"[b]{site.get('name', 'Nom inconnu')}[/b]"
        detail_screen.ids.recommendation_detail_location.text = f"📍 {site.get('location', 'Lieu inconnu')}"
        detail_screen.ids.recommendation_detail_description.text = site.get('description', 'Aucune description disponible')
        detail_screen.ids.recommendation_detail_info.text = (
            f"🕒 {site.get('duration', 'N/A')}      💰 {site.get('price', 'N/A')}       ⭐ {site.get('rating', 'N/A')}"
        )
        detail_screen.ids.recommendation_detail_image.source = site.get('image', '')
        detail_screen.audio_path = site.get('audio', '')  # Mettre à jour le chemin de l'audio

        # Rediriger vers l'écran RecommendationDetailScreen
        self.manager.current = 'recommendation_detail'

class RecommendationDetailScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pygame.mixer.init()  # Initialiser le module audio de pygame
    music_bar_visible = BooleanProperty(False)
    audio_path = StringProperty("")

    def play_audio(self, audio_path):
        """
        Joue un fichier audio.
        """
        if not audio_path:
            show_popup("Erreur", "Aucun fichier audio disponible pour ce site.")
            return

        self.music_bar_visible = True
        self.audio_file = audio_path
        pygame.mixer.music.load(audio_path)  # Charger le fichier audio
        pygame.mixer.music.play()  # Jouer l'audio
        
        # Masquer la barre à la fin de la lecture
        # Vérifier régulièrement si la musique est terminée
        Clock.schedule_interval(self._check_music_end, 0.5)
    
    def _check_music_end(self, dt):
        if not pygame.mixer.music.get_busy():
            self.music_bar_visible = False
            Clock.unschedule(self._check_music_end)

    def pause_audio(self):
        """
        Met en pause la lecture audio.
        """
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()

    def resume_audio(self):
        """
        Reprend la lecture audio.
        """
        pygame.mixer.music.unpause()

    def stop_audio(self):
        """
        Arrête la lecture audio.
        """
        self.music_bar_visible = False
        pygame.mixer.music.stop()
        
class RecognitionScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cap = None
        self.count_image = 0  # Compteur pour les images capturées
        
    def on_enter(self):
        """
        Lorsqu'on entre dans l'écran, on ouvre la caméra et on démarre la preview.
        """
        self.start_camera()
        
    def start_camera(self):
        """ Ouvre la caméra et démarre la mise à jour du flux vidéo en continu """
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.show_popup("Erreur", "Impossible d'accéder à la caméra.")
            return
        # Demande à la méthode update_preview d'être appelée 30 fois par seconde
        Clock.schedule_interval(self.update_preview, 1.0 / 30.0)
        
    def update_preview(self, dt):
        """
        Capture un frame de la caméra et l'affiche dans le widget Image.
        """
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Convertir BGR -> RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Retourner l'image verticalement pour une correspondance correcte
                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(
                    size=(frame.shape[1], frame.shape[0]),
                    colorfmt="rgb"
                )
                texture.blit_buffer(buf, colorfmt="rgb", bufferfmt="ubyte")
                self.ids.camera_preview.texture = texture
            else:
                self.show_popup("Erreur", "Impossible de lire le flux vidéo.")
    
    def capture_image(self):
        """
        Capture l'image en cours, arrête la caméra et affiche l'image capturée.
        """
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                image_path = "pictures/captured_image/captured_image_" + str(self.count_image) + ".jpg"
                self.count_image += 1  # Incrémenter le compteur pour les prochaines captures
                cv2.imwrite(image_path, frame)
                # Arrêter la mise à jour de la preview et fermer la caméra
                self.close_camera()
                # Mettre à jour le widget d'aperçu avec la photo capturée
                self.ids.camera_preview.source = image_path
                self.ids.camera_preview.reload()
            else:
                self.show_popup("Erreur", "Impossible de capturer l'image.")

    def close_camera(self):
        """
        Arrête le flux de la caméra et désactive la mise à jour du preview.
        """
        Clock.unschedule(self.update_preview)
        if self.cap:
            self.cap.release()
            self.cap = None
    
    def reload_camera(self):
        """
        Recharge la caméra pour mettre à jour l'aperçu.
        """
        self.on_enter()
            
    def on_leave(self):
        """
        En quittant l'écran, il est important de fermer la caméra.
        """
        self.close_camera()
    
    def open_file_chooser(self):
        """
        Ouvre un gestionnaire de fichiers pour sélectionner une image.
        """
        print("Ouverture du gestionnaire de fichiers...")

        try:
            # Créer un FileChooser
            filechooser = FileChooserIconView(filters=["*.png", "*.jpg", "*.jpeg"])
            filechooser.multiselect = False  # Désactiver la sélection multiple
            
            # Créer une boîte verticale pour le contenu du popup
            popup_content = BoxLayout(orientation='vertical', spacing=10, padding=10)
            popup_content.add_widget(filechooser)
            
            buttons_layout = BoxLayout(orientation='horizontal', spacing=10, padding=10)
            # Bouton pour valider la sélection
            select_btn = Button(text="Sélectionner", size_hint_y=None, height=40)
            cancel_btn = Button(text="Annuler", size_hint_y=None, height=40)
            buttons_layout.add_widget(select_btn)
            buttons_layout.add_widget(cancel_btn)
            popup_content.add_widget(buttons_layout)
            
            popup = Popup(
                title="Sélectionnez une image",
                content=popup_content,
                size_hint=(0.9, 0.9),
            )

            # Lier l'action du bouton au traitement de la sélection
            cancel_btn.bind(on_release=lambda btn: popup.dismiss())
            select_btn.bind(on_release=lambda btn: self.on_file_selected(filechooser.selection, popup))
            
            # Fermer la caméra si elle est ouverte
            self.close_camera()
            
            # Ouvrir le popup
            popup.open()
        except Exception as e:
            print(f"Erreur lors de l'ouverture du gestionnaire de fichiers : {e}")
            show_popup("Erreur", "Impossible d'ouvrir le gestionnaire de fichiers.")
            
    def on_file_selected(self, selection, popup):
        """
        Gère le fichier sélectionné par l'utilisateur.
        """
        if selection:
            # Fermer la camera si elle est ouverte
            self.close_camera()
            
            # Prendre le premier fichier sélectionné
            file_path = selection[0]
            print(f"Fichier sélectionné : {file_path}")
            self.ids.camera_preview.source = file_path
            self.ids.camera_preview.reload()
            popup.dismiss()
        else:
            show_popup("Erreur", "Aucun fichier sélectionné.")

    def recognize_image(self):
        """
        Lance la reconnaissance d'image sur l'image capturée ou sélectionnée.
        """
        image = self.ids.camera_preview.source
        if not image:
            show_popup("Erreur", "Aucune image à reconnaître. Veuillez prendre une photo ou en sélectionner une.")
            return
        print(f"Lancement de la reconnaissance d'image sur : {image}")
        # Rediriger vers l'écran de résultats de reconnaissance
        detail_screen = self.manager.get_screen('recognition_result') 
        detail_screen.ids.captured_image.source = image
        self.manager.current = 'recognition_result'
        
class RecognitionResultScreen(Screen):
    def on_enter(self):
        """
        Méthode appelée lorsque l'utilisateur entre dans l'écran de résultats de reconnaissance.
        """
        image = self.ids.captured_image.source
        # Appeler la fonction de reconnaissance d'image
        results = predict_monument(image)
        # Afficher les résultats de la reconnaissance
        self.ids.result_label_text.text = results
        # Vous pouvez ajouter d'autres éléments d'interface utilisateur pour afficher les résultats
class RihlaApp(App):
    def build(self):
        root = RootWidget()
        # Binder la fonction de visibilité à tout changement de l'écran courant
        root.ids.screen_manager.bind(current=lambda instance, value: root.update_nav_bar_visibility())
        # Appel initial après la construction du widget (timing avec Clock)
        Clock.schedule_once(lambda dt: root.update_nav_bar_visibility(), 0)
        
        # Le logo
        self.icon = "../Logo.png"
        return root
    
    def logout(self, message=None):
        """Déconnecte l'utilisateur et redirige vers l'écran de connexion."""
        self.root.ids.screen_manager.current = 'home'
        if message is not None:
            self.root.ids.screen_manager.get_screen('home').ids.message.text = message
        else:
            self.root.ids.screen_manager.get_screen('home').ids.message.text = "Vous êtes déconnecté."
        self.root.user = None
        
    def delete_account(self, password, popup):
        """Supprime le compte de l'utilisateur et redirige vers l'écran de connexion."""
        
        user, error = AuthService.login(self.user.email, password)
        if error:
            show_popup("Erreur", "Mot de passe incorrect. veillez réessayer.")
            return
        
        popup.dismiss()
        
        success, error = AuthService.delete_account(user.id)
        if error:
            show_popup("Erreur", f"Erreur lors de la suppression du compte : {error}")
            return
        
        self.logout("Votre compte a été supprimé avec succès.")

if __name__ == '__main__':
    RihlaApp().run()