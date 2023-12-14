import sys
import subprocess
import socket

#Controlamos el numero de argumentos que vamos a pasar al script
num_argumentos = len(sys.argv)
if num_argumentos == 6:
	nombre_equipo = sys.argv[1]
	domain = sys.argv[2]
	dns = sys.argv[3]
	admin_user = sys.argv[4]
	admin_pass = sys.argv[5]
else:
	print ('Error al pasar el numero de argumentos')
	exit()

#Instalamos todos los paquetes necesarios

def instalar_paquetes():
	actualizacion = "sudo apt update --quiet > archivo.log"
	subprocess.run(actualizacion, shell=True)
	paquetes = ["samba", "krb5-config", "winbind", "realmd", "libnss-winbind", "libpam-winbind"]
	for paquete in paquetes:
		comando_instalacion = f"sudo DEBIAN_FRONTEND=noninteractive apt install -y {paquete} --quiet >> archivo.log"
		resultado = subprocess.run(comando_instalacion, shell=True)
		if resultado.returncode == 0:
    			print(f"El paquete {paquete} ha sido instalado con éxito.")
		else:
    			print(f"Hubo un problema al instalar el paquete {paquete}.")

def cambiar_nombre(nombre_dominio, nombre_host):
	encontrar_ip = "ip a | grep inet | tail -2 | head -1 | cut -d' ' -f6"
	resultado_ip = subprocess.run(encontrar_ip, shell=True, capture_output=True, text=True, check=True)
	ip = resultado_ip.stdout.strip()
	encontrar_nombre_interfaz = "ip a | grep UP | grep -v LOOPBACK | cut -d' ' -f2 | cut -d':' -f1"
	resultado_nombre_interfaz = subprocess.run(encontrar_nombre_interfaz, shell=True, capture_output=True, text=True, check=True)
	interfaz = resultado_nombre_interfaz.stdout.strip()
	encontrar_gateway = "ip route | grep default | cut -d' ' -f3"
	resultado_encontrar_gateway = subprocess.run(encontrar_gateway, shell=True, capture_output=True, text=True, check=True)
	gateway = resultado_encontrar_gateway.stdout.strip()

	ruta_archivo_interfaces = "/etc/network/interfaces"
	with open(ruta_archivo_interfaces, 'r') as archivo:
		lineas = archivo.readlines()

        # Modificar las líneas relevantes para la interfaz
	for i in range(len(lineas)):
		if lineas[i].startswith(f"iface {interfaz}"):
                # Reemplazar la configuración DHCP por configuración estática
			lineas[i] = f"""iface {interfaz} inet static \n	address {ip} \n	gateway {gateway}"""

        # Escribir el contenido modificado de vuelta al archivo
	with open(ruta_archivo_interfaces, 'w') as archivo:
		archivo.writelines(lineas)

	def reiniciar_networking():
			comando_reinicio = "sudo systemctl restart networking"
			subprocess.run(comando_reinicio, shell=True, check=True)

	reiniciar_networking()

	#Vamos a modificar el fichero de hosts añadiendo la ip y el nombre de hosts

	encontrar_ip = "ip a | grep inet | tail -2 | head -1 | cut -d' ' -f6 | cut -d'/' -f1"
	resultado_ip = subprocess.run(encontrar_ip, shell=True, capture_output=True, text=True, check=True)
	ip = resultado_ip.stdout.strip()
	ruta_archivo_interfaces = "/etc/hosts"
	nombre_completo = nombre_host +'.'+nombre_dominio

	with open(ruta_archivo_interfaces, 'r') as archivo:
		lineas = archivo.readlines()

	for i in range(len(lineas)):
		if lineas[i].startswith(f"127.0.0.1	localhost"):
			lineas[i + 1] = f"{ip}	{nombre_completo + ' ' + nombre_host}\n"

        # Escribir el contenido modificado de vuelta al archivo
	with open(ruta_archivo_interfaces, 'w') as archivo:
		archivo.writelines(lineas)


def cambiar_dns(nuevo_dns):
	ruta_resolv_conf = "/etc/resolv.conf"
	linea_dns = "nameserver " + nuevo_dns
	file = open(ruta_resolv_conf, "w")
	file.write(linea_dns)

def verificar_dominio(dominio, servidor_dns):
	comando_dig = ["dig", dominio, "@{}".format(servidor_dns), "+short"]
	resultado = subprocess.run(comando_dig, capture_output=True, text=True, check=True)
	if resultado.stdout.strip():
		print(f"El dominio {dominio} no existe.")
	else:
		print(f"El dominio {dominio} si existe.")

def modificar_samba(dominio, host):
	dominio_mayus = dominio.upper()
	dominio_mayus_primera = dominio_mayus.split(".")
	print (dominio_mayus)
	print (dominio_mayus_primera[0])
	configuracion_samba = f"""
	[global]
	server role = MEMBER SERVER
	workgroup = {dominio_mayus_primera[0]}
	security = ads
	realm = {dominio_mayus}
	idmap config * : backend = tdb
	idmap config * : range = 10000-20000
	idmap config {dominio_mayus_primera[0]} = rid
	idmap config {dominio_mayus_primera[0]} = 30000-40000
	winbind refresh tickets = yes
	winbind enum users = yes
	winbind enum groups = yes
	winbind nested groups = yes
	winbind expand groups = 2
	winbind use default domain = yes
	winbind nss info = template
	template shell = /bin/bash
	template homedir = /home/%U
	netbios name = {host}

	"""
	ruta_archivo = "/home/usuario/smb.conf"
	with open(ruta_archivo, 'w') as archivo:
		archivo.write(configuracion_samba)

	#instalar paquetes
instalar_paquetes()

	#modificar el fichero de /etc/resolv.conf
cambiar_dns(dns)

#verificar_dominio(domain, dns)
	#Cambiar ip a ip estatica y añadir el nombre del equipo al fichero hosts
cambiar_nombre(domain, nombre_equipo)

modificar_samba(domain, nombre_equipo)