CC = gcc
CFLAGS = -O2 -Wall -Wextra
TARGET = syn_flood
SRC = syn_flood.c

all: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET)

clean:
	rm -f $(TARGET) *.o *.aux *.log *.out
	$(MAKE) -C simulator clean

report:
	python3 compile_report.py

test: $(TARGET)
	python3 run_live_experiments.py

web: $(TARGET)
	python3 simulator/app.py

cli: $(TARGET)
	python3 simulator/cli.py

.PHONY: all clean report test web cli
