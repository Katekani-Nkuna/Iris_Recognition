all:
	g++ -std=c++11 main.cpp `pkg-config --libs --cflags opencv` -o hello -I/usr/include/python2.7 -lpython2.7 -L . libdvp.so libhzd.so -lpthread   -Wl,-rpath=.

run:
	./hello

clean:
	rm hello
