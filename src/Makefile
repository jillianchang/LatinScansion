all: scansion_pb2.py tests

tests: scansion_test.py
	python $<

scansion_pb2.py: scansion.proto
	protoc --python_out=. $<
