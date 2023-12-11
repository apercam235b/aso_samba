import os
import sys
import pwd
import grp

directorio = sys.argv[1]

def encontrar_ruta (ruta_enc):
        resultado = os.path.exists(ruta_enc)
        if resultado == False:
                os.makedirs(ruta_enc)
        os.chmod(ruta_enc, 0o771)
        uid = pwd.getpwnam("root").pw_uid
        gid = grp.getgrnam("usuarios_del_dominio").gr_gid
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
        configuracion_samba = f"""
        [{recurso}]
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
        ruta_archivo = "/opt/recurso/smb.conf"
        with open(ruta_archivo, 'a') as archivo:
                archivo.write(configuracion_samba)

encontrar_ruta(directorio)
enlace_simbolico(directorio)
recurso(directorio)
