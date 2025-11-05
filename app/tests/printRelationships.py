import networkx as nx
import matplotlib.pyplot as plt

# Simulación de la carga de un archivo con nodos
nodos = [
{"id": 1600, "parentId": "1598"},
{"id": 1896, "parentId": "1598"},
{"id": 1599, "parentId": "1598"},
{"id": 1601, "parentId": "1598"},
{"id": 1460, "parentId": "1342"},
{"id": 1459, "parentId": "1342"},
{"id": 4345, "parentId": "4331"},
{"id": 4344, "parentId": "4331"},
{"id": 4332, "parentId": "4331"},
{"id": 4346, "parentId": "4331"},
{"id": 4333, "parentId": "4331"},
{"id": 2457, "parentId": "1390"},
{"id": 3979, "parentId": "1390"},
{"id": 2458, "parentId": "1390"},
{"id": 1351, "parentId": "1311"},
{"id": 1349, "parentId": "1311"},
{"id": 1340, "parentId": "1311"},
{"id": 1863, "parentId": "1311"},
{"id": 1862, "parentId": "1311"},
{"id": 4407, "parentId": "4403"},
{"id": 4406, "parentId": "4403"},
{"id": 4405, "parentId": "4403"},
{"id": 4404, "parentId": "4403"},
{"id": 6278, "parentId": "6277"},
{"id": 6283, "parentId": "6277"},
{"id": 6280, "parentId": "6277"},
{"id": 6279, "parentId": "6277"},
{"id": 6513, "parentId": "6277"},
{"id": 4425, "parentId": "4414"},
{"id": 4431, "parentId": "4414"},
{"id": 4426, "parentId": "4414"},
{"id": 4423, "parentId": "4414"},
{"id": 4417, "parentId": "4414"},
{"id": 4433, "parentId": "4414"},
{"id": 4429, "parentId": "4414"},
{"id": 4415, "parentId": "4414"},
{"id": 4430, "parentId": "4414"},
{"id": 4436, "parentId": "4414"},
{"id": 4424, "parentId": "4414"},
{"id": 4427, "parentId": "4414"},
{"id": 4428, "parentId": "4414"},
{"id": 4416, "parentId": "4414"},
{"id": 4418, "parentId": "4414"},
{"id": 4435, "parentId": "4414"},
{"id": 4422, "parentId": "4414"},
{"id": 4432, "parentId": "4414"},
{"id": 4421, "parentId": "4414"},
{"id": 4420, "parentId": "4414"},
{"id": 4419, "parentId": "4414"},
{"id": 4434, "parentId": "4414"},
{"id": 1093, "parentId": "993"},
{"id": 1002, "parentId": "993"},
{"id": 1091, "parentId": "995"},
{"id": 1371, "parentId": "995"},
{"id": 1356, "parentId": "995"},
{"id": 1004, "parentId": "995"},
{"id": 1278, "parentId": "995"},
{"id": 1200, "parentId": "994"},
{"id": 1099, "parentId": "994"},
{"id": 1341, "parentId": "994"},
{"id": 1101, "parentId": "994"},
{"id": 1199, "parentId": "994"},
{"id": 1202, "parentId": "994"},
{"id": 928, "parentId": "994"},
{"id": 1207, "parentId": "994"},
{"id": 1102, "parentId": "994"},
{"id": 1100, "parentId": "994"},
{"id": 5931, "parentId": "5930"},
{"id": 1557, "parentId": "1501"},
{"id": 1558, "parentId": "1501"},
{"id": 1738, "parentId": "1501"},
{"id": 1800, "parentId": "1798"},
{"id": 4398, "parentId": "4374"},
{"id": 4389, "parentId": "4374"},
{"id": 4462, "parentId": "4374"},
{"id": 4461, "parentId": "4374"},
{"id": 4379, "parentId": "4374"},
{"id": 4387, "parentId": "4374"},
{"id": 4392, "parentId": "4374"},
{"id": 4395, "parentId": "4374"},
{"id": 4463, "parentId": "4374"},
{"id": 1974, "parentId": "1792"},
{"id": 1931, "parentId": "1792"},
{"id": 1849, "parentId": "1792"},
{"id": 1850, "parentId": "1792"},
{"id": 1793, "parentId": "1792"},
{"id": 1415, "parentId": "6856"},
{"id": 4391, "parentId": "4365"},
{"id": 4393, "parentId": "4365"},
{"id": 4368, "parentId": "4365"},
{"id": 4400, "parentId": "4365"},
{"id": 4388, "parentId": "4365"},
{"id": 4366, "parentId": "4365"},
{"id": 4385, "parentId": "4365"},
{"id": 4390, "parentId": "4365"},
{"id": 4394, "parentId": "4365"},
{"id": 4386, "parentId": "4365"},
{"id": 4367, "parentId": "4365"},
{"id": 4370, "parentId": "4365"},
{"id": 4397, "parentId": "4365"},
{"id": 4396, "parentId": "4365"},
{"id": 4358, "parentId": "4356"},
{"id": 4401, "parentId": "4356"},
{"id": 4369, "parentId": "4356"},
{"id": 4363, "parentId": "4356"},
{"id": 4364, "parentId": "4356"},
{"id": 4373, "parentId": "4356"},
{"id": 4372, "parentId": "4356"},
{"id": 4380, "parentId": "4356"},
{"id": 4383, "parentId": "4356"},
{"id": 4377, "parentId": "4356"},
{"id": 4371, "parentId": "4356"},
{"id": 4357, "parentId": "4356"},
{"id": 4384, "parentId": "4356"},
{"id": 4375, "parentId": "4356"},
{"id": 4382, "parentId": "4356"},
{"id": 4378, "parentId": "4356"},
{"id": 4376, "parentId": "4356"},
{"id": 4381, "parentId": "4356"},
{"id": 1475, "parentId": "6856"},
{"id": 944, "parentId": "934"},
{"id": 935, "parentId": "933"},
{"id": 1001, "parentId": "933"},
{"id": 957, "parentId": "955"},
{"id": 956, "parentId": "955"},
{"id": 958, "parentId": "955"},
{"id": 1084, "parentId": "1081"},
{"id": 1497, "parentId": "1496"},
{"id": 1576, "parentId": "1751"},
{"id": 1674, "parentId": "1672"},
{"id": 1817, "parentId": "1672"},
{"id": 1750, "parentId": "1672"},
{"id": 1843, "parentId": "1842"},
{"id": 1519, "parentId": "1518"},
{"id": 1760, "parentId": "1759"},
{"id": 1868, "parentId": "1867"},
{"id": 1659, "parentId": "1655"},
{"id": 1657, "parentId": "1655"},
{"id": 1656, "parentId": "1655"},
{"id": 1661, "parentId": "1655"},
{"id": 6211, "parentId": "6209"},
{"id": 6890, "parentId": "6209"},
{"id": 6210, "parentId": "6209"},
{"id": 6610, "parentId": "6209"},
{"id": 5996, "parentId": "5995"},
{"id": 5997, "parentId": "5995"},
{"id": 5998, "parentId": "5995"},
{"id": 6135, "parentId": "5932"},
{"id": 6268, "parentId": "5932"},
{"id": 6079, "parentId": "5932"},
{"id": 6006, "parentId": "5932"},
{"id": 6355, "parentId": "6353"},
{"id": 6354, "parentId": "6353"},
{"id": 6078, "parentId": "6074"},
{"id": 6075, "parentId": "6074"},
{"id": 6076, "parentId": "6074"},
{"id": 6196, "parentId": "6074"},
{"id": 6033, "parentId": "6031"},
{"id": 6107, "parentId": "6031"},
{"id": 6032, "parentId": "6031"},
{"id": 6108, "parentId": "6031"},
{"id": 6010, "parentId": "6007"},
{"id": 6011, "parentId": "6007"},
{"id": 6154, "parentId": "6083"},
{"id": 6058, "parentId": "6055"},
{"id": 6056, "parentId": "6055"},
{"id": 6060, "parentId": "6059"},
{"id": 6203, "parentId": "6059"},
{"id": 6356, "parentId": "5934"},
{"id": 6130, "parentId": "6127"},
{"id": 6131, "parentId": "6127"},
{"id": 6128, "parentId": "6127"},
{"id": 6129, "parentId": "6127"},
{"id": 6552, "parentId": "6044"},
{"id": 6746, "parentId": "6044"},
{"id": 6087, "parentId": "6044"},
{"id": 6091, "parentId": "6090"},
{"id": 6132, "parentId": "6090"},
{"id": 6086, "parentId": "5934"},
{"id": 6050, "parentId": "6030"},
{"id": 6048, "parentId": "6030"},
{"id": 6049, "parentId": "6030"},
{"id": 6133, "parentId": "6095"},
{"id": 6134, "parentId": "6095"},
{"id": 6359, "parentId": "5934"},
{"id": 6965, "parentId": "6909"},
{"id": 6910, "parentId": "6909"},
{"id": 6094, "parentId": "6093"},
{"id": 6699, "parentId": "6093"},
{"id": 6547, "parentId": "6545"},
{"id": 6548, "parentId": "6545"},
{"id": 6546, "parentId": "6545"},
{"id": 6543, "parentId": "5966"},
{"id": 6082, "parentId": "5966"},
{"id": 6000, "parentId": "5999"},
{"id": 6003, "parentId": "5999"},
{"id": 6002, "parentId": "5999"},
{"id": 6198, "parentId": "6013"},
{"id": 6045, "parentId": "6013"},
{"id": 6138, "parentId": "6013"},
{"id": 6014, "parentId": "6013"},
{"id": 6739, "parentId": "6013"}
]

