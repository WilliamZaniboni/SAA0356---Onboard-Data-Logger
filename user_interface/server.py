from vpython import *
from time import *
import numpy as np
import math
import socket
import sys
import time
from stl import mesh 
import pyvista



s = 'Gráficos de <b><i>Row</i></b>, <b><i>Pitch</i></b>, <b><i>Yaw</i></b> em função do tempo.'
grafico = graph(title=s, xtitle='Tempo (s)', ytitle='Ângulo', fast=False, width=800)
funct1 = gcurve(color=color.blue, width=4, marker_color=color.orange, label='Row')
funct2 = gcurve( color=color.green, label='Pitch')
funct3 = gcurve(color=color.red, size=6, label='Yaw')


your_mesh = mesh.Mesh.from_file('airplane.stl') 


volume, cog, inertia = your_mesh.get_mass_properties() 
print("Volume = {0}".format(volume)) 
print("Position of the center of gravity (COG) = {0}".format(cog)) 
print("Inertia matrix at expressed at the COG = {0}".format(inertia[0,:])) 
print(" {0}".format(inertia[1,:])) 
print(" {0}".format(inertia[2,:]))


sgrid = pyvista.PolyData('airplane.stl')
sgrid.translate([-cog[0], -1.15*cog[1], -cog[2]])
sgrid.rotate_z(90)
sgrid.rotate_x(-90)
points = sgrid.points.copy()
cent = [0,0,0]
direction = [1,1,1]


# Start a plotter object and set the scalars to the Z height
plotter = pyvista.Plotter(off_screen=None, notebook=None)
plotter.add_axes()
plotter.add_axes_at_origin(labels_off = True)
plotter.add_mesh(sgrid)
plotter.show(title='Airplane', window_size=[800, 600],
                 auto_close=False, interactive_update=True)



# Criando o server no endereço padrão da conexão via USB, trocar caso esteja usando outra
# forma de conexão.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("192.168.7.2", 8888)
print('Iniciando servidor no endereço:', server_address)
sock.bind(server_address)
sock.listen(1)

while True:
    # Wait for a connection
    print('Servidor: Esperando conexao... ')
    connection, client_address = sock.accept()
    try:
        print('Servidor: Conexão feita com:', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(30).decode("utf-8")

            if data:
                str_time, str_roll, str_pitch, str_yaw =  data.split("/") #Le a string e a converte
                time = float(str_time)
                roll = float(str_roll)
                pitch = float(str_pitch)
                yaw = float(str_yaw)
     
                funct1.plot(time, roll)
                funct2.plot( time, pitch )
                funct3.plot( time, yaw )
                print("Roll=",roll," Pitch=",pitch,"Yaw=",yaw)
               
                sgrid.rotate_z(yaw)
                sgrid.rotate_y(pitch)
                sgrid.rotate_x(roll)

                plotter.update()

                connection.sendall(("R:" + data).encode()) #responde o cliente
            
            
    finally:
        print("Atualizando dados")
      






