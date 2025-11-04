from database import db
from services import AuthService
from models import User

def print_menu():
    print("\n" + "="*50)
    print("1. S'inscrire")
    print("2. Se connecter")
    print("3. Modifier le profil")
    print("4. Changer le mot de passe")
    print("5. Réinitialiser le mot de passe")
    print("6. Quitter")
    print("="*50 + "\n")

def test_register():
    print("\n--- Inscription ---")
    email = input("Email: ")
    password = input("Mot de passe: ")
    first_name = input("Prénom (optionnel): ") or None
    last_name = input("Nom (optionnel): ") or None
    
    user, error = AuthService.register(email, password, first_name, last_name)
    if error:
        print(f"Erreur: {error}")
    else:
        print(f"Compte créé pour {user.full_name or user.email}")

def test_login():
    print("\n--- Connexion ---")
    email = input("Email: ")
    password = input("Mot de passe: ")
    
    user, error = AuthService.login(email, password)
    if error:
        print(f"Erreur: {error}")
    else:
        print(f"Connecté en tant que {user.full_name or user.email}")
        return user
    return None

def test_update_profile(user):
    print("\n--- Modification du profil ---")
    new_email = input(f"Nouvel email (actuel: {user.email}): ") or None
    new_first = input(f"Nouveau prénom (actuel: {user.first_name}): ") or None
    new_last = input(f"Nouveau nom (actuel: {user.last_name}): ") or None
    
    success, error = AuthService.update_profile(
        user.id,
        email=new_email,
        first_name=new_first,
        last_name=new_last
    )
    
    if error:
        print(f"Erreur: {error}")
    else:
        print("Profil mis à jour avec succès")

def test_change_password(user):
    print("\n--- Changement de mot de passe ---")
    current = input("Mot de passe actuel: ")
    new = input("Nouveau mot de passe: ")
    
    success, error = AuthService.change_password(user.id, current, new)
    if error:
        print(f"Erreur: {error}")
    else:
        print("Mot de passe changé avec succès")

def test_password_reset():
    print("\n--- Réinitialisation de mot de passe ---")
    email = input("Email: ")
    
    # Étape 1: Demande de réinitialisation
    token, error = AuthService.initiate_password_reset(email)
    if error:
        print(f"Erreur: {error}")
        return
    
    print(f"Token généré (simulé): {token}")
    
    # Étape 2: Saisie du nouveau mot de passe
    new_password = input("Nouveau mot de passe: ")
    
    success, error = AuthService.complete_password_reset(token, new_password)
    if error:
        print(f"Erreur: {error}")
    else:
        print("Mot de passe réinitialisé avec succès")

def main():
    current_user = None
    
    while True:
        print_menu()
        choice = input("Choix: ")
        
        try:
            if choice == "1":
                test_register()
            elif choice == "2":
                current_user = test_login()
            elif choice == "3":
                if current_user:
                    test_update_profile(current_user)
                else:
                    print("Veuillez vous connecter d'abord")
            elif choice == "4":
                if current_user:
                    test_change_password(current_user)
                else:
                    print("Veuillez vous connecter d'abord")
            elif choice == "5":
                test_password_reset()
            elif choice == "6":
                print("Au revoir!")
                break
            else:
                print("Choix invalide")
        except Exception as e:
            print(f"Une erreur est survenue: {str(e)}")
    
    db.close()

if __name__ == "__main__":
    main()