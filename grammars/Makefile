all: normalize.far pron.far

byte.far: byte.grm 
	thraxcompiler --input_grammar=$< --output_far=$@

normalize.far: normalize.grm byte.far
	thraxcompiler --input_grammar=$< --output_far=$@

pron.far: pron.grm byte.far
	thraxcompiler --input_grammar=$< --output_far=$@

clean:
	rm -f byte.far
