import sys
import subprocess
import socket

#Instalamos todos los paquetes necesarios

def instalar_paquetes():
	actualizacion = "sudo apt update --quiet > archivo.log > archivo.log 2>&1"
	subprocess.run(actualizacion, shell=True)
	paquetes = ["samba", "smbclient", "krb5-config", "krb5-kdc", "krb5-user", "winbind", "realmd", "libnss-winbind", "libpam-winbind"]
	for paquete in paquetes:
		comando_instalacion = f"sudo DEBIAN_FRONTEND=noninteractive apt install -y {paquete} --quiet >> archivo.log 2>&1"
		resultado = subprocess.run(comando_instalacion, shell=True)
		if resultado.returncode == 0:
				print(f"El paquete {paquete} ha sido instalado con éxito.")
		else:
				print(f"Hubo un problema al instalar el paquete {paquete}.")


def cambiar_nombre(nombre_dominio, nombre_host):
	encontrar_ip = "ip a | grep inet | tail -2 | head -1 | cut -d' ' -f6"
	resultado_ip = subprocess.run(encontrar_ip, shell=True, capture_output=True, text=True, check=True)
	ip = resultado_ip.stdout.strip()
	print (ip)
	ip_divida = ip.split("/")
	print (ip_divida[0])
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
			lineas[i] = f"""iface {interfaz} inet static \n	address {ip} \n	gateway {gateway} \n	dns-nameservers {dns} \n"""

			# Escribir el contenido modificado de vuelta al archivo
	with open(ruta_archivo_interfaces, 'w') as archivo:
		archivo.writelines(lineas)

	def reiniciar_networking():
			comando_reinicio = "sudo systemctl restart networking"
			subprocess.run(comando_reinicio, shell=True, check=True)

	reiniciar_networking()
	#Cambiamos el nombre del equipo con hostnamectl

	#comando = ["sudo", "hostnamectl", "set-hostname", nombre_equipo]
	#subprocess.run(comando, check=True)

	#Vamos a modificar el fichero de hosts añadiendo la ip y el nombre de hosts

	ruta_archivo_interfaces = "/etc/hosts"
	nombre_completo = nombre_host +'.'+nombre_dominio
	configuracion_hosts = f"""127.0.0.1	localhost
{ip_divida[0]}	{nombre_completo + ' ' + nombre_host}
	"""
	
	with open(ruta_archivo_interfaces, 'w') as archivo:
		archivo.write(configuracion_hosts)

def cambiar_dns(nuevo_dns):
	ruta_resolv_conf = "/etc/resolv.conf"
	linea_dns = "nameserver " + nuevo_dns + "\n"
	print (linea_dns)
	with open(ruta_resolv_conf, 'w') as archivo:
		archivo.write(linea_dns)
	with open(ruta_resolv_conf, 'r') as resolv:
		contenido = resolv.read()
	print (contenido)

def modificar_samba(dominio, host):
	dominio_mayus = dominio.upper()
	dominio_mayus_primera = dominio_mayus.split(".") 
	configuracion_samba = f"""[global]
	server role = MEMBER SERVER
	netbios name = {host.upper()}
	workgroup = {dominio_mayus_primera[0]}
	security = ads
	realm = {dominio_mayus}
	idmap config * : backend = tdb
	idmap config * : range = 10000-20000
	idmap config {dominio_mayus_primera[0]} : backend = rid
	idmap config {dominio_mayus_primera[0]} : range = 30000-40000
	winbind refresh tickets = yes
	winbind enum users = yes
	winbind enum groups = yes
	winbind nested groups = yes
	winbind expand groups = 2
	winbind use default domain = yes
	winbind nss info = template
	template shell = /bin/bash
	template homedir = /home/%U
	
	"""
	ruta_archivo = "/etc/samba/smb.conf"
	with open(ruta_archivo, 'w') as archivo:
		archivo.write(configuracion_samba)

def modificar_kerberos(dominio):
	dominio_minus = dominio
	dominio_mayus = dominio.upper()
	n_equipo_dominio = f"dig SRV _ldap._tcp.{dominio} | grep .{dominio} | tail -1 | cut -d'.' -f1-3"
	resultado_n_equipo_dominio = subprocess.run(n_equipo_dominio, shell=True, capture_output=True, text=True, check=True)
	nombre_equipo_dominio = resultado_n_equipo_dominio.stdout.strip()
	configuracion_samba = f"""[libdefaults]
	default_realm = {dominio_mayus}
	dns_lookup_realm = false
	dns_lookup_kdc = true
# The following krb5.conf variables are only for MIT Kerberos.
	forwardable = true

[realms]
	{dominio_mayus} = {{
			kdc = {nombre_equipo_dominio}
			admin_server = {nombre_equipo_dominio}
		}}
[domain_realm]
		.{dominio_minus} = {dominio_mayus}
		{dominio_minus} = {dominio_mayus}

	"""
	ruta_archivo = "/etc/krb5.conf"
	with open(ruta_archivo, 'w') as archivo:
		archivo.write(configuracion_samba)

#Controlamos el numero de argumentos que vamos a pasar al script
num_argumentos = len(sys.argv)
if num_argumentos == 6:
	nombre_equipo = sys.argv[1]
	domain = sys.argv[2]
	dns = sys.argv[3]
	admin_user = sys.argv[4]
	admin_pass = sys.argv[5]
else:
	print ('Error al pasar el numero de argumentos, el orden es nombre dominio dns admin_user admin_pass')
	exit()


	#instalar paquetes
instalar_paquetes()
	#Cambiar ip a ip estatica y añadir el nombre del equipo al fichero hosts
cambiar_nombre(domain, nombre_equipo)
	#modificar el fichero de /etc/resolv.conf
cambiar_dns(dns)

modificar_samba(domain, nombre_equipo)

modificar_kerberos(domain)