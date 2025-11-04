import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import random

def send_email_with_attachment(recipient_email):
    sender_email = "tahirou068@gmail.com"
    load_dotenv()
    sender_password = os.getenv("APP_PASSWORD")  # Utilisez une variable d'environnement pour le mot de passe

    subject = "Code de réinitialisation de mot de passe"
    code = str(random.randint(10000000, 99999999))
    message = (
        "Bonjour,\n\n"
        f"Voici le code de réinitialisation de votre mot de passe : {code}\n\n"
        "Cordialement,\n"
        "Votre équipe de support."
    )

    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Création de l'objet de message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        # Connexion au serveur SMTP
        print("Connexion au serveur SMTP...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        print("Connexion réussie.")

        # Envoi de l'email
        print("Envoi de l'email...")
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email envoyé avec succès !")
        return code
    except smtplib.SMTPAuthenticationError:
        print("Erreur d'authentification : Vérifiez votre adresse email et mot de passe.")
    except smtplib.SMTPConnectError:
        print("Erreur de connexion : Vérifiez votre connexion Internet.")
    except smtplib.SMTPException as e:
        print(f"Erreur SMTP : {e}")
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")

# Appel de la fonction
# send_email_with_attachment("mrtdsow@outlook.com")

# import smtplib

# sender_email = "tahirou068@gmail.com"
# load_dotenv()
# sender_password = os.getenv("APP_PASSWORD")
# recipient_email = "mrtdsow@outlook.com"

# try:
#     server = smtplib.SMTP("smtp.gmail.com", 587)
#     server.starttls()
#     server.login(sender_email, sender_password)
#     print("Connexion OK")
#     server.sendmail(sender_email, recipient_email, "Subject: Test\n\nCeci est un test avec Gmail.")
#     print("Mail envoyé")
#     server.quit()
# except Exception as e:
#     print("Erreur:", e)

# from O365 import Account

# credentials = ('CLIENT_ID', 'CLIENT_SECRET')
# account = Account(credentials)
# if not account.is_authenticated:
#     # Ouvre un navigateur pour autoriser l'app la première fois
#     account.authenticate(scopes=['basic', 'message_all'])

# m = account.new_message()
# m.to.add('tahirou068@gmail.com')
# m.subject = 'Test'
# m.body = 'Ceci est un test.'
# m.send()