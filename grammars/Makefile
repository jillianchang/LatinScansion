final_scan.far: final_scan.grm optional.far meter.far
	thraxcompiler --input_grammar=$< --output_far=$@

optional.far: optional.grm byte.far inventory.far utility.far
	thraxcompiler --input_grammar=$< --output_far=$@

byte.far: byte.grm 
	thraxcompiler --input_grammar=$< --output_far=$@

inventory.far: inventory.grm byte.far
	thraxcompiler --input_grammar=$< --output_far=$@

utility.far: utility.grm inventory.far
	thraxcompiler --input_grammar=$< --output_far=$@

meter.far: meter.grm inventory.far byte.far utility.far
	thraxcompiler --input_grammar=$< --output_far=$@

clean:
	rm -f optional.far meter.far byte.far inventory.far utility.far
