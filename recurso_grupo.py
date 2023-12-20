import os
import sys
import pwd
import grp
import subprocess

password = 'Dpto1!'
usuario = 'administrador'
host = '192.168.210.86'

def existe_grupo(nombre_grupo):
        comando_instalacion = f"sudo DEBIAN_FRONTEND=noninteractive apt install -y sshpass --quiet >> archivo_recurso.log 2>&1"
        subprocess.run(comando_instalacion, shell=True)
        try:
                grp.getgrnam(nombre_grupo)
                print ('el grupo si existe')
        except KeyError: 
                cmd_ssh = f'sshpass -p "{password}" ssh {usuario}@{host} "powershell -NoProfile -NonInteractive -Command "New-ADGroup -Name {nombre_grupo} -GroupScope Global""'
                subprocess.run(cmd_ssh, shell=True)
                print ('creando grupo...')
     
def encontrar_ruta (ruta_enc, grupo):
        resultado = os.path.exists(ruta_enc)
        if resultado == False:
                os.makedirs(ruta_enc)
        os.chmod(ruta_enc, 0o771)
        uid = pwd.getpwnam("root").pw_uid
        gid = grp.getgrnam(grupo).gr_gid
        os.chown(ruta_enc, uid, gid)

def enlace_simbolico(ruta_enl):
        ruta_final = "/recurso/" + ruta_enl
        if not os.path.exists(ruta_final):
                try:
                        ruta_actual = os.getcwd()
                        ruta_original = ruta_actual + "/" + ruta_enl
                        os.symlink(ruta_original, ruta_final)
                except OSError as e:
                        print(f"Error al crear el enlace simbólico: {e}")

def recurso(recurso):
        ruta_compartida = "/recurso/" + recurso
        configuracion_samba = f"""[{recurso}]
        comment = "Recurso compartido samba {recurso}"
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
        valid users = @usuariosdominio
        """
        print(configuracion_samba)
        ruta_archivo = "/etc/samba/smb.conf"
        with open(ruta_archivo, 'a') as archivo:
                archivo.write(configuracion_samba)

num_argumentos = len(sys.argv)
if num_argumentos == 3:
	nombre_recurso = sys.argv[1]
	nombre_grupo = sys.argv[2]
else:
	print ('Error al pasar el numero de argumentos, el orden es nombre dominio dns admin_user admin_pass')
	exit()

existe_grupo(nombre_grupo)
encontrar_ruta(nombre_recurso, nombre_grupo)
enlace_simbolico(nombre_recurso)
recurso(nombre_recurso)
