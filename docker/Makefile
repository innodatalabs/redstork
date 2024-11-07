all: main

main: main.o
	cc -g -o main main.o

main.o: main.c
	cc -g -c main.c

clean:
	rm -f *.o main