# Crear un grafo dirigido
G = nx.DiGraph()

# Agregar nodos y aristas al grafo
for nodo in nodos:
    G.add_node(nodo['id'])
    if nodo['parentId']:
        G.add_edge(nodo['parentId'], nodo['id'])

# Función para detectar ciclos en el grafo
def tiene_ciclo(grafo):
    visitado = set()
    pila_recursion = set()

    def dfs(nodo):
        if nodo in pila_recursion:
            return True
        if nodo in visitado:
            return False
        
        visitado.add(nodo)
        pila_recursion.add(nodo)

        for vecino in grafo.neighbors(nodo):
            if dfs(vecino):
                return True
        
        pila_recursion.remove(nodo)
        return False

    for nodo in grafo.nodes():
        if dfs(nodo):
            return True
    return False

# Verificar si el grafo tiene ciclos
if tiene_ciclo(G):
    print("El grafo tiene ciclos.")
else:
    print("El grafo no tiene ciclos.")

# Función para identificar nodos con dos o más entradas
def nodos_con_dos_entradas(grafo):
    entradas = {nodo: 0 for nodo in grafo.nodes()}  # Inicializar contador de entradas

    # Contar entradas para cada nodo
    for _, destino in grafo.edges():
        entradas[destino] += 1

    # Identificar nodos con dos o más entradas
    nodos_dos_entradas = [nodo for nodo, conteo in entradas.items() if conteo >= 2]
    
    return nodos_dos_entradas

