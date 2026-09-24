from math import cos, sin, radians
base_diameter = param("base_diameter", 114.0)
base_thickness = param("base_thickness", 12.0)
base_ear_length = param("base_ear_length", 30.0)
base_ear_width = param("base_ear_width", 22.0)
base_ear_center = param("base_ear_center", 60.0)
base_socket_center = param("base_socket_center", 65.0)
base_socket_size = param("base_socket_size", 8.1)
base_socket_depth = param("base_socket_depth", 8.2)
base_magnet_pocket_diameter = param("base_magnet_pocket_diameter", 7.2)
base_magnet_pocket_depth = param("base_magnet_pocket_depth", 2.15)
base_magnet_radius = param("base_magnet_radius", 41.0)
base_rim_outer_diameter = param("base_rim_outer_diameter", 104.0)
base_rim_inner_diameter = param("base_rim_inner_diameter", 94.6)
base_rim_height = param("base_rim_height", 2.0)
base_edge_radius = param("base_edge_radius", 1.0)
base = Cylinder(base_diameter / 2, base_thickness, align=(Align.CENTER,Align.CENTER,Align.MIN))
base = fillet(base.edges().filter_by(GeomType.CIRCLE), base_edge_radius)
for side in (-1, 1):
    ear = Pos(side * base_ear_center, 0, 0) * extrude(RectangleRounded(base_ear_length,base_ear_width,base_edge_radius*2), amount=base_thickness)
    base = base + ear
    socket = Pos(side * base_socket_center,0,base_thickness-base_socket_depth) * Box(base_socket_size,base_socket_size,base_socket_depth+1,align=(Align.CENTER,Align.CENTER,Align.MIN))
    base = base - socket
rim = Pos(0,0,base_thickness) * extrude(Circle(base_rim_outer_diameter/2)-Circle(base_rim_inner_diameter/2),amount=base_rim_height)
base = base + rim
for angle in (0,120,240):
    center_x = base_magnet_radius*cos(radians(angle))
    center_y = base_magnet_radius*sin(radians(angle))
    cutter = Pos(center_x,center_y,base_thickness-base_magnet_pocket_depth)*Cylinder(base_magnet_pocket_diameter/2,base_magnet_pocket_depth+1,align=(Align.CENTER,Align.CENTER,Align.MIN))
    base = base - cutter
assert len(base.solids()) == 1
assert base.is_valid
base.color = Color(0.12,0.62,0.60)
publish("base",base,"底座",material="petg")
