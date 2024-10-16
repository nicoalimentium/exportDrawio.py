import xml.etree.ElementTree as ET
#ruta donde se aloja el fichero
archivo = ''
tree = ET.parse(archivo)
root = tree.getroot()
def obtener_datos(root):
    conexiones = []
    for elemento in root.iter('mxCell'):
        if elemento.attrib.get('edge'):
            source = elemento.attrib.get('source')
            target = elemento.attrib.get('target')
            conexiones.append([source, target])
    
    nodos_a_expandir = []
    tipos_validos=['rhombus', 'shape=process']    
    for cell in root.findall('.//mxCell[@vertex="1"]'):
        estilo = cell.attrib.get('style', '')
        
        # Revisar si el estilo contiene alguno de los tipos válidos
        if any(tipo in estilo for tipo in tipos_validos):
            nodo = cell.attrib['id']  # Obtiene el valor del nodo (texto dentro del nodo)
            nodos_a_expandir.append(nodo)
    nodos_por_id = {}
    for elemento in root.iter('mxCell'):
        if elemento.attrib.get('value'):
            estilo = elemento.attrib.get('style')
            nodo_data = {
                'texto': elemento.attrib['value'],
                'estilo': estilo
            }
            nodos_por_id[elemento.attrib['id']] = nodo_data
    return conexiones, nodos_a_expandir, nodos_por_id

def reemplazar_ids_por_nombres(secuencias, diccionario_nodos):
    secuencias_con_nombres = []
    texto_final = ''
    for secuencia in secuencias:
        nueva_secuencia = []
        texto_final = ''
        texto_notif = ';'
        for nodo_id in secuencia:
            if nodo_id is None:
                nueva_secuencia.append('NULL;')
            else:
                nodo_buscado = diccionario_nodos[nodo_id]
                if 'rhombus' in nodo_buscado['estilo']:
                    texto_final += "P: " + nodo_buscado['texto'] + ';'
                elif 'shape=process' in nodo_buscado['estilo']:
                    texto_notif = 'SEND_MAIL_TO;'
                else:
                    nueva_secuencia.append(nodo_buscado['texto'] + ";")
        nueva_secuencia.append('APROBADO;' + texto_notif + texto_final)
        secuencias_con_nombres.append(nueva_secuencia)
    return secuencias_con_nombres


# Función para construir el grafo a partir de las conexiones
def construir_grafo(conexiones):
    grafo = {}
    for conexion in conexiones:
        if conexion[0] not in grafo:
            grafo[conexion[0]] = []
        grafo[conexion[0]].append(conexion[1])
    return grafo

# Función para encontrar las secuencias válidas
def encontrar_secuencias(grafo, nodos_expandir):
    secuencias_finales = []
    nodos_no_expandibles = [nodo for nodo in grafo.keys() if nodo not in nodos_expandir]
    
    for nodo in nodos_no_expandibles:
        pila = [(nodo, [nodo], 1)]  # La pila almacenará tuplas (nodo_actual, secuencia_actual, cuenta_no_expandibles)
        visitados = set()  # Para evitar ciclos
        
        while pila:
            nodo_actual, secuencia_actual, cuenta_no_expandibles = pila.pop()
            
            # Marcar el nodo actual como visitado para evitar ciclos
            if (nodo_actual, tuple(secuencia_actual)) in visitados:
                continue
            visitados.add((nodo_actual, tuple(secuencia_actual)))
            
            # Agregar la secuencia si hemos llegado a dos nodos no expandibles
            if cuenta_no_expandibles == 2:
                secuencias_finales.append(secuencia_actual.copy())
                continue
            
            # Continuar explorando las conexiones
            if nodo_actual in grafo:
                for vecino in grafo[nodo_actual]:
                    if vecino not in nodos_expandir:
                        # Solo seguir si no excedemos 2 nodos no expandibles
                        if cuenta_no_expandibles < 2:
                            nueva_secuencia = secuencia_actual + [vecino]
                            pila.append((vecino, nueva_secuencia, cuenta_no_expandibles + 1))
                    else:
                        # Agregar nodos expandibles sin aumentar el conteo
                        nueva_secuencia = secuencia_actual + [vecino]
                        pila.append((vecino, nueva_secuencia, cuenta_no_expandibles))
    
    return secuencias_finales

# Función principal que coordina la búsqueda de secuencias
def generar_secuencias(conexiones, nodos_expandir):
    grafo = construir_grafo(conexiones)
    return encontrar_secuencias(grafo, nodos_expandir)

# Ejecutamos el programa
conexiones, nodos_expandir, nodos_por_id = obtener_datos(root)

secuencias_validas = generar_secuencias(conexiones, nodos_expandir)
secuencias_con_nombres = reemplazar_ids_por_nombres(secuencias_validas, nodos_por_id)

# Mostrar las secuencias válidas con los nombres en los nodos
for secuencia in secuencias_con_nombres:
    print(f"{secuencia}")
# Mostrar las secuencias válidas
# for secuencia in secuencias_validas:
#     print(secuencia)
# Mostrar los nodos a expandir (nodos de paso)
# for nodoExp in nodos_expandir:
#     print(f"{nodoExp}")
# Mostrar info de los nodos
# for nodo in nodos_por_id:
#     print(f"{nodo}")