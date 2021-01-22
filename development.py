from stl import mesh 
import numpy as np
import pyvista
import time


def plot_wave(fps=200, frequency=1, wavetime=3, interactive=False,
              off_screen=None, notebook=None):
    
    cpos = [(6.879481857604187, -32.143727535933195, 23.05622921691103),
            (-0.2336056403734026, -0.6960083534590372, -0.7226721553894022),
            (-0.008900669873416645, 0.6018246347860926, 0.7985786667826725)]

    # Create and plot structured grid
    # sgrid = pyvista.StructuredGrid(X, Y, Z)

    # Using an existing closed stl file: 
    your_mesh = mesh.Mesh.from_file('airplane5.stl') 
    volume, cog, inertia = your_mesh.get_mass_properties() 
    print("Volume = {0}".format(volume)) 
    print("Position of the center of gravity (COG) = {0}".format(cog)) 
    print("Inertia matrix at expressed at the COG = {0}".format(inertia[0,:])) 
    print(" {0}".format(inertia[1,:])) 
    print(" {0}".format(inertia[2,:]))


    sgrid = pyvista.PolyData('airplane5.stl')
    sgrid.translate([-cog[0], -1.15*cog[1], -cog[2]])

    # Get pointer to points
    points = sgrid.points.copy()
    sgrid.rotate_x(90)
    sgrid.rotate_z(-90)

    cent = [0,0,0]
    direction = [1,1,1]


    # Start a plotter object and set the scalars to the Z height
    plotter = pyvista.Plotter(off_screen=off_screen, notebook=notebook)
    plotter.add_axes()
    plotter.add_axes_at_origin(labels_off = True)
    # plotter.add_mesh(sgrid, scalars=Z.ravel())
    plotter.add_mesh(sgrid)
    # plotter.camera_position = cpos
    plotter.show(title='Wave Example', window_size=[800, 600],
                 auto_close=False, interactive_update=True)

    # Update Z and display a frame for each updated position
    tdelay = 1. / fps
    tlast = time.time()
    tstart = time.time()
    while time.time() - tstart < wavetime:
        # get phase from start
        telap = time.time() - tstart
        phase = telap * 2 * np.pi * frequency
        #Z = np.sin(R + phase)
        #points[:, -1] = Z.ravel()

        # update plotting object, but don't automatically render
        sgrid.rotate_z(2)
        # sgrid.rotate_y(0)
        # sgrid.rotate_x(10)
        
        #plotter.update_coordinates(points, render=False)
        #plotter.update_scalars(1, render=False)

        # Render and get time to render
        #rstart = time.time()
        plotter.update()
        # plotter.render()
        #rstop = time.time()

        # time delay
        tpast = time.time() - tlast
        if tpast < tdelay and tpast >= 0:
            time.sleep(tdelay - tpast)

        # get render time and actual FPS
        # rtime = rstop - rstart
        # act_fps = 1 / (time.time() - tlast + 1E-10)
        tlast = time.time()

    # Close movie and delete object
    plotter.close()

    return points


plot_wave()