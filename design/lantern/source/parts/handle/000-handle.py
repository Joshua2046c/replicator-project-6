handle_center_spacing = param("handle_center_spacing",130.0)
handle_foot_spacing = param("handle_foot_spacing",102.0)
handle_band_width = param("handle_band_width",10.0)
handle_thickness = param("handle_thickness",10.0)
handle_height = param("handle_height",198.0)
handle_jog_start = param("handle_jog_start",4.0)
handle_jog_height = param("handle_jog_height",20.0)
handle_tenon_size = param("handle_tenon_size",7.8)
handle_tenon_length = param("handle_tenon_length",8.0)
handle_edge_radius = param("handle_edge_radius",0.7)
outer_radius = handle_center_spacing/2+handle_band_width/2
inner_radius = handle_center_spacing/2-handle_band_width/2
spring_height = handle_height-outer_radius
arch = Pos(0,0,spring_height)*Rot(90,0,0)*extrude(Circle(outer_radius)-Circle(inner_radius),amount=handle_thickness/2,both=True)
upper_half = Pos(0,0,spring_height)*Box(outer_radius*2+2,handle_thickness+2,outer_radius+1,align=(Align.CENTER,Align.CENTER,Align.MIN))
handle = arch & upper_half
half_band=handle_band_width/2
foot=handle_foot_spacing/2
upper=handle_center_spacing/2
jog_top=handle_jog_start+handle_jog_height
for side in (-1,1):
    outline=Polygon((side*(foot-half_band),0),(side*(foot+half_band),0),(side*(foot+half_band),handle_jog_start),(side*(upper+half_band),jog_top),(side*(upper+half_band),spring_height),(side*(upper-half_band),spring_height),(side*(upper-half_band),jog_top),(side*(foot-half_band),handle_jog_start),align=None)
    leg=Rot(90,0,0)*extrude(outline,amount=handle_thickness/2,both=True)
    handle += leg
handle = fillet([edge for edge in handle.edges().filter_by(Axis.Y) if edge.center().Z < jog_top+0.001],handle_edge_radius)
for side in (-1,1):
    handle += Pos(side*foot,0,-handle_tenon_length)*Box(handle_tenon_size,handle_tenon_size,handle_tenon_length+1,align=(Align.CENTER,Align.CENTER,Align.MIN))
assert len(handle.solids()) == 1 and handle.is_valid
handle.color=Color(0.83,0.27,0.46)
publish("handle",handle,"折脚拱形提手",material="petg")
