from math import cos, sin, radians
base_diameter = param("base_diameter",114.0)
base_thickness = param("base_thickness",12.0)
base_floor_thickness = param("base_floor_thickness",4.0)
base_rim_inner_diameter = param("base_rim_inner_diameter",90.0)
base_socket_center = param("base_socket_center",51.0)
base_socket_size = param("base_socket_size",8.1)
base_socket_depth = param("base_socket_depth",8.2)
base_magnet_pocket_diameter = param("base_magnet_pocket_diameter",7.2)
base_magnet_pocket_depth = param("base_magnet_pocket_depth",2.15)
base_magnet_radius = param("base_magnet_radius",39.2)
base_magnet_count = param("base_magnet_count",2)
base_magnet_angle = param("base_magnet_angle",0.0)
base_edge_radius = param("base_edge_radius",0.7)
base = Cylinder(base_diameter/2,base_thickness,align=(Align.CENTER,Align.CENTER,Align.MIN))
base = fillet(base.edges().filter_by(GeomType.CIRCLE),base_edge_radius)
base -= Pos(0,0,base_floor_thickness)*Cylinder(base_rim_inner_diameter/2,base_thickness,align=(Align.CENTER,Align.CENTER,Align.MIN))
for side in (-1,1):
    base -= Pos(side*base_socket_center,0,base_thickness-base_socket_depth)*Box(base_socket_size,base_socket_size,base_socket_depth+1,align=(Align.CENTER,Align.CENTER,Align.MIN))
for index in range(int(base_magnet_count)):
    angle=base_magnet_angle+index*360/int(base_magnet_count)
    base -= Pos(base_magnet_radius*cos(radians(angle)),base_magnet_radius*sin(radians(angle)),base_floor_thickness-base_magnet_pocket_depth)*Cylinder(base_magnet_pocket_diameter/2,base_magnet_pocket_depth+1,align=(Align.CENTER,Align.CENTER,Align.MIN))
assert base_floor_thickness-base_magnet_pocket_depth >= 1.5
assert len(base.solids()) == 1 and base.is_valid
base.color=Color(0.12,0.62,0.60)
publish("base",base,"浅托盘底座",material="petg")
