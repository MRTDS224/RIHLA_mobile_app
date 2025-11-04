import re

class Users:
    count = 0
    id : int = None

    def __init__(self, last_name: str, first_name: str, email: str, password: str, preferences: list = None):
        self.last_name = last_name
        self.first_name = first_name
        self.email = email
        self.password = password
        self.preferences = preferences if preferences is not None else []
        Users.count += 1

    # Propriétés pour last_name
    @property
    def last_name(self):
        return self.__last_name
    @last_name.setter
    def last_name(self, value):
        self.__last_name = value

    # Propriétés pour first_name
    @property
    def first_name(self):
        return self.__first_name
    @first_name.setter
    def first_name(self, value):
        self.__first_name = value

    # Propriétés pour email avec validation
    @property
    def email(self):
        return self.__email
    @email.setter
    def email(self, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError("Email invalide")
        self.__email = value

    # Propriétés pour password avec validation
    @property
    def password(self):
        return self.__password
    @password.setter
    def password(self, value):
        if len(value) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        self.__password = value
    
    @property
    def preferences(self):
        return self.__preferences
    @preferences.setter
    def preferences(self, value):
        if not isinstance(value, list):
            raise ValueError("Les préférences doivent être une liste")
        self.__preferences = value

    # Méthode pour afficher les informations utilisateur
    def display_user_info(self):
        return f"Nom: {self.first_name} {self.last_name}\nEmail: {self.email}\nMot de passe: {self.password}\nPréférences: {', '.join(self.preferences)}"

    # Méthode pour supprimer un utilisateur
    def delete_user(self):
        Users.count -= 1
        print(f"L'utilisateur {self.first_name} {self.last_name} a été supprimé.")

    # Méthode de classe pour obtenir le nombre d'utilisateurs
    @classmethod
    def get_user_count(cls):
        return cls.count

    # Méthode __str__ pour une représentation lisible
    def __str__(self):
        return f"Utilisateur: {self.first_name} {self.last_name}, Email: {self.email}, Préférences: {self.preferences}"


print(Users.get_user_count())