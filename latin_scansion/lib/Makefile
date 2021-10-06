all: scansion_pb2.py

scansion_pb2.py: scansion.proto
	protoc --python_out=. $<