# Verificar nodos con dos o más entradas
nodos_identificados = nodos_con_dos_entradas(G)
if nodos_identificados:
    print("Nodos con dos o más entradas:", nodos_identificados)
else:
    print("No hay nodos con dos o más entradas.")

# Función para asignar niveles a los nodos
def asignar_niveles(grafo):
    niveles = {}
    
    def dfs(nodo, nivel):
        niveles[nodo] = nivel
        for vecino in grafo.neighbors(nodo):
            if vecino not in niveles:  # Solo visitar nodos no visitados
                dfs(vecino, nivel + 1)

    # Comenzar DFS desde los nodos raíz (sin padres)
    for nodo in grafo.nodes():
        if grafo.in_degree(nodo) == 0:  # Nodo raíz
            dfs(nodo, 0)

    return niveles

# Asignar niveles a los nodos
niveles = asignar_niveles(G)

# Colores para cada nivel
colores = {0: 'lightblue', 1: 'lightgreen', 2: 'lightcoral', 3: 'lightyellow'}


# Dibujar el grafo
plt.figure(figsize=(8, 6))
pos = nx.spring_layout(G)
node_colors = [colores[niveles[nodo]] for nodo in G.nodes()]  # Asignar color según el nivel


nx.draw(G, pos, with_labels=True, node_size=400, node_color=node_colors, font_size=6, font_color='black', font_weight='regular', arrows=True)
plt.title('Grafo de Nodos')
plt.show()