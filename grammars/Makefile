meter.far: meter.grm inventory.far byte.far
	thraxcompiler --input_grammar=$< --output_far=$@

inventory.far: inventory.grm byte.far
	thraxcompiler --input_grammar=$< --output_far=$@

byte.far: byte.grm 
	thraxcompiler --input_grammar=$< --output_far=$@

clean:
	rm -f inventory.far byte.far
