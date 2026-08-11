import cv2
import cleanBotFonctions
import time
from aliot.aliot_obj import AliotObj

# Attente pour bien établir la communication avec le capteur
time.sleep(5)


# Création de l'objet à partir du fichier de configuration
rasp_cleanbot = AliotObj("rasp-cleanbot")

# Initialiser les variables
distance = None
camera_active = False
automatic_mode = False

# Initialize the camera and QR Code detector
cap = cleanBotFonctions.initialize_camera()
detector = cv2.QRCodeDetector()

# Check if the camera was initialized
if cap is None:
    exit()

# Fonction exécutée lorsqu'un bouton est cliqué
def OnClickButton(data):
    global camera_active, automatic_mode
    if isinstance(data, bool):  # Gestion du ventilateur
        if data:
            rasp_cleanbot.update_doc({"/doc/ventilateur": True})
            cleanBotFonctions.send_command("V")
        else:
            rasp_cleanbot.update_doc({"/doc/ventilateur": False})
            cleanBotFonctions.send_command("v")
    elif data == 'C':  # Gestion de la caméra
        camera_active = not camera_active

    elif data == 'M':  # Gestion du mode automatique
        automatic_mode = not automatic_mode
        cleanBotFonctions.send_command("S")
        if automatic_mode:
            rasp_cleanbot.update_doc({"/doc/ventilateur": True})
            cleanBotFonctions.send_command("V")
        else:
            rasp_cleanbot.update_doc({"/doc/ventilateur": False})
            cleanBotFonctions.send_command("v")
        cleanBotFonctions.send_command(data)
    else:  # Commande générique
        cleanBotFonctions.send_command(data)

def start():
    global camera_active, automatic_mode
    while True:
        # Si la caméra est activée
        if camera_active:
            cleanBotFonctions.display_camera_feed(cap, detector)

        # Si la caméra est désactivée
        if not camera_active:
            cv2.destroyAllWindows()

        try:
            # Récupérer et envoyer la distance à la base de données
            distance = cleanBotFonctions.get_distance()
            print(distance)
            rasp_cleanbot.update_doc({"/doc/distance": distance})
            time.sleep(0.5)

            # Contrôle automatique basé sur la distance
            if automatic_mode:
                if distance > 15:
                    cleanBotFonctions.send_command('A')  
                elif distance <= 10 and distance > 0:
                    cleanBotFonctions.send_command('H') 
            
            rasp_cleanbot.on_action_recv(action_id="send_command", callback=OnClickButton)
        except KeyboardInterrupt:
            if camera_active:
                cap.release() 
                cv2.destroyAllWindows()
            break

# Appel de la fonction start après la connexion au serveur
rasp_cleanbot.on_start(callback=start)
rasp_cleanbot.run()
