from math import cos, sin, radians, pi, sqrt
shade_height = param("shade_height",76.0)
shade_top_inset = param("shade_top_inset",4.0)
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
shade_rim_wave_depth = param("shade_rim_wave_depth",0.6)
shade_shoulder_min_wall = param("shade_shoulder_min_wall",1.5)
shade_body_wall_thickness = param("shade_body_wall_thickness",1.2)
shade_inner_transition_height = param("shade_inner_transition_height",6.0)
outer_radius=shade_belly_diameter/2+shade_rib_radius
end_radius=shade_ring_outer_diameter/2
outer_round=outer_radius-end_radius
inner_radius=shade_belly_diameter/2-shade_wall_thickness
inner_end=end_radius-shade_wall_thickness
inner_round=inner_radius-inner_end
top_end_radius=end_radius-shade_top_inset
top_outer_round=outer_radius-top_end_radius
top_inner_end=top_end_radius-shade_wall_thickness
top_inner_round=inner_radius-top_inner_end
assert 0 < shade_shoulder_min_wall <= shade_wall_thickness
top_inner_center_z=shade_height-sqrt((top_inner_round+shade_shoulder_min_wall)**2-shade_wall_thickness**2)
top_inner_end_z=top_inner_center_z+top_inner_round
assert outer_round>0 and inner_round>0
assert shade_top_inset>=0 and top_inner_end>shade_ring_inner_diameter/2
assert shade_height>outer_round+top_outer_round+shade_ring_height
assert shade_ring_height>shade_magnet_pocket_depth
assert shade_magnet_radius-shade_magnet_pocket_diameter/2>shade_ring_inner_diameter/2
assert 0 < shade_rim_wave_depth <= shade_rib_radius
shoulder_z=shade_height-top_outer_round
def wave_wire(peak_radius, depth, height):
    wave_edges=[]
    for flute_index in range(int(shade_rib_count)):
        points=[]
        for sample_index in range(9):
            angle=(flute_index+sample_index/8)*2*pi/int(shade_rib_count)
            radius=peak_radius-depth*(1-cos(int(shade_rib_count)*angle))/2
            points.append((radius*cos(angle),radius*sin(angle),height))
        wave_edges.append(Edge.make_spline(points))
    return Wire(wave_edges)
lower_edges=[
 Edge.make_line((0,0,0),(end_radius,0,0)),
 Edge.make_three_point_arc((end_radius,0,0),(end_radius+outer_round/sqrt(2),0,outer_round-outer_round/sqrt(2)),(outer_radius,0,outer_round)),
 Edge.make_line((outer_radius,0,outer_round),(outer_radius,0,shoulder_z)),
 Edge.make_line((outer_radius,0,shoulder_z),(0,0,shoulder_z)),
 Edge.make_line((0,0,shoulder_z),(0,0,0))
]
lower_solid=revolve(Face(Wire(lower_edges)),axis=Axis.Z)
wave_prism=extrude(Face(wave_wire(outer_radius,shade_rib_radius,0)),amount=shoulder_z)
lower_solid=lower_solid & wave_prism
shoulder_sections=[]
for section_index in range(9):
    sweep_angle=section_index*pi/16
    blend=sin(sweep_angle)**2
    peak_radius=top_end_radius+top_outer_round*cos(sweep_angle)+shade_rim_wave_depth*blend
    depth=shade_rib_radius*(1-blend)+shade_rim_wave_depth*blend
    height=shoulder_z+top_outer_round*sin(sweep_angle)
    shoulder_sections.append(Face(wave_wire(peak_radius,depth,height)))
