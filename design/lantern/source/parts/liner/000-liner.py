from math import cos, sin, radians
liner_flange_diameter = param("liner_flange_diameter",94.0)
liner_floor_thickness = param("liner_floor_thickness",6.0)
liner_cup_outer_diameter = param("liner_cup_outer_diameter",76.0)
liner_light_pocket_diameter = param("liner_light_pocket_diameter",60.6)
liner_cup_height = param("liner_cup_height",18.0)
liner_shelf_thickness = param("liner_shelf_thickness",4.0)
liner_magnet_pocket_diameter = param("liner_magnet_pocket_diameter",7.2)
liner_magnet_pocket_depth = param("liner_magnet_pocket_depth",2.15)
liner_lower_magnet_radius = param("liner_lower_magnet_radius",41.0)
liner_upper_magnet_radius = param("liner_upper_magnet_radius",42.0)
liner_wire_width = param("liner_wire_width",8.0)
liner_wire_angle = param("liner_wire_angle",-90.0)
liner_height = param("liner_height",96.0)
liner_top_outer_diameter = param("liner_top_outer_diameter",73.4)
liner_top_inner_diameter = param("liner_top_inner_diameter",63.0)
liner_top_thickness = param("liner_top_thickness",5.0)
liner_post_diameter = param("liner_post_diameter",4.0)
liner_post_radius = param("liner_post_radius",33.8)
liner_post_angle = param("liner_post_angle",60.0)
liner = Cylinder(liner_flange_diameter/2,liner_floor_thickness,align=(Align.CENTER,Align.CENTER,Align.MIN))
liner = liner + Cylinder(liner_cup_outer_diameter/2,liner_cup_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
slope_height = (liner_flange_diameter-liner_cup_outer_diameter)/2
slope_bottom = liner_cup_height-liner_shelf_thickness-slope_height
liner = liner + Pos(0,0,slope_bottom)*Cone(liner_cup_outer_diameter/2,liner_flange_diameter/2,slope_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
liner = liner + Pos(0,0,liner_cup_height-liner_shelf_thickness)*Cylinder(liner_flange_diameter/2,liner_shelf_thickness,align=(Align.CENTER,Align.CENTER,Align.MIN))
liner = liner - Pos(0,0,liner_floor_thickness)*Cylinder(liner_light_pocket_diameter/2,liner_cup_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
for angle in (0,120,240):
    for radius, start_z in ((liner_lower_magnet_radius,0),(liner_upper_magnet_radius,liner_cup_height-liner_magnet_pocket_depth)):
        pocket = Pos(radius*cos(radians(angle)),radius*sin(radians(angle)),start_z)*Cylinder(liner_magnet_pocket_diameter/2,liner_magnet_pocket_depth,align=(Align.CENTER,Align.CENTER,Align.MIN))
        liner = liner - pocket
wire_cut = Rot(0,0,liner_wire_angle)*Pos(liner_flange_diameter/2,0,liner_floor_thickness)*Box(liner_flange_diameter,liner_wire_width,liner_cup_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
liner = liner - wire_cut
post_height = liner_height-liner_top_thickness-liner_cup_height
for offset_angle in (0,120,240):
    angle = radians(liner_post_angle+offset_angle)
    post = Pos(liner_post_radius*cos(angle),liner_post_radius*sin(angle),liner_cup_height)*Cylinder(liner_post_diameter/2,post_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
    liner = liner + post
top_ring = Pos(0,0,liner_height-liner_top_thickness)*extrude(Circle(liner_top_outer_diameter/2)-Circle(liner_top_inner_diameter/2),amount=liner_top_thickness)
liner = liner + top_ring
assert liner_floor_thickness > liner_magnet_pocket_depth
assert liner_top_inner_diameter > liner_light_pocket_diameter
assert liner_post_radius-liner_post_diameter/2 > liner_light_pocket_diameter/2
assert len(liner.solids()) == 1
assert liner.is_valid
liner.color=Color(0.88,0.82,0.57)
publish("liner",liner,"灯托内胆",material="petg")
