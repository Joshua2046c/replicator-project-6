from math import cos, sin, radians
liner_cup_outer_diameter = param("liner_cup_outer_diameter",88.0)
liner_floor_thickness = param("liner_floor_thickness",6.0)
liner_light_pocket_diameter = param("liner_light_pocket_diameter",60.6)
liner_cup_height = param("liner_cup_height",28.0)
liner_height = param("liner_height",108.0)
liner_top_outer_diameter = param("liner_top_outer_diameter",68.4)
liner_top_inner_diameter = param("liner_top_inner_diameter",63.0)
liner_top_thickness = param("liner_top_thickness",5.0)
liner_slot_count = param("liner_slot_count",12)
liner_slot_width = param("liner_slot_width",9.0)
liner_slot_angle = param("liner_slot_angle",-90.0)
liner_magnet_pocket_diameter = param("liner_magnet_pocket_diameter",7.2)
liner_magnet_pocket_depth = param("liner_magnet_pocket_depth",2.15)
liner_lower_magnet_radius = param("liner_lower_magnet_radius",39.2)
liner_upper_magnet_radius = param("liner_upper_magnet_radius",39.2)
liner_wire_width = param("liner_wire_width",8.0)
liner_wire_angle = param("liner_wire_angle",-90.0)
liner = Cylinder(liner_cup_outer_diameter/2,liner_cup_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
liner -= Pos(0,0,liner_floor_thickness)*Cylinder(liner_light_pocket_diameter/2,liner_cup_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
tube = Pos(0,0,liner_cup_height)*extrude(Circle(liner_top_outer_diameter/2)-Circle(liner_top_inner_diameter/2),amount=liner_height-liner_cup_height)
slot_height=liner_height-liner_cup_height-liner_top_thickness
for index in range(int(liner_slot_count)):
    angle=liner_slot_angle+index*360/int(liner_slot_count)
    window=Rot(0,0,angle)*Pos(liner_top_outer_diameter/2,0,liner_cup_height)*Box(liner_top_outer_diameter/2,liner_slot_width,slot_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
    tube -= window
liner += tube
for angle in (0,120,240):
    for radius,start_z in ((liner_lower_magnet_radius,0),(liner_upper_magnet_radius,liner_cup_height-liner_magnet_pocket_depth)):
        liner -= Pos(radius*cos(radians(angle)),radius*sin(radians(angle)),start_z)*Cylinder(liner_magnet_pocket_diameter/2,liner_magnet_pocket_depth,align=(Align.CENTER,Align.CENTER,Align.MIN))
liner -= Rot(0,0,liner_wire_angle)*Pos(liner_cup_outer_diameter/2,0,liner_floor_thickness)*Box(liner_cup_outer_diameter,liner_wire_width,liner_cup_height-liner_floor_thickness,align=(Align.CENTER,Align.CENTER,Align.MIN))
assert liner_floor_thickness > liner_magnet_pocket_depth
assert liner_top_inner_diameter > liner_light_pocket_diameter
assert liner_cup_height-liner_floor_thickness >= 8
assert len(liner.solids()) == 1 and liner.is_valid
liner.color=Color(0.88,0.82,0.57)
publish("liner",liner,"直筒镂空内胆",material="petg")
