optimize=-O3
FFLAGS=$(optimize)
CFLAGS=$(optimize)
#SACHOME=/home/crempien/sac
#if SAC library has been installed, uncomment the next two lines
#CFLAGS=$(optimize) -DSAC_LIB
#SACLIB=-L$(SACHOME)/lib -lsac -lsacio
#
FC=gfortran -ffixed-line-length-132
CC=gcc

SUBS = fft.o Complex.o sacio.o
FKSUBS = fk.o kernel.o prop.o source.o bessel.o $(SUBS)

all: fk syn st_fk trav sachd

syn: syn.o ${SUBS} radiats.o futterman.o
	${CC} -o $@ $^ ${SACLIB} -lm

fk: ${FKSUBS} haskell.o
	${FC} -o $@ $^

st_fk: ${FKSUBS} st_haskell.o
	${FC} -o $@ $^

sachd: sachd.o sacio.o
	${FC} -o $@ $^

trav: trav.o tau_p.o
	${FC} -o $@ trav.o tau_p.o

bessel.f: bessel.FF
	cpp -traditional-cpp $< > $@

clean:
	rm -f *.o bessel.f
