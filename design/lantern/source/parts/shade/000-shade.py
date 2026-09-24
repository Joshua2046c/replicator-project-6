from math import cos, sin, radians, pi
shade_height = param("shade_height",76.0)
shade_belly_diameter = param("shade_belly_diameter",106.0)
shade_waist_diameter = param("shade_waist_diameter",99.0)
shade_neck_diameter = param("shade_neck_diameter",79.2)
shade_wall_thickness = param("shade_wall_thickness",1.8)
shade_ring_outer_diameter = param("shade_ring_outer_diameter",94.0)
shade_ring_inner_diameter = param("shade_ring_inner_diameter",74.0)
shade_ring_height = param("shade_ring_height",4.0)
shade_rib_count = param("shade_rib_count",40)
shade_rib_radius = param("shade_rib_radius",0.9)
shade_magnet_pocket_diameter = param("shade_magnet_pocket_diameter",7.2)
shade_magnet_pocket_depth = param("shade_magnet_pocket_depth",2.15)
shade_magnet_radius = param("shade_magnet_radius",42.0)
shade_wire_width = param("shade_wire_width",8.0)
shade_wire_height = param("shade_wire_height",6.0)
shade_wire_angle = param("shade_wire_angle",-90.0)
stations = [
    (0.0,shade_ring_outer_diameter/2),
    (0.10,shade_belly_diameter/2-3),
    (0.25,shade_belly_diameter/2),
    (0.43,shade_waist_diameter/2+0.5),
    (0.48,shade_waist_diameter/2),
    (0.63,shade_belly_diameter/2),
    (0.77,shade_belly_diameter/2-2),
    (0.90,shade_neck_diameter/2+5),
    (1.0,shade_neck_diameter/2)
]
outside_sections=[]
inside_sections=[]
sample_count=int(shade_rib_count)*8
for fraction,radius in stations:
    height=shade_ring_height+fraction*(shade_height-shade_ring_height)
    amplitude=shade_rib_radius*sin(pi*fraction)**0.5
    points=[]
    for index in range(sample_count):
        angle=index*2*pi/sample_count
        fluted_radius=radius+amplitude*(1+cos(int(shade_rib_count)*angle))/2
        points.append((fluted_radius*cos(angle),fluted_radius*sin(angle),height))
    outline=Wire([Edge.make_spline(points,periodic=True)])
    outside_sections.append(Face(outline))
    inside_sections.append(Plane.XY.offset(height)*Circle(radius-shade_wall_thickness))
outside=loft(outside_sections)
inside=loft(inside_sections)
shade=outside-inside
ring=extrude(Circle(shade_ring_outer_diameter/2)-Circle(shade_ring_inner_diameter/2),amount=shade_ring_height+0.6)
shade=shade+ring
for angle in (0,120,240):
    pocket=Pos(shade_magnet_radius*cos(radians(angle)),shade_magnet_radius*sin(radians(angle)),0)*Cylinder(shade_magnet_pocket_diameter/2,shade_magnet_pocket_depth,align=(Align.CENTER,Align.CENTER,Align.MIN))
    shade=shade-pocket
wire_cut=Rot(0,0,shade_wire_angle)*Pos(shade_belly_diameter/2,0,0)*Box(shade_belly_diameter,shade_wire_width,shade_wire_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
shade=shade-wire_cut
assert len(shade.solids())==1, str([(solid.volume,str(solid.bounding_box())) for solid in shade.solids()])
assert shade.is_valid
shade.color=Color(0.16,0.70,0.40)
publish("shade",shade,"薄壁竖纹灯罩",material="petg")