upper_solid=loft(shoulder_sections)
outer_solid=lower_solid+upper_solid
cavity_edges=[
 Edge.make_line((0,0,0),(shade_ring_inner_diameter/2,0,0)),
 Edge.make_line((shade_ring_inner_diameter/2,0,0),(shade_ring_inner_diameter/2,0,shade_ring_height)),
 Edge.make_line((shade_ring_inner_diameter/2,0,shade_ring_height),(inner_end,0,shade_ring_height)),
 Edge.make_three_point_arc((inner_end,0,shade_ring_height),(inner_end+inner_round/sqrt(2),0,shade_ring_height+inner_round-inner_round/sqrt(2)),(inner_radius,0,shade_ring_height+inner_round)),
 Edge.make_line((inner_radius,0,shade_ring_height+inner_round),(inner_radius,0,top_inner_center_z)),
 Edge.make_three_point_arc((inner_radius,0,top_inner_center_z),(top_inner_end+top_inner_round/sqrt(2),0,top_inner_center_z+top_inner_round/sqrt(2)),(top_inner_end,0,top_inner_end_z)),
 Edge.make_line((top_inner_end,0,top_inner_end_z),(top_inner_end,0,shade_height+shade_wall_thickness)),
 Edge.make_line((top_inner_end,0,shade_height+shade_wall_thickness),(0,0,shade_height+shade_wall_thickness)),
 Edge.make_line((0,0,shade_height+shade_wall_thickness),(0,0,0))
]
cavity=revolve(Face(Wire(cavity_edges)),axis=Axis.Z)
inner_shoulder_face=cavity.faces().filter_by(GeomType.TORUS).sort_by(Axis.Z)[-1]
shoulder_distances=[face.distance_to(inner_shoulder_face) for face in upper_solid.faces() if face.geom_type != GeomType.PLANE]
measured_shoulder_wall=min(shoulder_distances)
print("upper_shoulder_minimum_surface_distance_mm",measured_shoulder_wall)
assert measured_shoulder_wall >= shade_shoulder_min_wall-0.005
body_bottom=shade_ring_height+inner_round
body_top=shoulder_z
assert 0 < shade_body_wall_thickness <= shade_wall_thickness
assert body_top-body_bottom > 2*shade_inner_transition_height
def inner_wave_wire(height, blend):
    inner_edges=[]
    for flute_index in range(int(shade_rib_count)):
        points=[]
        for sample_index in range(33):
            angle=(flute_index+sample_index/32)*2*pi/int(shade_rib_count)
            radius=outer_radius-shade_rib_radius*(1-cos(int(shade_rib_count)*angle))/2
            derivative=-shade_rib_radius*int(shade_rib_count)*sin(int(shade_rib_count)*angle)/2
            normal_length=sqrt(radius**2+derivative**2)
            normal_x=(radius*cos(angle)+derivative*sin(angle))/normal_length
            normal_y=(radius*sin(angle)-derivative*cos(angle))/normal_length
            inset_x=radius*cos(angle)-shade_body_wall_thickness*normal_x
            inset_y=radius*sin(angle)-shade_body_wall_thickness*normal_y
            points.append(((1-blend)*inner_radius*cos(angle)+blend*inset_x,(1-blend)*inner_radius*sin(angle)+blend*inset_y,height))
        inner_edges.append(Edge.make_spline(points))
    return Wire(inner_edges)
outer_section=wave_wire(outer_radius,shade_rib_radius,0)
inner_section=inner_wave_wire(0,1)
body_wall_measured=outer_section.distance_to(inner_section)
print("body_normal_wall_min_mm",body_wall_measured)
assert abs(body_wall_measured-shade_body_wall_thickness)<0.01
bottom_blend=[]
top_blend=[]
for section_index in range(5):
    fraction=section_index/4
    blend=fraction*fraction*(3-2*fraction)
    bottom_blend.append(Face(inner_wave_wire(body_bottom+shade_inner_transition_height*fraction,blend)))
    top_blend.append(Face(inner_wave_wire(body_top-shade_inner_transition_height+shade_inner_transition_height*fraction,1-blend)))
body_void=loft(bottom_blend)
body_void+=extrude(Face(Pos(0,0,body_bottom+shade_inner_transition_height)*inner_section),amount=body_top-body_bottom-2*shade_inner_transition_height)
body_void+=loft(top_blend)
cavity=cavity+body_void
shade=outer_solid-cavity
print("rim_wave_depth_mm",shade_rim_wave_depth,"rim_radial_wall_min_mm",top_end_radius-top_inner_end)
for index in range(int(shade_magnet_count)):
    angle=shade_magnet_angle+index*360/int(shade_magnet_count)
    pocket=Pos(shade_magnet_radius*cos(radians(angle)),shade_magnet_radius*sin(radians(angle)),0)*Cylinder(shade_magnet_pocket_diameter/2,shade_magnet_pocket_depth,align=(Align.CENTER,Align.CENTER,Align.MIN))
    shade-=pocket
assert len(shade.solids())==1 and shade.is_valid
shade.color=Color(0.16,0.70,0.40)
publish("shade",shade,"圆弧直筒波纹灯罩",material="petg")
