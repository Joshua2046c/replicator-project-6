handle_center_spacing = param("handle_center_spacing",130.0)
handle_band_width = param("handle_band_width",8.0)
handle_thickness = param("handle_thickness",8.0)
handle_height = param("handle_height",198.0)
handle_tenon_size = param("handle_tenon_size",7.8)
handle_tenon_length = param("handle_tenon_length",8.0)
handle_edge_radius = param("handle_edge_radius",0.7)
outer_radius = handle_center_spacing/2+handle_band_width/2
inner_radius = handle_center_spacing/2-handle_band_width/2
spring_height = handle_height-outer_radius
arch = Pos(0,0,spring_height)*Rot(90,0,0)*extrude(Circle(outer_radius)-Circle(inner_radius),amount=handle_thickness/2,both=True)
upper_half = Pos(0,0,spring_height)*Box(outer_radius*2+2,handle_thickness+2,outer_radius+1,align=(Align.CENTER,Align.CENTER,Align.MIN))
handle = arch & upper_half
for side in (-1,1):
    leg = Pos(side*handle_center_spacing/2,0,0)*Box(handle_band_width,handle_thickness,spring_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
    handle = handle + leg
handle = fillet([edge for edge in handle.edges().filter_by(Axis.Y) if abs(edge.center().Z)<0.001],handle_edge_radius)
for side in (-1,1):
    peg = Pos(side*handle_center_spacing/2,0,-handle_tenon_length)*Box(handle_tenon_size,handle_tenon_size,handle_tenon_length+1,align=(Align.CENTER,Align.CENTER,Align.MIN))
    handle = handle + peg
assert len(handle.solids()) == 1
assert handle.is_valid
handle.color=Color(0.83,0.27,0.46)
publish("handle",handle,"拱形提手",material="petg")
