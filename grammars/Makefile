normalize.far: normalize.grm byte.far casefold.tsv
	thraxcompiler --input_grammar=$< --output_far=$@

byte.far: byte.grm 
	thraxcompiler --input_grammar=$< --output_far=$@

clean:
	rm -f byte.far
