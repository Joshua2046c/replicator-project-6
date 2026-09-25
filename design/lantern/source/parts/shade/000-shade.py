from math import cos, sin, radians, pi, sqrt
shade_height = param("shade_height",76.0)
shade_belly_diameter = param("shade_belly_diameter",106.0)
shade_wall_thickness = param("shade_wall_thickness",1.8)
shade_ring_outer_diameter = param("shade_ring_outer_diameter",94.0)
shade_ring_inner_diameter = param("shade_ring_inner_diameter",69.2)
shade_ring_height = param("shade_ring_height",4.0)
shade_rib_count = param("shade_rib_count",40)
shade_rib_radius = param("shade_rib_radius",1.8)
shade_magnet_pocket_diameter = param("shade_magnet_pocket_diameter",7.2)
shade_magnet_pocket_depth = param("shade_magnet_pocket_depth",2.15)
shade_magnet_radius = param("shade_magnet_radius",39.2)
shade_magnet_count = param("shade_magnet_count",2)
shade_magnet_angle = param("shade_magnet_angle",0.0)
outer_radius=shade_belly_diameter/2+shade_rib_radius
end_radius=shade_ring_outer_diameter/2
outer_round=outer_radius-end_radius
inner_radius=shade_belly_diameter/2-shade_wall_thickness
inner_end=end_radius-shade_wall_thickness
inner_round=inner_radius-inner_end
assert outer_round>0 and inner_round>0
assert shade_height>2*outer_round+shade_ring_height
assert shade_ring_height>shade_magnet_pocket_depth
assert shade_magnet_radius-shade_magnet_pocket_diameter/2>shade_ring_inner_diameter/2
edges=[
 Edge.make_three_point_arc((end_radius,0,0),(end_radius+outer_round/sqrt(2),0,outer_round-outer_round/sqrt(2)),(outer_radius,0,outer_round)),
 Edge.make_line((outer_radius,0,outer_round),(outer_radius,0,shade_height-outer_round)),
 Edge.make_three_point_arc((outer_radius,0,shade_height-outer_round),(end_radius+outer_round/sqrt(2),0,shade_height-outer_round+outer_round/sqrt(2)),(end_radius,0,shade_height)),
 Edge.make_line((end_radius,0,shade_height),(inner_end,0,shade_height)),
 Edge.make_three_point_arc((inner_end,0,shade_height),(inner_end+inner_round/sqrt(2),0,shade_height-inner_round+inner_round/sqrt(2)),(inner_radius,0,shade_height-inner_round)),
 Edge.make_line((inner_radius,0,shade_height-inner_round),(inner_radius,0,shade_ring_height+inner_round)),
 Edge.make_three_point_arc((inner_radius,0,shade_ring_height+inner_round),(inner_end+inner_round/sqrt(2),0,shade_ring_height+inner_round-inner_round/sqrt(2)),(inner_end,0,shade_ring_height)),
 Edge.make_line((inner_end,0,shade_ring_height),(shade_ring_inner_diameter/2,0,shade_ring_height)),
 Edge.make_line((shade_ring_inner_diameter/2,0,shade_ring_height),(shade_ring_inner_diameter/2,0,0)),
 Edge.make_line((shade_ring_inner_diameter/2,0,0),(end_radius,0,0))
]
rounded_shell=revolve(Face(Wire(edges)),axis=Axis.Z)
wave_edges=[]
for flute_index in range(int(shade_rib_count)):
    points=[]
    for sample_index in range(9):
        angle=(flute_index+sample_index/8)*2*pi/int(shade_rib_count)
        radius=shade_belly_diameter/2+shade_rib_radius*(1+cos(int(shade_rib_count)*angle))/2
        points.append((radius*cos(angle),radius*sin(angle),0))
    wave_edges.append(Edge.make_spline(points))
wave_prism=extrude(Face(Wire(wave_edges)),amount=shade_height)
shade=rounded_shell & wave_prism
assert rounded_shell.volume-shade.volume>shade_rib_radius*shade_height
print("wave_removed_volume_mm3",rounded_shell.volume-shade.volume)
for index in range(int(shade_magnet_count)):
    angle=shade_magnet_angle+index*360/int(shade_magnet_count)
    pocket=Pos(shade_magnet_radius*cos(radians(angle)),shade_magnet_radius*sin(radians(angle)),0)*Cylinder(shade_magnet_pocket_diameter/2,shade_magnet_pocket_depth,align=(Align.CENTER,Align.CENTER,Align.MIN))
    shade-=pocket
assert len(shade.solids())==1 and shade.is_valid
shade.color=Color(0.16,0.70,0.40)
publish("shade",shade,"圆弧直筒波纹灯罩",material="petg")
