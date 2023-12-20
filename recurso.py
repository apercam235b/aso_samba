import subprocess
import os

def recurso(recurso):
    ruta_compartida = "/home/" + recurso
    archivo = f"/etc/samba/smb.conf"
    with open(archivo, 'r') as f:
        contenido = f.read()

    if not f"[{recurso}]" in contenido:
        print("Creando recurso compartido...")
        configuracion_samba = f"""[{recurso}]
    comment = "Recurso compartido samba del usuario: {recurso}"
    path = {ruta_compartida}
    create mask = 0770
    browseable = yes
    writeable = yes
    acl_xattr:ignore system acl = Yes
    acl allow execute always = Yes
    acl group control = Yes
    inherit acls = Yes
    inherit owner = windows and unix
    inherit permissions = Yes
    valid users = {recurso}

        """
        ruta_archivo = "/etc/samba/smb.conf"
        with open(ruta_archivo, 'a') as archivo:
                archivo.write(configuracion_samba)
    else:
         print ("el recurso ya existe")

usuario = os.getenv('SUDO_USER') or os.getenv('USER')
print (f'el usuario es: {usuario}')

recurso(usuario)