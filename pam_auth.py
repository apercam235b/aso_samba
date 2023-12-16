import pexpect

def configurar_pam():
    try:
        # Ejecutar pam-auth-update
        proceso = pexpect.spawn('sudo pam-auth-update')

        # Esperar a que aparezca la cadena 'Authentication methods provided by modules'
        proceso.expect('Authentication methods provided by modules')

        # Enviar 'TAB' para moverse al botón 'OK' y presionar 'Enter'
        proceso.send('\t\n')

        # Esperar a que aparezca la cadena 'Save changes'
        proceso.expect('Save changes')

        # Enviar 'TAB' para moverse al botón 'Yes' y presionar 'Enter'
        proceso.send('\t\n')

        # Esperar a que termine el proceso
        proceso.wait()

        print("Configuración de PAM actualizada exitosamente.")
    except Exception as e:
        print(f"Error al configurar PAM. Detalles: {e}")

# Llamada a la función para configurar PAM
configurar_pam()
